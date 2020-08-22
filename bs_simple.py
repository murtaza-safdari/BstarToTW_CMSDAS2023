from HAMMER.Analyzer import *
from HAMMER.Tools.Common import *
from optparse import OptionParser
import ROOT
import time, glob

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
    a.Define("jetIdx","hemispherize(FatJet_phi, FatJet_jetId)")

    a.Cut("hemispherize","(jetIdx[0] != -1)&&(jetIdx[1] != -1)")
    a.Cut("pt_cut","FatJet_pt[jetIdx[0]] > 400 && FatJet_pt[jetIdx[1]] > 400")
    a.Cut("eta_cut","abs(FatJet_eta[jetIdx[0]]) < 2.4 && abs(FatJet_eta[jetIdx[1]]) < 2.4")

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
    jets.Add("lead_vect",   "analyzer::TLvector(FatJet_pt[jetIdx[0]],FatJet_eta[jetIdx[0]],FatJet_phi[jetIdx[0]],FatJet_msoftdrop[jetIdx[0]])")
    jets.Add("sublead_vect","analyzer::TLvector(FatJet_pt[jetIdx[1]],FatJet_eta[jetIdx[1]],FatJet_phi[jetIdx[1]],FatJet_msoftdrop[jetIdx[1]])")
    jets.Add("deltaY",      "lead_vect.Rapidity()-sublead_vect.Rapidity()")
    jets.Add("mtw",         "analyzer::invariantMass(lead_vect,sublead_vect)")

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

    outfile = TFile.Open('rootfiles/%s_%s.root'%(setname,year),'RECREATE')
    hpass = final["pass"].DataFrame.Histo2D(('MtwvMtPass','MtwvMtPass',60, 50, 350, 70, 500, 4000),'mtop','mtw')
    hfail = final["fail"].DataFrame.Histo2D(('MtwvMtFail','MtwvMtFail',60, 50, 350, 70, 500, 4000),'mtop','mtw')
    outfile.cd()
    hpass.Write()
    hfail.Write()
    outfile.Close()

# No multiprocessing
main(options)

print "Total time: "+str((time.time()-start_time)/60.) + ' min'
