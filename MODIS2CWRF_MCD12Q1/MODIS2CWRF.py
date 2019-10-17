#!/usr/bin/env python
import argparse
from  collections import OrderedDict
import remaproj 
from pyhdf.SD import SD,SDC
from glob import glob
import os
from subprocess import call
import ESMF
from util import Taskditributor
from datetime import datetime,timedelta
from readin import getlatlon,getnxny,getscwater,getlandmask,getprojectinfo
from interpolate import grid_create_from_coordinates,create_locstream_spherical
from netCDF4 import Dataset,date2num
from writenc import createnc_serial
from constant import units_cur,calendar_cur,Oneyear
import numpy as np
hvs=set(['h11v06', 'h11v07', 'h11v04', 'h11v05', 'h11v03', 'h07v05', 'h07v04', 'h07v07', 'h07v06', 'h13v03', 'h13v04', 'h13v05', 'h14v03', 'h10v03', 'h10v05', 'h10v04', 'h10v07', 'h10v06', 'h09v03', 'h09v07', 'h09v06', 'h09v05', 'h09v04', 'h08v04', 'h08v05', 'h08v06', 'h08v07', 'h12v03', 'h14v04', 'h12v06', 'h12v05', 'h12v04', 'h06v06', 'h06v07'])

parser = argparse.ArgumentParser(description='Process daiyly data into seasonal the varialbe you choose ')
parser.add_argument("-YS",type=int,default=2001)
parser.add_argument("-YE",type=int,default=2016)
args = parser.parse_args()
YS   = args.YS
YE   = args.YE


grids={}
outputnames=OrderedDict()
nz=1 
outputnames["IGBP"]="LC_Type1"

fname="/glade/u/home/sunchao/scratch/us_15/1992120100-1993010100/wrfinput_d01"
fname="/glade/u/home/sunchao/scratch/us_10/1993010100-1994010100/wrfinput_d01"
nx,ny=getnxny(fname)

print("read landmask")
landmask=getlandmask(fname)
print("read watermask")
scwater=getscwater(fname)
truelat1,truelat2,cen_lat,cen_lon,stand_lon,map_proj,dx,dy =getprojectinfo(fname)

nz=1
lat,lon=getlatlon(fname)
lat0=15.3832
lon0=-120.6885
lat=np.ravel(lat)
lon=np.ravel(lon)
t_lon=np.array(lon)
lon = ((t_lon + 180) % 360) - 180
lon =lon.astype(np.float64)
lat =lat.astype(np.float64)
irec=0
FillValues=np.ones((nx,ny))
firsttime=True
# more information visit:https://modis-land.gsfc.nasa.gov/MODLAND_grid.html


numcol=2400
numrow=2400
totaltile=len(hvs)
srcdatas=np.zeros((numcol,numrow,totaltile),order='F',dtype=np.float32)
outputnc=None

scale_factor=1
units="coef"
julianday = 1 # this is an annual product
for year in range(YS,YE+1):
  numtile=0
  date_cur =datetime(year,1,1,0,0,0)
  casename="modis_%s"%(date_cur.strftime("%Y%m%d"))
  listih,listjv=[],[]

  for ihv,hv in enumerate(hvs):
    h=int(hv[1:3])
    v=int(hv[4:6])
    pattern   = "MCD12Q1.A%s%03d.h%02dv%02d*hdf"%(date_cur.strftime("%Y"),julianday,h,v)
    fnames=glob(pattern)
    print("Reading %s"%fnames)
    if len(fnames):
      listih.append(h)
      listjv.append(v)
      fname =fnames[0]
      f   =SD(fname,SDC.READ)
      for vname,modisname in outputnames.iteritems():
        print(modisname)
        srcdata=f.select(modisname)
        long_name="FVC" #srcdata.long_name
        FillValue=-9999 #srcdata._FillValue#*scale_factor
        FillValue_unscale=-9999 #srcdata._FillValue
        if firsttime:
          FillValues=FillValues*FillValue_unscale
          firsttime=False
        vname0=vname # why do this? because the lateron part need only one output prefix, this is a little bit arkward, needed to be improved in the future
        if outputnc is None:
          outputnc=createnc_serial(casename,vname0,"daily",units_cur,calendar_cur,
                                 outputnames,nx,ny,units=units,
                                 long_name=long_name,nz=nz,FillValue=FillValue_unscale)
        srcdata=np.asarray(srcdata[:,:])
        srcdatas[:,:,numtile]=srcdata
      numtile=numtile+1

  print("All tiles ready, totally there are %s tiles"%numtile)
  print(truelat1,truelat2,stand_lon)
  data_dst=remaproj.remap(nx_src=ny, ny_src=nx, 
                       mapprj=map_proj, deltax=dx, deltay=dy, stdlon=stand_lon, 
                       truelat1=truelat1,truelat2=truelat2,
                       ctrlat=15.3832, ctrlon=-120.6885, 
                       numcol=numcol, numrow=numrow,        
                       numtile=numtile,listih=listih,listjv=listjv,
                       data_src=srcdatas[:,:,0:numtile] , 
                       missing_value=FillValue, 
                       project_method="near")#data_dst=data_dst)
  data_dst=np.transpose(data_dst)
  data_dst=data_dst*scale_factor
  data_dst[scwater==8]=FillValue
  outputnc.variables[vname][irec,:,:]=data_dst
  outputtime=date2num( date_cur,units=units_cur,calendar=calendar_cur)
  outputnc.variables["time"][irec]=outputtime
  print(date_cur)
  irec    +=1

outputnc.variables[vname].units=units
outputnc.variables[vname].long_name=long_name
outputnc.close()
