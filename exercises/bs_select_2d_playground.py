''' Selection script for b*->tW all-hadronic full run II analysis
    Data and MC files are stored at `eos_path` and correspond to
    NanoAOD that has been processed by NanoAOD-tools. The processing
    required that each event have two jets with pt > 350 GeV and 
    |eta| < 2.5 and ran the jetmetHelperRun2*, puWeightProducer,
    and PrefireCorr modules.

    *The jetmetHelperRun2 module used runs a custom version of fatJetUncertainties
    that can be found at
    https://github.com/lcorcodilos/nanoAOD-tools/blob/master/python/postprocessing/modules/jme/fatJetUncertainties.py
    The main difference between this and the central version
    is that this saves the individual corrections and NOT the 
    already corrected pt and mass. This gives more freedom
    to the end user and how the corrections are used (for example,
    the central version only has variables suitable for W jets and not top jets).
'''
# import sys

# TIMBER
from TIMBER.Analyzer import *
from TIMBER.Tools.Common import *
from TIMBER.Tools.Plot import *
import helpers
# Other
import argparse
import time, sys
sys.path.append('../TIMBER/')

import ROOT, collections,os
sys.path.append('./')
from collections import OrderedDict
# from TIMBER.Analyzer import analyzer, HistGroup
# from TIMBER.Tools.Common import CompileCpp
# from TIMBER.Tools.Plot import *
# import helpers
ROOT.gROOT.SetBatch(True)

###########################################
# Set some global variables for later use #
###########################################
# Deduce set name from input file
redirector = 'root://cmsxrootd.fnal.gov/'
rootfile_path = '/store/user/cmsdas/2021/long_exercises/BstarTW/rootfiles'
# setname = args.input.replace('.root','').split('/')[-1]
# setname = '_'.join(setname.split('_')[:-1])

plotdir = 'plots/' # this is where we'll save your plots
if not os.path.exists(plotdir):
    os.makedirs(plotdir)

# Flags - https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
flags = ["Flag_goodVertices",
        "Flag_globalSuperTightHalo2016Filter", 
        "Flag_HBHENoiseFilter", 
        "Flag_HBHENoiseIsoFilter",
        "Flag_EcalDeadCellTriggerPrimitiveFilter",
        "Flag_BadPFMuonFilter" 
        "Flag_ecalBadCalibReducedMINIAODFilter", 
    ]

# # Triggers
# if args.year == '16': 
#     triggers = ["HLT_PFHT800","HLT_PFHT900","HLT_PFJet450"]
# else: 
#     triggers = ["HLT_PFHT1050","HLT_PFJet500","HLT_AK8PFJet380_TrimMass30","HLT_AK8PFJet400_TrimMass30"]

# Compile some C++ modules for use
CompileCpp("TIMBER/Framework/include/common.h")
CompileCpp('bstar.cc') # custom .cc script

varnames2d = {
        'softdrop_lead_sublead_mass_v_mass':['lead_softdrop_mass',"sublead_softdrop_mass"],
        'leadjet_mass_v_score_W':['lead_softdrop_mass','lead_deepAK8_WvsQCD'],
        'leadjet_mass_v_score_T':['lead_softdrop_mass','lead_deepAK8_TvsQCD'],
        'leadjet_mass_v_score_W_MD':['lead_softdrop_mass','lead_deepAK8_WvsQCD_MD'],
        'leadjet_mass_v_score_T_MD':['lead_softdrop_mass','lead_deepAK8_TvsQCD_MD'],
        'subleadjet_mass_v_score_W':['sublead_softdrop_mass','sublead_deepAK8_WvsQCD'],
        'subleadjet_mass_v_score_T':['sublead_softdrop_mass','sublead_deepAK8_TvsQCD'],
        'subleadjet_mass_v_score_W_MD':['sublead_softdrop_mass','sublead_deepAK8_WvsQCD_MD'],
        'subleadjet_mass_v_score_T_MD':['sublead_softdrop_mass','sublead_deepAK8_TvsQCD_MD'],
        'leadjet_mass_v_t21':['lead_softdrop_mass','lead_tau21'],
        'leadjet_mass_v_t32':['lead_softdrop_mass','lead_tau32'],
        'subleadjet_mass_v_t21':['sublead_softdrop_mass','sublead_tau21'],
        'subleadjet_mass_v_t32':['sublead_softdrop_mass','sublead_tau32'],
    }

