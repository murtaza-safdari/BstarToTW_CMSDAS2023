'''
   Apply simple kinematic selection and plot substructure variables
   for signal and background MC and compare.
'''
import ROOT, collections,sys,os
sys.path.append('./')
sys.path.append('exercises/')
from optparse import OptionParser
from collections import OrderedDict

from TIMBER.Analyzer import analyzer, HistGroup
from TIMBER.Tools.Common import CompileCpp
from TIMBER.Tools.Plot import *
import helpers
from selection import select,bstarPayload

ROOT.gROOT.SetBatch(True) 

# CL options
parser = OptionParser()
parser.add_option('-y', '--year', metavar='YEAR', type='string', action='store',
                default   =   '',
                dest      =   'year',
                help      =   'Year (16,17,18)')
parser.add_option('-s', metavar='NAME', type='string', action='store', 
                default   =   '',
                dest      =   'setname',
                help      =   'Set name')
(options, args) = parser.parse_args()

###########################################
# Establish some global variables for use #
###########################################
bs_payload = bstarPayload(options)

CompileCpp("TIMBER/Framework/include/common.h") 
CompileCpp('bstar.cc') # has the c++ functions we need when looping of the RDataFrame

# Runs when calling `python selection.py`
if __name__ == "__main__":
    histgroup = select(options.setname,options.year)
    outfile = ROOT.TFile.Open("rootfiles/%s_%s.root"%(options.setname,options.year),'RECREATE')
    outfile.cd()
    histgroup.Do('Write') # This will call TH1.Write() for all of the histograms in the group
    outfile.Close()
    del histgroup # Now that they are saved out, drop from memory
            
     