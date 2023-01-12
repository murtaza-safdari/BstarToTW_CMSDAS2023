#!/bin/bash
echo "Run script starting"
ls
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/musafdar/CMSDAS2023/BstarTW.tgz ./
scramv1 project CMSSW CMSSW_11_1_4
export SCRAM_ARCH=slc7_amd64_gcc820
tar -xzvf BstarTW.tgz
rm BstarTW.tgz
rm *.root

mkdir tardir; cp tarball.tgz tardir/; cd tardir/
tar -xzf tarball.tgz; rm tarball.tgz
cp -r * ../CMSSW_11_1_4/src/BstarToTW_CMSDAS2023/; cd ../CMSSW_11_1_4/src/
echo 'IN RELEASE'
pwd
ls
eval `scramv1 runtime -sh`
rm -rf timber-env
python -m virtualenv timber-env
source timber-env/bin/activate
cd TIMBER
source setup.sh
cd ../BstarToTW_CMSDAS2023
rm rootfiles/*.root

echo python exercises/bs_select.py $*
python exercises/bs_select.py $*

xrdcp -f rootfiles/*.root root://cmseos.fnal.gov//store/user/musafdar/CMSDAS2023/selectfiles/