varnames1d = {
        'lead_tau32'         : '#tau_{32}^{jet0}',
        'sublead_tau32'      : '#tau_{32}^{jet1}',
        'lead_tau21'         : '#tau_{21}^{jet0}',
        'sublead_tau21'      : '#tau_{21}^{jet1}',
        'nbjet_loose'        : 'loosebjets',
        'nbjet_medium'       : 'mediumbjets',
        'nbjet_tight'        : 'tightbjets',
        'lead_jetPt'         : 'p_{T}^{jet0}',
        'sublead_jetPt'      : 'p_{T}^{jet1}',
        'deltaphi'       : '#Delta#phi_{jet0,jet1}',
        'lead_softdrop_mass'     : 'm_{SD}^{jet0}',
        'sublead_softdrop_mass'  : 'm_{SD}^{jet1}',
        'invariantMass': 'm_{SD}^{inv}',
        'lead_deepAK8_TvsQCD'    : 'Deep AK8 TvsQCD^{jet0}',
        'sublead_deepAK8_TvsQCD' : 'Deep AK8 TvsQCD^{jet1}',
        'lead_deepAK8_WvsQCD'    : 'Deep AK8 WvsQCD^{jet0}',
        'sublead_deepAK8_WvsQCD' : 'Deep AK8 WvsQCD^{jet1}',
}

