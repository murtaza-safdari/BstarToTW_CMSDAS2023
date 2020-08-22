# Goal:
# (1) Plot N-1 for tagging variables
# (2) Calculate HEM corrected mt vs mtw distribution
# (3) Save a ttree as a snapshot for isolating signal after successful top tag

from HAMMER.Analyzer import *
from HAMMER.Tools.Common import *
from optparse import OptionParser
import ROOT
import multiprocessing, time, glob

parser = OptionParser()

parser.add_option('-i', '--input', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-y', '--year', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'year',
                help      =   'Year')
parser.add_option('-c', '--config', metavar='FILE', type='string', action='store',
                default   =   'bstar_config.json',
                dest      =   'config',
                help      =   'Configuration file in json format with xsecs, cuts, etc that is interpreted as a python dictionary')
parser.add_option('--HEM',metavar='BOOL',action='store_true',
                default   =   False,
                dest      =   'HEM',
                help      =   'Use HEM corrected pt for testing')
parser.add_option('--EXCESSISO',metavar='BOOL',action='store_true',
                default   =   False,
                dest      =   'EXCESSISO',
                help      =   'Make plots to isolate excess')

(options, args) = parser.parse_args()

start_time = time.time()

cc = CommonCscripts()
CompileCpp(cc.deltaPhi)
CompileCpp(cc.vector)
CompileCpp(cc.invariantMass)
CompileCpp('bstar.cc')

