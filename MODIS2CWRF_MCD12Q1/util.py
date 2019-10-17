#!/usr/bin/env python
def Taskditributor(ntask,nprocs,rank):
  import numpy as np
  procs=np.zeros(nprocs,dtype=np.int)
  iprocs=0
  if rank<ntask:
    for iday in range(ntask):
      procs[iprocs]=procs[iprocs]+1
      if iprocs<nprocs-1:
        iprocs=iprocs+1
      else:
        iprocs=0
    task_beg=np.cumsum(procs)-procs[0]

    return procs[rank],task_beg[rank]
  else:
    return 0,-1

def findid(lat0,lon0):
  import subprocess as sub
  cmd="tile_id -proj=SIN -lon=%s -lat=%s"%(lon0,lat0)
  p = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE, shell=True)
  output, errors = p.communicate()
  output=output.decode("utf-8") 
  for line in output.splitlines():#qstat[5:]:
    if "Tile ID" in line:
      _,hv=line.split(":")
      h,v=hv.split()
      return "h%02dv%02d"%(int(h),int(v))

def getlatlon(fname):
  from netCDF4 import Dataset
  import numpy as np
  fh=Dataset(fname)
  lat=fh.variables["CLAT"]
  lon=fh.variables["CLONG"]
  lat=np.array(lat)
  lon=np.array(lon)

  return np.ravel(lat),np.ravel(lon)

def findids(wrfinput):
  lat,lon=getlatlon(wrfinput)
  hvs=[]
  print(lat.shape)
  for lat0,lon0 in zip(lat,lon): 
    hvs.append(findid(lat0,lon0))
  return set(hvs)


def buildlatlon(hvs):
  import subprocess as sub
  import numpy as np
  import pickle
  import progressbar
  nx,ny=1200,1200
  lats={}
  lons={}
  for hv in hvs:
    h=int(hv[1:3])
    v=int(hv[4:])
    lats[hv]=np.zeros((nx,ny))
    lons[hv]=np.zeros((nx,ny))
    print("Processing %s"%hv)
    bar = progressbar.ProgressBar(maxval=nx*ny, \
            widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    for ix in range(nx): 
      for iy in range(ny): 
        bar.update(ix+1+iy*ny)
        cmd="geolocation -res=1km -hv=%s,%s -xy=%s,%s  -proj=SIN"%(h,v,ix,iy)
        p = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE, shell=True)
        output, errors = p.communicate()
        output=output.decode("utf-8") 
        for line in output.splitlines():#qstat[5:]:
          if "Geolocation" in line:
            #print(line)
            _,latlon=line.split(":")
            lat,lon=latlon.split()
            lat=float(lat)
            lon=float(lon)
            lats[hv][ix,iy]=lat
            lons[hv][ix,iy]=lon
            #print(lat,lon)
    bar.finish()
  pickle.dump( (lats,lons), open( "modis1klatlon.p", "wb" ) )
   



if __name__ == "__main__":
  #hvs=set(['h11v06', 'h11v07', 'h11v04', 'h11v05', 'h11v03', 'h07v05', 'h07v04', 'h07v07', 'h07v06', 'h13v03', 'h13v04', 'h13v05', 'h14v03', 'h10v03', 'h10v05', 'h10v04', 'h10v07', 'h10v06', 'h09v03', 'h09v07', 'h09v06', 'h09v05', 'h09v04', 'h08v04', 'h08v05', 'h08v06', 'h08v07', 'h12v03', 'h14v04', 'h12v06', 'h12v05', 'h12v04', 'h06v06', 'h06v07'])
  wrfinput="/glade/u/home/sunchao//data/wrfinput_d01"
  wrfinput="//glade/u/home/sunchao/model/git_work/CWRF_preprocess/cn_cut/geo_data//geo_em.d01_new.nc"
  hvs=findids(wrfinput)
  print(hvs)
  #buildlatlon(hvs)
