'''Example to cover exercise 4 of CMSDAS2020 B2G long exercise.
   Apply simple kinematic selection and plot substructure variables
   for signal and background MC and compare.
'''
import ROOT, collections,sys,os
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
cernbox = '/eos/home-%s/%s/Documents/plots'%(os.environ['USER'][0],os.environ['USER']) # this is where we'll save your plots (accessible via web on cernbox.cern.ch)
if not os.path.exists(cernbox):
    os.makedirs(cernbox)
rootfile_path = '/eos/user/c/cmsdas/long-exercises/bstarToTW/rootfiles/'
config = 'bstar_config.json' # holds luminosities and cross sections
CompileCpp('bstar.cc') # has the c++ functions we need when looping of the RDataFrame

# Sets we want to process and some nice naming for our plots
signal_names = ['signalLH%s'%(mass) for mass in [2000]]#range(1400,4200,600)]
bkg_names = ['singletop_tW','singletop_tWB','ttbar','QCDHT700','QCDHT1000','QCDHT1500','QCDHT2000']
names = {
    "singletop_tW":"single top (tW)",
    "singletop_tWB":"single top (tW)",
    "ttbar":"t#bar{t}",
    "QCDHT700":"QCD",
    "QCDHT1000":"QCD",
    "QCDHT1500":"QCD",
    "QCDHT2000":"QCD",
    "QCD":"QCD",
    "singletop":"single top (tW)"
}
for sig in signal_names:
    names[sig] = "b*_{LH} %s (GeV)"%(sig[-4:])
# ... and some nice colors
colors = {}
for p in signal_names+bkg_names:
    if 'signal' in p:
        colors[p] = ROOT.kCyan-int((int(p[-4:])-1400)/600)
    elif 'ttbar' in p:
        colors[p] = ROOT.kRed
    elif 'singletop' in p:
        colors[p] = ROOT.kBlue
    elif 'QCD' in p:
        colors[p] = ROOT.kYellow
colors["QCD"] = ROOT.kYellow
colors["singletop"] = ROOT.kBlue

# Flags - https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
flags = ["Flag_goodVertices",
        "Flag_globalSuperTightHalo2016Filter", 
        "Flag_HBHENoiseFilter", 
        "Flag_HBHENoiseIsoFilter",
        "Flag_EcalDeadCellTriggerPrimitiveFilter",
        "Flag_BadPFMuonFilter",
        "Flag_ecalBadCalibReducedMINIAODFilter"
    ]
# Triggers
if options.year == '16': 
    triggers = ["HLT_PFHT800","HLT_PFHT900","HLT_PFJet450"]
else: 
    triggers = ["HLT_PFHT1050","HLT_PFJet500","HLT_AK8PFJet380_TrimMass30","HLT_AK8PFJet400_TrimMass30"]

# Variables we want to plot (need to be constructed as variables in the RDataFrame)
varnames = {
        'lead_tau32':'#tau_{32}^{jet0}',
        'sublead_tau32':'#tau_{32}^{jet1}',
        'lead_tau21':'#tau_{21}^{jet0}',
        'sublead_tau21':'#tau_{21}^{jet1}'
    }


#########################################
# Define function for actual processing #
#########################################
def select(setname,year):
    ROOT.ROOT.EnableImplicitMT(2) # Just use two threads - no need to kill the interactive nodes

    # Initialize TIMBER analyzer
    file_path = '%s/%s_bstar%s.root' %(rootfile_path,setname, year)
    a = analyzer(file_path)

    # Determine normalization weight
    if not a.isData: 
        norm = helpers.getNormFactor(setname,year,config,a.genEventCount)
    else: 
        norm = 1.

    # Book actions on the RDataFrame
    a.Cut('filters',a.GetFlagString(flags))
    a.Cut('trigger',a.GetTriggerString(triggers))
    a.Define('jetIdx','hemispherize(FatJet_phi, FatJet_jetId)') # need to calculate if we have two jets (with Id) that are back-to-back
    a.Cut('nFatJets_cut','nFatJet > max(jetIdx[0],jetIdx[1])') # If we don't do this, we may try to access variables of jets that don't exist! (leads to seg fault)
    a.Cut("hemis","(jetIdx[0] != -1)&&(jetIdx[1] != -1)") # cut on that calculation
    a.Cut('pt_cut','FatJet_pt[jetIdx[0]] > 400 && FatJet_pt[jetIdx[1]] > 400')
    a.Cut('eta_cut','abs(FatJet_eta[jetIdx[0]]) < 2.4 && abs(FatJet_eta[jetIdx[1]]) < 2.4')
    a.Cut('mjet_cut','FatJet_msoftdrop[jetIdx[0]] > 50 && FatJet_msoftdrop[jetIdx[1]] > 50')
    a.Cut('mtw_cut','analyzer::invariantMass(jetIdx[0],jetIdx[1],FatJet_pt,FatJet_eta,FatJet_phi,FatJet_msoftdrop) > 1200')
    a.Define('lead_tau32','FatJet_tau2[jetIdx[0]] > 0 ? FatJet_tau3[jetIdx[0]]/FatJet_tau2[jetIdx[0]] : -1') # Conditional to make sure tau2 != 0 for division
    a.Define('sublead_tau32','FatJet_tau2[jetIdx[1]] > 0 ? FatJet_tau3[jetIdx[1]]/FatJet_tau2[jetIdx[1]] : -1') # condition ? <do if true> : <do if false>
    a.Define('lead_tau21','FatJet_tau1[jetIdx[0]] > 0 ? FatJet_tau2[jetIdx[0]]/FatJet_tau1[jetIdx[0]] : -1') # Conditional to make sure tau2 != 0 for division
    a.Define('sublead_tau21','FatJet_tau1[jetIdx[1]] > 0 ? FatJet_tau2[jetIdx[1]]/FatJet_tau1[jetIdx[1]] : -1') # condition ? <do if true> : <do if false>
    a.Define('norm',str(norm))

    # Book a group to save the histograms
    out = HistGroup("%s_%s"%(setname,year))
    for varname in varnames.keys():
        histname = '%s_%s_%s'%(setname,year,varname)
        hist_tuple = (histname,histname,20,0,1) # Arguments for binning that you would normally pass to a TH1
        hist = a.GetActiveNode().DataFrame.Histo1D(hist_tuple,varname,'norm') # Project dataframe into a histogram (hist name/binning tuple, variable to plot from dataframe, weight)
        hist.GetValue() # This gets the actual TH1 instead of a pointer to the TH1
        out.Add(varname,hist) # Add it to our group

    # Return the group
    return out

