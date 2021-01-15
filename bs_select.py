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
import sys

# TIMBER
from TIMBER.Analyzer import *
from TIMBER.Tools.Common import *
# Other
import argparse
import time, sys
sys.path.append('../TIMBER/')

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input', type=str, action='store', default='', dest='input', help='A root file or text file with multiple root file locations to analyze') 
parser.add_argument('-y', '--year',  type=str, action='store', default='', dest='year', help='Year')
parser.add_argument('-c', '--config', type=str, action='store', default='bstar_config.json', dest='config', help='Configuration file in json format with xsecs, cuts, etc that is interpreted as a python dictionary') 
parser.add_argument('--deep', default=False, action='store_true',help='DeepAK8 selection')
args = parser.parse_args()

###########################################
# Set some global variables for later use #
###########################################
# Deduce set name from input file
setname = args.input.replace('.root','').split('/')[-1]

# Flags - https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
flags = ["Flag_goodVertices",
        "Flag_globalSuperTightHalo2016Filter", 
        "Flag_HBHENoiseFilter", 
        "Flag_HBHENoiseIsoFilter",
        "Flag_EcalDeadCellTriggerPrimitiveFilter",
        "Flag_BadPFMuonFilter" 
        "Flag_ecalBadCalibReducedMINIAODFilter", 
    ]

# Triggers
if args.year == '16': 
    triggers = ["HLT_PFHT800","HLT_PFHT900","HLT_PFJet450"]
else: 
    triggers = ["HLT_PFHT1050","HLT_PFJet500","HLT_AK8PFJet380_TrimMass30","HLT_AK8PFJet400_TrimMass30"]

# Compile some C++ modules for use
CompileCpp("TIMBER/Framework/include/common.h")
CompileCpp('bstar.cc') # custom .cc script

