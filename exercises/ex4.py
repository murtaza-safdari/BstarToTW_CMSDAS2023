'''Example to cover exercise 4 of CMSDAS2020 B2G long exercise.
   Apply simple kinematic selection and plot substructure variables
   for signal and background MC and compare.
'''

from optparse import OptionParser

from TIMBER.Analyzer import analyzer

# CL options
parser = OptionParser()
parser.add_option('-y', '--year', metavar='YEAR', type='string', action='store',
                default   =   '',
                dest      =   'year',
                help      =   'Year (16,17,18)')
(options, args) = parser.parse_args()

###########################################
# Establish some global variables for use #
###########################################
rootfile_path = '/eos/user/c/cmsdas/long-exercises/bstarToTW/rootfiles/'
signal_names = ['signalLH%s'(hand,mass) for mass in range(1400,4200,400)]
bkg_names = ['ttbar','QCDHT700','QCDHT1000','QCDHT1500','QCDHT2000']
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

#########################################
# Define function for actual processing #
#########################################
def select(setname,year):
    ROOT.EnablineImplicitMT(1)

    file_path = rootfile_path + '/%s_bstar%s.root' %(setname, options.year)
    a = analyzer(file_path)

    # Determine normalization weight
    if not a.isData: 
        norm = getNormFactor(options.config,a.genEventCount)
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
    a.Define('norm',norm)

    out = HistGroup()
    for varname in varnames.keys():
        histname = '%s_%s_%s'%(setname,options.year,varname)
        hist_tuple = (histname,histname,20,0,1)
        out.Add(varname,a.GetActiveNode().DataFrame.Histo2D(hist_tuple,varname,'norm'))

    return out

# Runs when calling `python ex4.py`
if __name__ == "__main__":
    histgroups = {}
    QCDs = {}
    for setname in signal_names+bkg_names:
        print ('Selecting for %s...'%setname)
    
        if 'QCD' in setname:
            QCDs[setname] = select(file_path)
        else:
            histgroups[setname] = select(file_path)

    histgroups['QCD'] = StitchQCD(QCDs)

    for varname in varnames.keys():
        plot_filename = 'plots/%s_%s.png'%(varname,options.year)
        bkg_hists = [histgroups[bkg][varname] for bkg in bkg_names]+[histgroups['QCD'][varname]]
        signal_hists = [histgroups[sig][varname] for sig in signal_names]

        CompareShapes(plot_filename,varnames[varname],bkg_hists,signal_hists)
    