###########################
# Run analyzer on file(s) #
###########################
def run(args):

    outputname = args.setname
    setname = args.setname
    year = args.year
    # Triggers
    if args.year == '16': 
        triggers = ["HLT_PFHT800","HLT_PFHT900","HLT_PFJet450"]
    else: 
        triggers = ["HLT_PFHT1050","HLT_PFJet500","HLT_AK8PFJet380_TrimMass30","HLT_AK8PFJet400_TrimMass30"]

    ROOT.ROOT.EnableImplicitMT(4)
    # a = analyzer(args.input)
    file_path = '{redirector}{rootfile_path}/{setname}_bstar{year}.root'.format(
    redirector=redirector, rootfile_path=rootfile_path, setname=setname, year=year
    )
    a = analyzer(file_path)

    # Config loading - will have cuts, xsec, and lumi
    config = OpenJSON(args.config)
    cuts = config['CUTS'][args.year]

    # Determine normalization weight
    if not a.isData: 
        norm = helpers.getNormFactor(setname,args.year,args.config)
    else: 
        norm = 1.

    # Initial cuts
    a.Cut('filters',a.GetFlagString(flags))
    a.Cut('trigger',a.GetTriggerString(triggers))
    a.Define('jetIdx','hemispherize(FatJet_phi, FatJet_jetId)') # need to calculate if we have two jets (with Id) that are back-to-back
    a.Cut('nFatJets_cut','nFatJet > max(jetIdx[0], jetIdx[1])') # If we don't do this, we may try to access variables of jets that don't exist! (leads to seg fault)
    a.Cut("hemis","(jetIdx[0] != -1)&&(jetIdx[1] != -1)") # cut on that calculation

    # Kinematics
    a.Cut("pt_cut","FatJet_pt[jetIdx[0]] > 400 && FatJet_pt[jetIdx[1]] > 400")
    a.Cut("eta_cut","abs(FatJet_eta[jetIdx[0]]) < 2.4 && abs(FatJet_eta[jetIdx[1]]) < 2.4")

    #---#
    a.SubCollection('Dijet', 'FatJet', 'jetIdx', useTake=True)
    # We can now cut on the values of the Dijet collection and simply index 0 (lead) or 1 (sublead) to get the information about the appropriate jet
    a.Cut('pt_cut',   'Dijet_pt[0] > 400 && Dijet_pt[1] > 400')
    a.Cut('eta_cut',  'abs(Dijet_eta[0]) < 2.4 && abs(Dijet_eta[1]) < 2.4')
    a.Cut('mjet_cut', 'Dijet_msoftdrop[0] > 50 && Dijet_msoftdrop[1] > 50')
    a.Define('lead_vector',    'hardware::TLvector(Dijet_pt[0], Dijet_eta[0], Dijet_phi[0], Dijet_msoftdrop[0])')
    a.Define('sublead_vector', 'hardware::TLvector(Dijet_pt[1], Dijet_eta[1], Dijet_phi[1], Dijet_msoftdrop[1])')
    a.Define('invariantMass','hardware::InvariantMass({lead_vector,sublead_vector})')
    a.Cut('mtw_cut','invariantMass > 1200')

    # Now, we can define the variables we're interested in plotting (see varnames dictionary in global definitions above)
    a.Define('deltaphi','hardware::DeltaPhi(Dijet_phi[0], Dijet_phi[1])')
    a.Define('lead_tau32',    'Dijet_tau2[0] > 0 ? Dijet_tau3[0]/Dijet_tau2[0] : -1') # Conditional to make sure tau2 != 0 for division
    a.Define('sublead_tau32', 'Dijet_tau2[1] > 0 ? Dijet_tau3[1]/Dijet_tau2[1] : -1') # condition ? <do if true> : <do if false>
    a.Define('lead_tau21',    'Dijet_tau1[0] > 0 ? Dijet_tau2[0]/Dijet_tau1[0] : -1') # Conditional to make sure tau2 != 0 for division
    a.Define('sublead_tau21', 'Dijet_tau1[1] > 0 ? Dijet_tau2[1]/Dijet_tau1[1] : -1') # condition ? <do if true> : <do if false>
    a.Define('lead_deepAK8_TvsQCD',    'Dijet_deepTag_TvsQCD[0]')
    a.Define('sublead_deepAK8_TvsQCD', 'Dijet_deepTag_TvsQCD[1]')
    a.Define('lead_deepAK8_WvsQCD',    'Dijet_deepTag_WvsQCD[0]')
    a.Define('sublead_deepAK8_WvsQCD', 'Dijet_deepTag_WvsQCD[1]')

    a.Define('lead_deepAK8_TvsQCD_MD',    'Dijet_deepTagMD_TvsQCD[0]')
    a.Define('sublead_deepAK8_TvsQCD_MD', 'Dijet_deepTagMD_TvsQCD[1]')
    a.Define('lead_deepAK8_WvsQCD_MD',    'Dijet_deepTagMD_WvsQCD[0]')
    a.Define('sublead_deepAK8_WvsQCD_MD', 'Dijet_deepTagMD_WvsQCD[1]')

    bcut = []
    if args.year == '16' :
        bcut = [0.2217,0.6321,0.8953]
    elif args.year == '17' :
        bcut = [0.1522,0.4941,0.8001]
    elif args.year == '18' :
        bcut = [0.1241,0.4184,0.7571]
    a.Define('nbjet_loose',  'Sum(Jet_btagDeepB > '+str(bcut[0])+')') # DeepCSV loose WP
    a.Define('nbjet_medium', 'Sum(Jet_btagDeepB > '+str(bcut[1])+')') # DeepCSV medium WP
    a.Define('nbjet_tight',  'Sum(Jet_btagDeepB > '+str(bcut[2])+')') # DeepCSV tight WP
    a.Define('lead_jetPt',   'Dijet_pt[0]')
    a.Define('sublead_jetPt','Dijet_pt[1]')
    a.Define('lead_softdrop_mass',   'Dijet_msoftdrop[0]')
    a.Define('sublead_softdrop_mass','Dijet_msoftdrop[1]')


    #---#

    #################################
    # Build some variables for jets #
    #################################
    # # Wtagging decision logic
    # # This statement returns 0 for no tag, 1 for lead tag, 2 for sublead tag, and 3 for both tag (which is equivalent to 2 for the sake of deciding what is the W)
    # wtag_str = "1*Wtag(FatJet_tau2[jetIdx[0]]/FatJet_tau1[jetIdx[0]],0,{0}, FatJet_msoftdrop[jetIdx[0]],65,105) + 2*Wtag(FatJet_tau2[jetIdx[1]]/FatJet_tau1[jetIdx[1]],0,{0}, FatJet_msoftdrop[jetIdx[1]],65,105)".format(cuts['tau21'])
    # if args.deep:
    #     wtag_str = "1*WtagDeepAK8(FatJet_deepTagMD_WvsQCD[jetIdx[0]],{0},1, FatJet_msoftdrop[jetIdx[0]],65,105) + 2*WtagDeepAK8(FatJet_deepTagMD_WvsQCD[jetIdx[1]],{0},1, FatJet_msoftdrop[jetIdx[1]],65,105)".format(cuts['deepAK8w'])

    # jets = VarGroup('jets')
    # jets.Add('wtag_bit',    wtag_str)
    # jets.Add('top_bit',     '(wtag_bit & 2)? 0: (wtag_bit & 1)? 1: -1') # (if wtag==3 or 2 (subleading w), top_index=0) else (if wtag==1, top_index=1) else (-1)
    # jets.Add('top_index',   'top_bit >= 0 ? jetIdx[top_bit] : -1')
    # jets.Add('w_index',     'top_index == 0 ? jetIdx[1] : top_index == 1 ? jetIdx[0] : -1')
    # # Calculate some new comlumns that we'd like to cut on (that were costly to do before the other filtering)
    # jets.Add("lead_vect",   "hardware::TLvector(FatJet_pt[jetIdx[0]],FatJet_eta[jetIdx[0]],FatJet_phi[jetIdx[0]],FatJet_msoftdrop[jetIdx[0]])")
    # jets.Add("sublead_vect","hardware::TLvector(FatJet_pt[jetIdx[1]],FatJet_eta[jetIdx[1]],FatJet_phi[jetIdx[1]],FatJet_msoftdrop[jetIdx[1]])")
    # jets.Add("deltaY",      "lead_vect.Rapidity()-sublead_vect.Rapidity()")
    # jets.Add("mtw",         "hardware::InvariantMass({lead_vect,sublead_vect})")

    # # W and top
    # tagging_vars = VarGroup('tagging_vars') 
    # tagging_vars.Add("mtop",        "top_index > -1 ? FatJet_msoftdrop[top_index] : -10")
    # tagging_vars.Add("mW",          "w_index   > -1 ? FatJet_msoftdrop[w_index]: -10")
    # tagging_vars.Add("tau32",       "top_index > -1 ? FatJet_tau3[top_index]/FatJet_tau2[top_index]: -1")
    # tagging_vars.Add("subjet_btag", "top_index > -1 ? max(SubJet_btagDeepB[FatJet_subJetIdx1[top_index]],SubJet_btagDeepB[FatJet_subJetIdx2[top_index]]) : -1")
    # tagging_vars.Add("tau21",       "w_index   > -1 ? FatJet_tau2[w_index]/FatJet_tau1[w_index]: -1")
    # tagging_vars.Add("deepAK8_MD_TvsQCD", "top_index > -1 ? FatJet_deepTagMD_TvsQCD[top_index] : -1")
    # tagging_vars.Add("deepAK8_MD_WvsQCD", "w_index > -1 ? FatJet_deepTagMD_WvsQCD[w_index] : -1")

    # toptag_str = "TopTag(tau32,0,{0}, subjet_btag,{1},1, mtop,50,1000)==1".format(cuts['tau32'],cuts['sjbtag'])
    # if args.deep:
    #     toptag_str = "TopTagDeepAK8(deepAK8_MD_TvsQCD,{0},1, mtop,50,1000)==1".format(cuts['deepAK8top']) 
    # tagging_vars.Add("wtag",'wtag_bit>0')
    # tagging_vars.Add("top_tag",toptag_str)
 
    # # Write cut on new column
    # jet_sel = CutGroup('jet_sel')
    # jet_sel.Add('wtag_cut','wtag')
    # jet_sel.Add("mtw_cut","mtw>1000.")
    # jet_sel.Add('deltaY_cut','abs(deltaY)<1.6')

    #########
    # Apply #
    #########
    # a.Apply([jets,tagging_vars,jet_sel])
    a.Define('norm',str(norm))

    # Finally discriminate on top tag
    # final = a.Discriminate("top_tag_cut","top_tag==1")

    # outfile = ROOT.TFile.Open('Presel_%s.root'%(outputname),'RECREATE')
    # outfile = ROOT.TFile.Open('2dplayground_%s.root'%(outputname),'RECREATE')
    outFile = ROOT.TFile.Open('rootfiles/{}_{}_2dplayground.root'.format(setname, year),'RECREATE')
    # hpass = final["pass"].DataFrame.Histo2D(('MtwvMtPass','MtwvMtPass',60, 50, 350, 70, 500, 4000),'mtop','mtw','norm')
    # hfail = final["fail"].DataFrame.Histo2D(('MtwvMtFail','MtwvMtFail',60, 50, 350, 70, 500, 4000),'mtop','mtw','norm')
    # hmtwmw = a.GetActiveNode().DataFrame.Histo2D(('LeadMassVSsLeadMass','LeadMassVSsLeadMass',30, 0, 300, 30, 0, 300),'lead_softdrop_mass','sublead_softdrop_mass','norm')

    # hmtwmw.GetValue()
    # plot_filename = plotdir+'/2dplayground_{}.png'.format("invariantMass")
    # EasyPlots(
    #     name = plot_filename, 
    #     histlist = [hmtwmw],
    #     xtitle = "lead_softdrop_mass",
    #     ytitle = 'sublead_softdrop_mass',
    #     datastyle = 'hist'
    # )

    # Now we are ready to save histograms (in a HistGroup)
    out = HistGroup("%s_%s"%(setname,year))
    for varname in varnames1d.keys():
        print('\t{}'.format(varname))
        histname = '%s_%s_%s'%(setname,year,varname)
        # Arguments for binning that you would normally pass to a TH1 (histname, histname, number of bins, min bin, max bin)
        if "nbjet" in varname :
            hist_tuple = (histname,histname, 10,0,10)
        elif "tau" in varname :
            hist_tuple = (histname,histname,20,0,1)
        elif "Pt" in varname :
            hist_tuple = (histname,histname,30,400,1000)
        elif "phi" in varname :
            hist_tuple = (histname,histname,30,-3.2,3.2)
        elif "softdrop_mass" in varname :
            hist_tuple = (histname,histname,30,0,300)
        elif "invariantMass" in varname :
            hist_tuple = (histname,histname,400,0,4000)
        else:
            hist_tuple = (histname,histname,20,0,1)
        hist = a.GetActiveNode().DataFrame.Histo1D(hist_tuple,varname,'norm') # Project dataframe into a histogram (hist name/binning tuple, variable to plot from dataframe, weight)
        hist.GetValue() # This gets the actual TH1 instead of a pointer to the TH1
        out.Add(varname,hist) # Add it to our group
    for varname,varval in varnames2d.items():
        print('\t{}'.format(varname))
        histname = '%s_%s_%s'%(setname,year,varname)
        # Arguments for binning that you would normally pass to a TH1 (histname, histname, number of bins, min bin, max bin)
        if "mass_v_score" in varname :
            hist_tuple = (histname,histname, 30, 0, 300, 20, 0, 1)
        elif "mass_v_t" in varname :
            hist_tuple = (histname,histname, 30, 0, 300, 20, 0, 1)
        elif "mass_v_mass" in varname :
            hist_tuple = (histname,histname,30, 0, 300, 30, 0, 300)
        else:
            hist_tuple = (histname,histname,30, 0, 300, 30, 0, 300)
        name1 = varval[0]
        name2 = varval[1]
        # print(hist_tuple, name1,name2,'norm')
        # print("1","2","3","4")
        hist = a.GetActiveNode().DataFrame.Histo2D(hist_tuple, name1,name2,'norm') # Project dataframe into a histogram (hist name/binning tuple, variable to plot from dataframe, weight)
        hist.GetValue() # This gets the actual TH1 instead of a pointer to the TH1
        out.Add(varname,hist) # Add it to our group

    outFile.cd()
    out.Do('Write') # This will call TH1.Write() for all of the histograms in the group
    outFile.Close()
    del out # Now that they are saved out, drop from memory

    # outfile.cd()
    # hmtwmw.Write()
    # outfile.Close()

if __name__ == "__main__":
    start_time = time.time()

    parser = argparse.ArgumentParser()

    # parser.add_argument('-i', '--input',  type=str, action='store', default='', dest='input', help='A root file or text file with multiple root file locations to analyze') 
    parser.add_argument('-s', type=str, dest='setname',
                            action='store', required=True,
                            help='Setname to process. E.g. ttbar, signalLH2000, singletop_tW, QCDHT700, etc...') 
    parser.add_argument('-y', '--year',   type=str, action='store', default='', dest='year', help='Year')
    parser.add_argument('-c', '--config', type=str, action='store', default='bstar_config.json', dest='config', help='Configuration file in json format with xsecs, cuts, etc that is interpreted as a python dictionary') 
    parser.add_argument('--deep', default=False, action='store_true',help='DeepAK8 selection')
    args = parser.parse_args()

    run(args)

    print ("Total time: "+str((time.time()-start_time)/60.) + ' min')
