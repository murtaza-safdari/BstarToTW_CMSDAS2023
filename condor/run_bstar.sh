#!/bin/bash
echo "Run script starting"
ls
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/cmsdas/2021/long_exercises/BstarTW/CMSSW_11_0_1_cmsdas.tgz ./
export SCRAM_ARCH=slc7_amd64_gcc820
scramv1 project CMSSW CMSSW_11_0_1
tar -xzf CMSSW_11_0_1_cmsdas.tgz
rm CMSSW_11_0_1_cmsdas.tgz
cd CMSSW_11_0_1/src/
eval `scramv1 runtime -sh`
ls -lrth

#source timber-env/bin/activate
#python -c 'import TIMBER.Analyzer'
rm -rf timber-env

#mkdir new; cd new;
#xrdcp root://cmseos.fnal.gov//store/user/cmsdas/2021/long_exercises/BstarTW/timber-env.tgz ./
xrdcp root://cmseos.fnal.gov//store/user/cmsdas/2021/long_exercises/BstarTW/timber-env.tar.gz ./
tar -xzf timber-env.tar.gz 
source timber-env/bin/activate
python -c 'import TIMBER.Analyzer'
cd ../../../

mkdir tardir; cp tarball.tgz tardir/; cd tardir/
tar -xzf tarball.tgz; rm tarball.tgz

ls 
python -c 'import TIMBER.Analyzer'

echo python bs_select.py $*
python bs_select.py $*

#xrdcp Presel_*.root root://cmseos.fnal.gov//store/user/cmantill/bstar_select_tau21/