###########################
# Run analyzer on file(s) #
###########################
def run(args):
    ROOT.ROOT.EnableImplicitMT(4)
    a = analyzer(args.input)

    # Config loading - will have cuts, xsec, and lumi
    config = OpenJSON(args.config)
    cuts = config['CUTS'][args.year]
    xsec, lumi = 1., 1.
    if setname in config['XSECS'].keys() and not a.isData: 
        xsec = config['XSECS'][setname]
        lumi = config['lumi']

    # Determine normalization weight
    if not a.isData: 
        norm = (xsec*lumi)/config['NEVENTS'][args.year]['_'.join(setname.split('_')[:-1])]
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

    #################################
    # Build some variables for jets #
    #################################
    # Wtagging decision logic
    # This statement returns 0 for no tag, 1 for lead tag, 2 for sublead tag, and 3 for both tag (which is equivalent to 2 for the sake of deciding what is the W)
    wtag_str = "1*Wtag(FatJet_tau2[jetIdx[0]]/FatJet_tau1[jetIdx[0]],0,{0}, FatJet_msoftdrop[jetIdx[0]],65,105) + 2*Wtag(FatJet_tau2[jetIdx[1]]/FatJet_tau1[jetIdx[1]],0,{0}, FatJet_msoftdrop[jetIdx[1]],65,105)".format(cuts['tau21'])
    if args.deep:
        wtag_str = "1*WtagDeepAK8(FatJet_deepTagMD_WvsQCD[jetIdx[0]],{0},1, FatJet_msoftdrop[jetIdx[0]],65,105) + 2*WtagDeepAK8(FatJet_deepTagMD_WvsQCD[jetIdx[1]],{0},1, FatJet_msoftdrop[jetIdx[1]],65,105)".format(cuts['deepAK8w'])

    jets = VarGroup('jets')
    jets.Add('wtag_bit',    wtag_str)
    jets.Add('top_bit',     '(wtag_bit & 2)? 0: (wtag_bit & 1)? 1: -1') # (if wtag==3 or 2 (subleading w), top_index=0) else (if wtag==1, top_index=1) else (-1)
    jets.Add('top_index',   'top_bit >= 0 ? jetIdx[top_bit] : -1')
    jets.Add('w_index',     'top_index == 0 ? jetIdx[1] : top_index == 1 ? jetIdx[0] : -1')
    # Calculate some new comlumns that we'd like to cut on (that were costly to do before the other filtering)
    jets.Add("lead_vect",   "hardware::TLvector(FatJet_pt[jetIdx[0]],FatJet_eta[jetIdx[0]],FatJet_phi[jetIdx[0]],FatJet_msoftdrop[jetIdx[0]])")
    jets.Add("sublead_vect","hardware::TLvector(FatJet_pt[jetIdx[1]],FatJet_eta[jetIdx[1]],FatJet_phi[jetIdx[1]],FatJet_msoftdrop[jetIdx[1]])")
    jets.Add("deltaY",      "lead_vect.Rapidity()-sublead_vect.Rapidity()")
    jets.Add("mtw",         "hardware::invariantMass({lead_vect,sublead_vect})")

    # W and top
    tagging_vars = VarGroup('tagging_vars') 
    tagging_vars.Add("mtop",        "top_index > -1 ? FatJet_msoftdrop[top_index] : -10")
    tagging_vars.Add("mW",          "w_index   > -1 ? FatJet_msoftdrop[w_index]: -10")
    tagging_vars.Add("tau32",       "top_index > -1 ? FatJet_tau3[top_index]/FatJet_tau2[top_index]: -1")
    tagging_vars.Add("subjet_btag", "top_index > -1 ? max(SubJet_btagDeepB[FatJet_subJetIdx1[top_index]],SubJet_btagDeepB[FatJet_subJetIdx2[top_index]]) : -1")
    tagging_vars.Add("tau21",       "w_index   > -1 ? FatJet_tau2[w_index]/FatJet_tau1[w_index]: -1")
    tagging_vars.Add("deepAK8_MD_TvsQCD", "top_index > -1 ? FatJet_deepTagMD_TvsQCD[top_index] : -1")
    tagging_vars.Add("deepAK8_MD_WvsQCD", "w_index > -1 ? FatJet_deepTagMD_WvsQCD[w_index] : -1")

    toptag_str = "TopTag(tau32,0,{0}, subjet_btag,{1},1, mtop,50,1000)==1".format(cuts['tau32'],cuts['sjbtag'])
    if args.deep:
        toptag_str = "TopTagDeepAK8(deepAK8_MD_TvsQCD,{0},1, mtop,50,1000)==1".format(cuts['deepAK8top']) 
    tagging_vars.Add("wtag",'wtag_bit>0')
    tagging_vars.Add("top_tag",toptag_str)
 
    # Write cut on new column
    jet_sel = CutGroup('jet_sel')
    jet_sel.Add('wtag_cut','wtag')
    jet_sel.Add("mtw_cut","mtw>1000.")
    jet_sel.Add('deltaY_cut','abs(deltaY)<1.6')

    #########
    # Apply #
    #########
    a.Apply([jets,tagging_vars,jet_sel])
    a.Define('norm',str(norm))

    # Finally discriminate on top tag
    final = a.Discriminate("top_tag_cut","top_tag==1")

    outfile = ROOT.TFile.Open('Presel_%s.root'%(setname),'RECREATE')
    hpass = final["pass"].DataFrame.Histo2D(('MtwvMtPass','MtwvMtPass',60, 50, 350, 70, 500, 4000),'mtop','mtw','norm')
    hfail = final["fail"].DataFrame.Histo2D(('MtwvMtFail','MtwvMtFail',60, 50, 350, 70, 500, 4000),'mtop','mtw','norm')
    outfile.cd()
    hpass.Write()
    hfail.Write()
    outfile.Close()

if __name__ == "__main__":
    start_time = time.time()
    run(args)

    print ("Total time: "+str((time.time()-start_time)/60.) + ' min')
