'''Example to cover exercise 4 of CMSDAS2020 B2G long exercise.
   Apply simple kinematic selection and plot substructure variables
   for signal and background MC and compare.
'''
import ROOT, collections,sys
sys.path.append('./')
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Analyzer import analyzer, HistGroup
from TIMBER.Tools.Common import CompileCpp
from TIMBER.Tools.Plot import *
import helpers

# CL options
parser = OptionParser()
parser.add_option('-y', '--year', metavar='YEAR', type='string', action='store',
                default   =   '',
                dest      =   'year',
                help      =   'Year (16,17,18)')
parser.add_option('--select', metavar='BOOL', action='store_true',
                default   =   False,
                dest      =   'select',
                help      =   'Whether to run the selection. If False, will attempt to recycle previous run histograms.')
(options, args) = parser.parse_args()

###########################################
# Establish some global variables for use #
###########################################
rootfile_path = '/eos/user/c/cmsdas/long-exercises/bstarToTW/rootfiles/'
config = 'bstar_config.json'
CompileCpp('bstar.cc')

signal_names = ['signalLH%s'%(mass) for mass in range(1400,4200,400)]
bkg_names = ['singletop_tW','singletop_tWB','ttbar','QCDHT700','QCDHT1000','QCDHT1500','QCDHT2000']
names = {
    "singletop_tW":"single top (tW)",
    "singletop_tWB":"single top (tW)",
    "ttbar":"t#bar{t}",
    "QCDHT700":"QCD",
    "QCDHT1000":"QCD",
    "QCDHT1500":"QCD",
    "QCDHT2000":"QCD"
}
for sig in signal_names:
    names[sig] = "b*_{LH} %s (GeV)"%(sig[-4:])

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
if options.year == '16': 
    triggers = ["HLT_PFHT800","HLT_PFHT900","HLT_PFJet450"]
else: 
    triggers = ["HLT_PFHT1050","HLT_PFJet500","HLT_AK8PFJet380_TrimMass30","HLT_AK8PFJet400_TrimMass30"]

varnames = {
        'lead_tau32':'#tau_{32}^{jet0}',
        'sublead_tau32':'#tau_{32}^{jet1}',
        'lead_tau21':'#tau_{21}^{jet0}',
        'sublead_tau21':'#tau_{21}^{jet1}'
    }

colors = {}
for p in signal_names+bkg_names:
    if 'signal' in p:
        colors[p] = ROOT.kCyan-int((int(p[-4:])-1400)/400)
    elif 'ttbar' in p:
        colors[p] = ROOT.kRed
    elif 'singletop' in p:
        colors[p] = ROOT.kBlue
    elif 'QCD' in p:
        colors[p] = ROOT.kYellow

#########################################
# Define function for actual processing #
#########################################
def select(setname,year):
    ROOT.ROOT.EnableImplicitMT(2)

    file_path = '%s/%s_bstar%s.root' %(rootfile_path,setname, year)
    a = analyzer(file_path)

    # Determine normalization weight
    if not a.isData: 
        norm = helpers.getNormFactor(setname,year,config,a.genEventCount)
    else: 
        norm = 1.

    a.Cut('filters',a.GetFlagString(flags))
    a.Cut('trigger',a.GetTriggerString(triggers))
    a.Cut('nFatJets_cut','nFatJet > 1') # If we don't do this, we may try to access variables of jets that don't exist! (leads to seg fault)
    a.Define('jetIdx','hemispherize(FatJet_phi, FatJet_jetId)') # need to calculate if we have two jets (with Id) that are back-to-back
    a.Cut("hemis","(jetIdx[0] != -1)&&(jetIdx[1] != -1)") # cut on that calculation
    a.Cut('pt_cut','FatJet_pt[jetIdx[0]] > 400 && FatJet_pt[jetIdx[1]] > 400')
    a.Cut('eta_cut','abs(FatJet_eta[jetIdx[0]]) < 2.4 && abs(FatJet_eta[jetIdx[1]]) < 2.4')
    a.Define('lead_tau32','FatJet_tau2[jetIdx[0]] > 0 ? FatJet_tau3[jetIdx[0]]/FatJet_tau2[jetIdx[0]] : -1') # Conditional to make sure tau2 != 0 for division
    a.Define('sublead_tau32','FatJet_tau2[jetIdx[1]] > 0 ? FatJet_tau3[jetIdx[1]]/FatJet_tau2[jetIdx[1]] : -1') # condition ? <do if true> : <do if false>
    a.Define('lead_tau21','FatJet_tau1[jetIdx[0]] > 0 ? FatJet_tau2[jetIdx[0]]/FatJet_tau1[jetIdx[0]] : -1') # Conditional to make sure tau2 != 0 for division
    a.Define('sublead_tau21','FatJet_tau1[jetIdx[1]] > 0 ? FatJet_tau2[jetIdx[1]]/FatJet_tau1[jetIdx[1]] : -1') # condition ? <do if true> : <do if false>
    a.Define('norm',str(norm))

    out = HistGroup("%s_%s"%(setname,year))
    for varname in varnames.keys():
        histname = '%s_%s_%s'%(setname,year,varname)
        hist_tuple = (histname,histname,20,0,1)
        hist = a.GetActiveNode().DataFrame.Histo1D(hist_tuple,varname,'norm')
        hist.GetValue()
        out.Add(varname,hist)

    return out

# Runs when calling `python ex4.py`
if __name__ == "__main__":
    histgroups = {}
    QCDs = {}
    for setname in signal_names+bkg_names:
        print ('Selecting for %s...'%setname)
    
        # Write out histograms
        if options.select:
            histgroups[setname] = select(setname,options.year)
            outfile = ROOT.TFile.Open("rootfiles/%s_%s.root"%(setname,options.year),'RECREATE')
            outfile.cd()
            histgroups[setname].Do('Write')
            outfile.Close()
            del histgroups
            
        # Open histogram files for plotting
        infile = ROOT.TFile.Open("rootfiles/%s_%s.root"%(setname,options.year))
        if infile == None:
            raise TypeError("rootfiles/%s_%s.root does not exist"%(setname,options.year))
        histgroups[setname] = HistGroup(setname)
        for key in infile.GetListOfKeys():
            keyname = key.GetName()
            if setname not in keyname: continue
            varname = '_'.join(keyname.split('_')[-2:])
            inhist = infile.Get(key.GetName())
            inhist.SetDirectory(0)
            histgroups[setname].Add(varname,inhist)
            
    for varname in varnames.keys():
        plot_filename = 'plots/%s_%s.png'%(varname,options.year)

        bkg_hists,signal_hists = OrderedDict(),OrderedDict()
        for bkg in bkg_names: bkg_hists[bkg] = histgroups[bkg][varname]
        for sig in signal_names: signal_hists[sig] = histgroups[sig][varname]

        CompareShapes(plot_filename,options.year,varnames[varname],bkg_hists,signal_hists,colors=colors,names=names)
    
