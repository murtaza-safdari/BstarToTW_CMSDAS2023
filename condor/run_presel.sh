#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/lcorcodi/11X_CMSDAS.tgz ./
export SCRAM_ARCH=slc7_amd64_gcc820
eval `scramv1 project CMSSW CMSSW_11_0_1`
tar xzf 11X_CMSDAS.tgz
rm 11X_CMSDAS.tgz

mkdir tardir; mv tarball.tgz tardir/; cd tardir
tar xzvf tarball.tgz
cp -r * ../CMSSW_11_0_1/src/BstarToTW_CMSDAS2020/
cd ../CMSSW_11_0_1/src/
eval `scramv1 runtime -sh`
rm -rf timber-env
python -m virtualenv timber-env
source timber-env/bin/activate

cd TIMBER/
source setup.sh
cd ../BstarToTW_CMSDAS2020/

echo bs_select.py $*
python bs_select.py $* #-s $1 -r $2 -d $3 -n $4 -j $5
cp *.root ../../../

