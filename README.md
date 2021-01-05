# BstarToTW_CMSDAS2021

## Getting started (in bash shell)

### Setup CMSSW environment:
```
ssh -XY USERNAME@cmslpc-sl7.fnal.gov
source /cvmfs/cms.cern.ch/cmsset_default.sh 
export $SCRAM_ARCH=slc7_amd64_gcc820 
cd nobackup/
mkdir b2g_exercise/
cd b2g_exercise/
cmsrel CMSSW_11_0_1
cd CMSSW_11_0_1/src
```

### Clone repo:
```
git clone https://github.com/cmantill/BstarToTW_CMSDAS2021
```
OR fork the code onto your personal project space and set the upstream:
```
git clone https://github.com/<GitHubUsername>/BstarToTW_CMSDAS2021
cd BstarToTW_CMSDAS2021
git remote add upstream https://github.com/cmantill/BstarToTW_CMSDAS2021
git remote -v
```

### Create environment
```
python -m virtualenv timber-env
source timber-env/bin/activate
git clone https://github.com/lcorcodilos/TIMBER.git
cd TIMBER
source setup.sh
cd ..
cmsenv
```

## Starting up once environment is set:

Once you have an environment:
```
cd ~/nobackup/b2g_exercise/CMSSW_11_0_1/src/
source timber-env/bin/activate
cd BstarToTW_CMSDAS2021/
source /cvmfs/cms.cern.ch/cmsset_default.sh 
cmsenv
```