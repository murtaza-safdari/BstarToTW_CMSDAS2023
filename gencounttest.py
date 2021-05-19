from TIMBER.Analyzer import analyzer
import sys

a = analyzer(sys.argv[1])

print (a.RunChain.genEventCount_)
# print (a.RunChain.genEventSumw_)
# print (a.RunChain.genEventSumw2_)