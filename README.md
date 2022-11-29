# BstarToTW_CMSDAS2021

## Getting started (in bash shell)

### Setup CMSSW environment:
```
ssh -XY USERNAME@cmslpc-sl7.fnal.gov
export $SCRAM_ARCH=slc7_amd64_gcc820 
cd ~/nobackup/
mkdir CMSDAS2023
cd CMSDAS2023/
cmsrel CMSSW_11_1_4
cd CMSSW_11_1_4/src
cmsenv
```

### In the `CMSSW_11_1_4/src/` directory, clone this exercise repo:
```
git clone https://github.com/ammitra/BstarToTW_CMSDAS2023.git
```
OR fork the code onto your personal project space and set the upstream:
```
git clone https://github.com/<GitHubUsername>/BstarToTW_CMSDAS2023.git
cd BstarToTW_CMSDAS2023
git remote add upstream https://github.com/ammitra/BstarToTW_CMSDAS2023.git
git remote -v
```

### In the `CMSSW_11_1_4/src/` directory, create a python virtual environment and install TIMBER within it:
```
git clone https://github.com/ammitra/TIMBER.git
python -m virtualenv timber-env
source timber-env/bin/activate
cd TIMBER
source setup.sh
cd ..
```

You can test that the TIMBER installation is working by running the following in your shell:
```
python -c 'import TIMBER.Analyzer'
```
If all went well, the command should be executed with no output.

### At this point you should have a directory structure that looks like this: 
```
└── ~/nobackup/CMSDAS2023/CMSSW_11_1_4/src/
    ├── TIMBER/
    ├── timber-env/
    └── BstarToTW_CMSDAS2023/
```

## Starting up once environment is set:

Once you have an environment:
```
cd CMSSW_11_1_4/src/
cmsenv
source timber-env/bin/activate
```
You will need to perform this step *every* time you log on to the LPC cluster.

## If you need to update TIMBER
```
cd TIMBER/
git fetch --all
git checkout master
python setup.py develop
cd ../
```

## If you need to update BstarToTW_CMSDAS2023
```
cd BstarToTW_CMSDAS2023
git fetch --all
git pull origin master
cd ../
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
