import glob

for y in ['16','17','18']:
  out = open('args%s.txt'%y,'w')
  for f in open('all_rootfiles.txt','r').readlines():
    if 'bstar'+y in f:
      out.write('-y %s -i root://cmseos.fnal.gov//store/user/lcorcodi/bstar_nano/rootfiles/%s'%(y,f))
  out.close()
    
