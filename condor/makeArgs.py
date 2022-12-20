from glob import glob
import subprocess, os
from TIMBER.Tools.Common import ExecuteCmd

redirector = 'root://cmseos.fnal.gov/'
eos_path = '/store/user/cmsdas/2023/long_exercises/BstarTW/rootfiles'
eosls = 'eos root://cmseos.fnal.gov ls'

files = subprocess.check_output('eos root://cmseos.fnal.gov ls %s'%(eos_path), shell=True)

f16 = open('condor/2016_args.txt','w')
f17 = open('condor/2017_args.txt','w')
f18 = open('condor/2018_args.txt','w')

for f in files.split('\n'):
    if (f == '') or ('prime' in f) or ('scale' in f) or ('ext' in f) or ('jets' in f) or ('DS' in f): continue
    if 'bstar16' in f:
	f16.write('-s {}{}/{} -y 16\n'.format(redirector,eos_path,f))
    elif 'bstar17' in f:
	f17.write('-s {}{}/{} -y 17\n'.format(redirector,eos_path,f))
    else:
	f18.write('-s {}{}/{} -y 18\n'.format(redirector,eos_path,f))
