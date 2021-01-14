# BstarToTW_CMSDAS2021

## Getting started (in bash shell)

### Setup CMSSW environment:
```
ssh -XY USERNAME@cmslpc-sl7.fnal.gov
export $SCRAM_ARCH=slc7_amd64_gcc820 
cd nobackup/
mkdir b2g_exercise/
cd b2g_exercise/
cmsrel CMSSW_11_0_1
cd CMSSW_11_0_1/src
cmsenv
```

### In the `src` directory, clone repo:
```
git clone https://github.com/cmantill/BstarToTW_CMSDAS2021.git
```
OR fork the code onto your personal project space and set the upstream:
```
git clone https://github.com/<GitHubUsername>/BstarToTW_CMSDAS2021.git
cd BstarToTW_CMSDAS2021
git remote add upstream https://github.com/cmantill/BstarToTW_CMSDAS2021.git
git remote -v
```

### In the `src` directory, create environment
```
git clone https://github.com/lcorcodilos/TIMBER.git
python -m virtualenv timber-env
source timber-env/bin/activate
cd TIMBER
source setup.sh
cd ..
python -c 'import TIMBER.Analyzer'
```

## Starting up once environment is set:

Once you have an environment:
```
cd CMSSW_11_0_1/src/
cmsenv
source timber-env/bin/activate
cd TIMBER/
git fetch --all
git checkout master
python setup.py install
cd ../BstarToTW_CMSDAS2020
git fetch --all
git pull origin master
```

## Submitting jobs

Modify username and output directory in `condor/run_bstar.sh` e.g.:
```
root://cmseos.fnal.gov//store/user/$USER/bstar_select_tau21/
```

also create the directory:
```
eosmkdir /store/user/$USER/bstar_select_tau21
```

Test it works on one file:
```
python CondorHelper.py -r condor/run_bstar.sh -a test_args.txt -i "bs_select.py bstar.cc bstar_config.json helpers.py"
```

For 2016 (then change args file for other years):
```
python CondorHelper.py -r condor/run_bstar.sh -a 2016_args.txt  -i "bs_select.py bstar.cc bstar_config.json helpers.py"
```

Check jobs:
```
condor_q $USER
```
