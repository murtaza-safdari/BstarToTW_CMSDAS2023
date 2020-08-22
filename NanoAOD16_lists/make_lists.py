# 2017 version which uses central NanoAOD rather than JHitos
import pickle
import subprocess
import glob

# Just grabbing the basic centrally produced nanoAOD so this will be different from the 2016 version
input_subs = {
    "ttbar":"/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v2/NANOAODSIM",
    "QCDHT700":"/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT700ext":"/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "QCDHT2000":"/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT2000ext":"/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "QCDHT1500":"/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT1500ext":"/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "QCDHT1000":"/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT1000ext":"/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "dataB":"/JetHT/Run2016B_ver1-Nano25Oct2019_ver1-v1/NANOAOD",
    "dataB2":"/JetHT/Run2016B_ver2-Nano25Oct2019_ver2-v1/NANOAOD",
    "dataC":"/JetHT/Run2016C-Nano25Oct2019-v1/NANOAOD",
    "dataD":"/JetHT/Run2016D-Nano25Oct2019-v1/NANOAOD",
    "dataE":"/JetHT/Run2016E-Nano25Oct2019-v1/NANOAOD",
    "dataF":"/JetHT/Run2016F-Nano25Oct2019-v1/NANOAOD",
    "dataG":"/JetHT/Run2016G-Nano25Oct2019-v1/NANOAOD",
    "dataH":"/JetHT/Run2016H-Nano25Oct2019-v1/NANOAOD",
    "WjetsHT600":"/WJetsToQQ_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "singletop_tW":"/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "singletop_tWB":"/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "singletop_tW-scaleup":"/ST_tW_top_5f_scaleup_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "singletop_tW-scaledown":"/ST_tW_top_5f_scaledown_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "singletop_tWB-scaleup":"/ST_tW_antitop_5f_scaleup_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "singletop_tWB-scaledown":"/ST_tW_antitop_5f_scaledown_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "singletop_t":"/ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "singletop_tB":"/ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "singletop_s":"/ST_s-channel_4f_InclusiveDecays_13TeV-amcatnlo-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH1200":"/BstarToTW_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH1400":"/BstarToTW_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH1600":"/BstarToTW_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH1800":"/BstarToTW_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH2000":"/BstarToTW_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH2200":"/BstarToTW_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH2400":"/BstarToTW_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH2600":"/BstarToTW_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH2800":"/BstarToTW_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH3000":"/BstarToTW_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH3200":"/BstarToTW_M-3200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH3400":"/BstarToTW_M-3400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH3600":"/BstarToTW_M-3600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH3800":"/BstarToTW_M-3800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalLH4000":"/BstarToTW_M-4000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    
    "signalRH1200":"/BstarToTW_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH1400":"/BstarToTW_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH1600":"/BstarToTW_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH1800":"/BstarToTW_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH2000":"/BstarToTW_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH2200":"/BstarToTW_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH2400":"/BstarToTW_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH2600":"/BstarToTW_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH2800":"/BstarToTW_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH3000":"/BstarToTW_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH3200":"/BstarToTW_M-3200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH3400":"/BstarToTW_M-3400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH3600":"/BstarToTW_M-3600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH3800":"/BstarToTW_M-3800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "signalRH4000":"/BstarToTW_M-4000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",

    "BprimeLH1200":"/BprimeTToTW_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeLH1300":"/BprimeTToTW_M-1300_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeLH1400":"/BprimeTToTW_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeLH1500":"/BprimeTToTW_M-1500_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeLH1600":"/BprimeTToTW_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeLH1700":"/BprimeTToTW_M-1700_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeLH1800":"/BprimeTToTW_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeRH1200":"/BprimeTToTW_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeRH1300":"/BprimeTToTW_M-1300_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeRH1400":"/BprimeTToTW_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeRH1500":"/BprimeTToTW_M-1500_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeRH1600":"/BprimeTToTW_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeRH1700":"/BprimeTToTW_M-1700_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "BprimeRH1800":"/BprimeTToTW_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",

    "TprimeLH1200":"/TprimeBToTZ_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeLH1300":"/TprimeBToTZ_M-1300_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeLH1400":"/TprimeBToTZ_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeLH1500":"/TprimeBToTZ_M-1500_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeLH1600":"/TprimeBToTZ_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeLH1700":"/TprimeBToTZ_M-1700_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeLH1800":"/TprimeBToTZ_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeRH1200":"/TprimeBToTZ_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeRH1300":"/TprimeBToTZ_M-1300_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeRH1400":"/TprimeBToTZ_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeRH1500":"/TprimeBToTZ_M-1500_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeRH1600":"/TprimeBToTZ_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeRH1700":"/TprimeBToTZ_M-1700_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "TprimeRH1800":"/TprimeBToTZ_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv6-PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM"
}
executables = []

# Remove files first
print 'rm *_loc.txt'
subprocess.call(['rm *_loc.txt'],shell=True)

f_release = open('release.txt','w')
f_release.close()
for i in input_subs.keys():
    if '/store/user/' in input_subs[i]:
        files = glob.glob('/eos/uscms'+input_subs[i])
        out = open(i+'_loc.txt','w')
        for f in files:
            out.write(f.replace('/eos/uscms','root://cmsxrootd.fnal.gov/')+'\n')
        out.close()
    else:
        executables.append('dasgoclient -query "file dataset='+input_subs[i]+'" > '+i+'_loc.txt')
        executables.append('echo '+input_subs[i]+' >> release.txt')
        executables.append('dasgoclient -query "release dataset='+input_subs[i]+'" >> release.txt')
for s in executables:
    print s
    subprocess.call([s],shell=True)


