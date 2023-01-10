# BstarToTW_CMSDAS2023

## Getting started (in bash shell)

### Setup CMSSW environment:
```
ssh -XY USERNAME@cmslpc-sl7.fnal.gov
export SCRAM_ARCH=slc7_amd64_gcc820 
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

## Submitting Condor jobs

Create the appropriate output directory in your EOS space:
```
eosmkdir /store/user/$USER/CMSDAS2023/rootfiles/
```

You can now run either your selection or N-1 script:

*Selection:*
```
python CondorHelper.py -r condor/run_selection.sh -a condor/2016_args.txt -i "bstar.cc bstar_config.json helpers.py"
```

*N - 1:*
```
python CondorHelper.py -r condor/run_Nminus1.sh -a condor/2016_args.txt -i "bstar.cc bstar_config.json helpers.py"
```

The argument files for the various years are:
```
condor/2016_args.txt
condor/2017_args.txt
condor/2018_args.txt
```

To check the progress/submission status of your jobs:
```
condor_q $USER
```
