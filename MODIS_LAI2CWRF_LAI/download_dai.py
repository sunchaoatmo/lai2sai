#!/usr/bin/env python
import requests
hvs=set(['h11v06', 'h11v07', 'h11v04', 'h11v05', 'h11v03', 'h07v05', 'h07v04', 'h07v07', 'h07v06', 'h13v03', 'h13v04', 'h13v05', 'h14v03', 'h10v03', 'h10v05', 'h10v04', 'h10v07', 'h10v06', 'h09v03', 'h09v07', 'h09v06', 'h09v05', 'h09v04', 'h08v04', 'h08v05', 'h08v06', 'h08v07', 'h12v03', 'h14v04', 'h12v06', 'h12v05', 'h12v04', 'h06v06', 'h06v07'])
#hvs=set(['h06v06'])
yearsurfixs=["","_2010-2013","_2014","_2015","_2016"]
urlbase="http://globalchange.bnu.edu.cn/download/data/lai/"

for hv in hvs:
  for year in yearsurfixs:
    fname="MOD15A2.%s%s.tar"%(hv,year)
    url="%s/%s"%(urlbase,fname)

    r = requests.get(url, allow_redirects=True)
    open(fname, 'wb').write(r.content)
    print(url)