# Runs when calling `python ex4.py`
if __name__ == "__main__":
    histgroups = {} # all of the HistGroups we want to track
    for setname in signal_names+bkg_names:
        print ('Selecting for %s...'%setname)
    
        # Perform selection and write out histograms if using --select
        if options.select:
            histgroup = select(setname,options.year)
            outfile = ROOT.TFile.Open("rootfiles/%s_%s.root"%(setname,options.year),'RECREATE')
            outfile.cd()
            histgroup.Do('Write') # This will call TH1.Write() for all of the histograms in the group
            outfile.Close()
            del histgroup # Now that they are saved out, drop from memory
            
        # Open histogram files that we saved
        infile = ROOT.TFile.Open("rootfiles/%s_%s.root"%(setname,options.year))
        # ... raise exception if we forgot to run with --select!
        if infile == None:
            raise TypeError("rootfiles/%s_%s.root does not exist"%(setname,options.year))
        # Put histograms back into HistGroups
        histgroups[setname] = HistGroup(setname)
        for key in infile.GetListOfKeys(): # loop over histograms in the file
            keyname = key.GetName()
            if setname not in keyname: continue # skip if it's not for the current set we are on
            varname = keyname[len(setname+'_'+options.year)+1:] # get the variable name (ex. lead_tau32)
            inhist = infile.Get(key.GetName()) # get it from the file
            inhist.SetDirectory(0) # set the directory so hist is stored in memory and not as reference to TFile (this way it doesn't get tossed by python garbage collection when infile changes)
            histgroups[setname].Add(varname,inhist) # add to our group
            
    # For each variable to plot...
    for varname in varnames.keys():
        plot_filename = cernbox+'/%s_%s.png'%(varname,options.year)

        # Setup ordered dictionaries so processes plot in the order we specify
        bkg_hists,signal_hists = OrderedDict(),OrderedDict()
        # Get the backgrounds
        for bkg in bkg_names: 
            histgroups[bkg][varname].SetTitle('%s 20%s'%(varname, options.year)) # empty title
            if 'QCD' in bkg: # Add the QCD HT bins together for one QCD sample
                if 'QCD' not in bkg_hists.keys():
                    bkg_hists['QCD'] = histgroups[bkg][varname].Clone('QCD_'+varname)
                else:
                    bkg_hists['QCD'].Add(histgroups[bkg][varname])
            elif 'singletop' in bkg: # Add the single top channels together for one single top sample
                if 'singletop' not in bkg_hists.keys():
                    bkg_hists['singletop'] = histgroups[bkg][varname].Clone('singletop_'+varname)
                else:
                    bkg_hists['singletop'].Add(histgroups[bkg][varname])
            else: # add everything else normally (ttbar)
                bkg_hists[bkg] = histgroups[bkg][varname]#all_hists[bkg] = histgroups[bkg][varname]#
                
        # Add the signals
        for sig in signal_names: signal_hists[sig] = histgroups[sig][varname]#all_hists[sig] = histgroups[sig][varname]#

        # Plot everything together!
        CompareShapes(plot_filename,options.year,varnames[varname],bkgs=bkg_hists,signals=signal_hists,colors=colors,names=names)
