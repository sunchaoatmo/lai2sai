#!/usr/bin/env python 
import subprocess
hvs=set(['h11v06', 'h11v07', 'h11v04', 'h11v05', 'h11v03', 'h07v05', 'h07v04', 'h07v07', 'h07v06', 'h13v03', 'h13v04', 'h13v05', 'h14v03', 'h10v03', 'h10v05', 'h10v04', 'h10v07', 'h10v06', 'h09v03', 'h09v07', 'h09v06', 'h09v05', 'h09v04', 'h08v04', 'h08v05', 'h08v06', 'h08v07', 'h12v03', 'h14v04', 'h12v06', 'h12v05', 'h12v04', 'h06v06', 'h06v07'])
yb=2000
ye=2014
for year in range(yb,ye+1):
  for day in range(1,365,8):
    for hv in hvs:
      url="http://files.ntsg.umt.edu/data/NTSG_Products/MOD16/MOD16A2.105_MERRAGMAO/Y%04d/D%03d"%(year,day)
      fname="MOD16A2.A%04d%03d.%s."%(year,day,hv)
      cmd="wget -nH -r -l1 --no-parent -A '%s*.hdf' -R *.html,*.htm %s"%(fname,url)
      print(cmd)
      subprocess.call(cmd,shell=True)

