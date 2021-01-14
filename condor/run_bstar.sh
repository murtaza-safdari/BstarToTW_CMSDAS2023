#!/bin/bash
echo "Run script starting"
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/lcorcodi/CMSDAS2021env.tgz ./
export SCRAM_ARCH=slc7_amd64_gcc820
tar -xzf CMSDAS2021env.tgz
rm CMSDAS2021env.tgz

mkdir tardir; cp tarball.tgz tardir/; cd tardir/
tar -xzf tarball.tgz; rm tarball.tgz
cp -r * ../CMSSW_11_0_1/src/BstarToTW_CMSDAS2021; cd ../CMSSW_11_0_1/src/
eval `scramv1 runtime -sh`
source timber-env/bin/activate

cd BstarToTW_CMSDAS2021

echo python bs_select.py $*
python bs_select.py $*

cp Presel_*.root ../../