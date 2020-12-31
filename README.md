# BstarToTW_CMSDAS2020

## Getting started (in bash shell)

Setup CMSSW environment:
```
ssh -XY USERNAME@cmslpc-sl7.fnal.gov
source /cvmfs/cms.cern.ch/cmsset_default.sh 
export $SCRAM_ARCH=slc7_amd64_gcc820 
cd nobackup/
mkdir b2g_exercise/
cd b2g_exercise/
cmsrel CMSSW_11_0_1
cd CMSSW_11_0_1/src
cmsenv
```

Clone repo:
```
git clone https://github.com/cmantill/BstarToTW_CMSDAS2020
```

Create TIMBER environement and setup cmsenv (for first time):
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
cd BstarToTW_CMSDAS2020/
```

## Exercise 1: Object and event selection


`python exercises/selection -y 16 --select`

## Exercise 2: Define analysis signal region

## Exercise 3: Define control regions

## Exercise 4: Background estimate

## Exercise 5: Systematics 

## Exercise 6: Limit setting

## Exercise 7: Extra - optimization