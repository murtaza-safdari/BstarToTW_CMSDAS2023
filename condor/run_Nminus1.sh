#!/bin/bash
echo "Run script starting"
ls
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/cmsdas/2023/long_exercises/BstarTW/BstarTW.tgz ./
export SCRAM_ARCH=slc7_amd64_gcc820
tar -xzvf BstarTW.tgz
rm BstarTW.tgz
rm *.root

mkdir tardir; cp tarball.tgz tardir/; cd tardir/
tar -xzf tarball.tgz; rm tarball.tgz
cp -r * ../CMSSW_11_1_4/src/BstarToTW_CMSDAS2023/; cd ../CMSSW_11_1_4/src/
eval `scramv1 runtime -sh`
rm -rf timber-env
python -m virtualenv timber-env
source timber-env/bin/activate
cd TIMBER
source setup.sh
cd ../BstarToTW_CMSDAS2023
rm rootfiles/*.root

echo python exercises/nminus1.py $*
python exercises/nminus1.py $*

xrdcp -f rootfiles/*.root root://cmseos.fnal.gov//store/user/$USER/CMSDAS2023/rootfiles/