#########
# Setup #
#########
def main(options):
    ROOT.ROOT.EnableImplicitMT(4)
    a = analyzer(options.input)

    setname = options.input.split('/')[-1].replace('.txt','').replace('.root','').replace('_loc','')
    print 'Setname: %s'%setname

    if options.HEM: hem_str = '_HEM'
    else: hem_str = ''

    config = openJSON(options.config)
    xsec, lumi = 1., 1.
    if setname in config['XSECS'].keys() and not a.isData: 
        xsec = config['XSECS'][setname]
        lumi = config['lumi']
        
    if "16" in options.year: year = "16"
    elif "17" in options.year: year = "17"
    elif "18" in options.year: year = "18"
    cuts = config['CUTS'][year]

    if not a.isData: norm = (xsec*lumi)/a.genEventCount
    else: norm = 1.

    flags = ["Flag_goodVertices",
               "Flag_globalTightHalo2016Filter", 
               "Flag_eeBadScFilter", 
               "Flag_HBHENoiseFilter", 
               "Flag_HBHENoiseIsoFilter", 
               "Flag_ecalBadCalibFilter", 
               "Flag_EcalDeadCellTriggerPrimitiveFilter"]
    flags = a.FilterColumnNames(flags)
    flag_string = '('
    for f in flags: flag_string += f +' && '
    flag_string = flag_string[:-4] + ') == 1'

    ##################################
    # Start an initial group of cuts #
    ##################################
    # Trigger
    if a.isData:
        if year == '16': trigs = ["HLT_PFHT800","HLT_PFHT900","HLT_PFJet450"]
        else: trigs = ["HLT_PFHT1050","HLT_PFJet500","HLT_AK8PFJet380_TrimMass30","HLT_AK8PFJet400_TrimMass30"]
        trigs = a.FilterColumnNames(trigs)
        trig_string = ''
        for t in trigs: trig_string += t + ' && '
        a.Cut('trigger',trig_string[:-4])
    # Filters and nJets
    a.Cut("filters",flag_string)
    a.Cut("nFatJets_cut","nFatJet > 1")
    # HEM re-ordering if needed
    if options.HEM: 
        a.Define('HEMstuff','HEMreweight(FatJet_phi,FatJet_eta,FatJet_pt)') # Returns a vector of the indices of jets after pt reweighting
        a.Define('myJet_pt','UnpackHEMpt(HEMstuff)')
        a.Define('HEM_index','UnpackHEMidx(HEMstuff)')
        a.Define("jetIdx","hemispherize(FatJet_phi, FatJet_jetId, HEM_index)")
    else:
        a.Define('myJet_pt','FatJet_pt')
        a.Define("jetIdx","hemispherize(FatJet_phi, FatJet_jetId)")

    a.Cut("hemispherize","(jetIdx[0] != -1)&&(jetIdx[1] != -1)")
    a.Cut("pt_cut","myJet_pt[jetIdx[0]] > 400 && myJet_pt[jetIdx[1]] > 400")
    a.Cut("eta_cut","abs(FatJet_eta[jetIdx[0]]) < 2.4 && abs(FatJet_eta[jetIdx[1]]) < 2.4")

    branches_to_save = [
        'nFatJet',
        'FatJet_pt',
        'myJet_pt',
        'FatJet_eta',
        'FatJet_phi',
        'FatJet_msoftdrop',
        'FatJet_tau.',
        'FatJet_subJetIdx.',
        'nSubJet',
        'SubJet_btagDeepB',
        '\bjetIdx'
    ]

    #################################
    # Build some variables for jets #
    #################################
    # Wtagging decision logic
    # Returns 0 for no tag, 1 for lead tag, 2 for sublead tag, and 3 for both tag (which is physics-wise equivalent to 2)
    wtag_str = "1*Wtag(FatJet_tau2[jetIdx[0]]/FatJet_tau1[jetIdx[0]],0,{0}, FatJet_msoftdrop[jetIdx[0]],65,105) + 2*Wtag(FatJet_tau2[jetIdx[1]]/FatJet_tau1[jetIdx[1]],0,{0}, FatJet_msoftdrop[jetIdx[1]],65,105)".format(cuts['tau21'])

    jets = VarGroup('jets')
    jets.Add('wtag_bit',    wtag_str)
    jets.Add('top_bit',     '(wtag_bit & 2)? 0: (wtag_bit & 1)? 1: -1') # (if wtag==3 or 2 (subleading w), top_index=0) else (if wtag==1, top_index=1) else (-1)
    jets.Add('top_index',   'top_bit >= 0 ? jetIdx[top_bit] : -1')
    jets.Add('w_index',     'top_index == 0 ? jetIdx[1] : top_index == 1 ? jetIdx[0] : -1')
    # Calculate some new comlumns that we'd like to cut on (that were costly to do before the other filtering)
    jets.Add("lead_vect",   "analyzer::TLvector(myJet_pt[jetIdx[0]],FatJet_eta[jetIdx[0]],FatJet_phi[jetIdx[0]],FatJet_msoftdrop[jetIdx[0]])")
    jets.Add("sublead_vect","analyzer::TLvector(myJet_pt[jetIdx[1]],FatJet_eta[jetIdx[1]],FatJet_phi[jetIdx[1]],FatJet_msoftdrop[jetIdx[1]])")
    jets.Add("deltaY",      "lead_vect.Rapidity()-sublead_vect.Rapidity()")
    jets.Add("mtw",         "analyzer::invariantMass(lead_vect,sublead_vect)")

    noJetTagging = a.Apply([jets])

    #########
    # N - 1 #
    #########
    plotting_vars = VarGroup('plotting_vars') # assume leading is top and subleading is W
    plotting_vars.Add("mtop",        "FatJet_msoftdrop[jetIdx[0]]")
    plotting_vars.Add("mW",          "FatJet_msoftdrop[jetIdx[1]]")
    plotting_vars.Add("tau32",       "FatJet_tau3[jetIdx[0]]/FatJet_tau2[jetIdx[0]]")
    plotting_vars.Add("subjet_btag", "max(SubJet_btagDeepB[FatJet_subJetIdx1[jetIdx[0]]],SubJet_btagDeepB[FatJet_subJetIdx2[jetIdx[0]]])")
    plotting_vars.Add("tau21",       "FatJet_tau2[jetIdx[1]]/FatJet_tau1[jetIdx[1]]")

    N_cuts = CutGroup('Ncuts') # cuts
    N_cuts.Add("deltaY_cut",      "abs(deltaY)<1.6")
    N_cuts.Add("mtop_cut",        "(mtop > 105.)&&(mtop < 220.)")
    N_cuts.Add("mW_cut",          "(mW > 65.)&&(mW < 105.)")
    N_cuts.Add("tau32_cut",       "(tau32 > 0.0)&&(tau32 < %s)"%(cuts['tau32']))
    N_cuts.Add("subjet_btag_cut", "(subjet_btag > %s)&&(subjet_btag < 1.)"%(cuts['sjbtag']))
    N_cuts.Add("tau21_cut",       "(tau21 > 0.0)&&(tau21 < %s)"%(cuts['tau21']))

    # Organize N-1 of tagging variables when assuming top is always leading
    nodeToPlot = a.Apply([plotting_vars])
    nminus1Nodes = a.Nminus1(nodeToPlot,N_cuts)
    nminus1Hists = HistGroup('nminus1Hists')
    binning = {
        'mtop': [25,50,300],
        'mW': [25,30,270],
        'tau32': [20,0,1],
        'tau21': [20,0,1],
        'subjet_btag': [20,0,1],
        'deltaY': [40,-2.0,2.0]
    }
    # Add hists to group and write out
    for nkey in nminus1Nodes.keys():
        if nkey == 'full': continue
        var = nkey.replace('_cut','').replace('minus_','')
        #hist = nminus1Nodes[nkey].DataFrame.Histo1D((var,var,binning[var][0],binning[var][1],binning[var][2]),var)
        #nminus1Hists.Add(var,hist)

    a.SetActiveNode(noJetTagging)

    # # Snapshot while we're here
    #branches_to_save.extend(plotting_vars.keys()+jets.keys())
    #noJetTagging.Snapshot(branches_to_save,'rootfiles/%s_%s_nojettag%s.root'%(setname,year,hem_str),'snapshot')

    ########################
    # Cut on new variables #
    ########################
    # Select real W and top
    tagging_vars = VarGroup('tagging_vars') 
    tagging_vars.Add("mtop",        "top_index > -1 ? FatJet_msoftdrop[top_index] : -10")
    tagging_vars.Add("mW",          "w_index   > -1 ? FatJet_msoftdrop[w_index]: -10")
    tagging_vars.Add("tau32",       "top_index > -1 ? FatJet_tau3[top_index]/FatJet_tau2[top_index]: -1")
    tagging_vars.Add("subjet_btag", "top_index > -1 ? max(SubJet_btagDeepB[FatJet_subJetIdx1[top_index]],SubJet_btagDeepB[FatJet_subJetIdx2[top_index]]) : -1")
    tagging_vars.Add("tau21",       "w_index   > -1 ? FatJet_tau2[w_index]/FatJet_tau1[w_index]: -1")
    toptag_str = "TopTag(tau32,0,{0}, subjet_btag,{1},1, mtop,50,1000)==1".format(cuts['tau32'],cuts['sjbtag'])
    tagging_vars.Add("wtag",'wtag_bit>0')
    tagging_vars.Add("top_tag",toptag_str)
 
    a.Apply([tagging_vars])
    branches_to_save.extend(tagging_vars.keys()+jets.keys())
    snapshot_node = a.GetActiveNode()
    #snapshot_node.Snapshot(branches_to_save,'rootfiles/%s_%s_presel%s.root'%(setname,year,hem_str),'snapshot',lazy=True if options.EXCESSISO else False)

    #f_out = ROOT.TFile.Open('rootfiles/%s_%s_presel%s.root'%(setname,year,hem_str),'UPDATE')
    #nminus1Hists.Do('Write')
    #f_out.Close()

    # Write cut on new column
    jet_sel = CutGroup('jet_sel')
    jet_sel.Add('wtag_cut','wtag')
    jet_sel.Add("mtw_cut","mtw>1000.")
    jet_sel.Add('deltaY_cut','abs(deltaY)<1.6')


    #########
    # Apply #
    #########
    a.Apply([jet_sel])

    # Finally discriminate on top tag
    final = a.Discriminate("top_tag_cut","top_tag==1")

    #CutflowTxt('txtfiles/%s_%s.txt'%(setname,year),final["pass"])

    # h = final["pass"].DataFrame.Histo2D(('MtwvMtPass','MtwvMtPass',60, 50, 350, 70, 500, 4000),'mtop','mtw')
    # h.Draw('lego')

    ####################
    # Signal isolation #
    ####################
    if options.EXCESSISO:
        a.SetActiveNode(final['pass'])
        a.Cut('signal_iso','mtop > 160. && mtop < 190. && mtw > 2000 && mtw < 3000')
        kin_binning = {
            'myJet_pt[top_index]':  ROOT.RDF.TH1DModel('pt_top','p_{T}_{top}',32,400,2000),
            'myJet_pt[w_index]':    ROOT.RDF.TH1DModel('pt_w','p_{T}_{W}',32,400,2000),
            'FatJet_eta[top_index]':ROOT.RDF.TH1DModel('eta_top','#eta_{top}',48,-2.4,2.4),
            'FatJet_eta[w_index]':  ROOT.RDF.TH1DModel('eta_w','#eta_{W}',48,-2.4,2.4),
            'FatJet_phi[top_index]':ROOT.RDF.TH1DModel('phi_top','#phi_{top}',50,-3.1415,3.1415),
            'FatJet_phi[w_index]':  ROOT.RDF.TH1DModel('phi_w','#phi_{W}',50,-3.1415,3.1415),
            'mtw': ROOT.RDF.TH1DModel('mtw','m_{tW}',50,2000,3000),
            'mtop': ROOT.RDF.TH1DModel('mtop','m_{t}',60,160,190),
            'mW': ROOT.RDF.TH1DModel('mW','m_{W}',25,30,270)
        }

        for k in kin_binning:
            if '[' in k:
                a.Define(kin_binning[k].fName,k)

        node = a.GetActiveNode()
        excessHists = HistGroup('excessHists')
        for k in kin_binning:
            binning = kin_binning[k]
            if '[' in k: var = binning.fName
            else: var = k
            hist = node.DataFrame.Histo1D(binning,var)
            excessHists.Add(var,hist)

        f_out = ROOT.TFile.Open('rootfiles/%s_%s%s.root'%(setname,year,hem_str),'UPDATE')
        excessHists.Do('Write')
        f_out.Close()

    # a.PrintNodeTree('test',verbose=False)
    
#########################
# Setup multiprocessing #
#########################
# ex. 4 processes (from multiprocessing) with 4 threads each (EnableImplicitMT) for 16 thread processor
inputs = args
if len(inputs) > 0:
    # Will use args as input for multiprocessing instead of options.input (for single process)
    print('Using multiprocessing')
    pool = multiprocessing.Pool(processes=min(4,len(inputs)))
    process_args = []
    for i in inputs:
        sub_options = copy.deepcopy(options)
        sub_options.input = i
        
        process_args.append(sub_options)

    pool.map(main,process_args)
    
else:
    main(options)

print "Total time: "+str((time.time()-start_time)/60.) + ' min'
