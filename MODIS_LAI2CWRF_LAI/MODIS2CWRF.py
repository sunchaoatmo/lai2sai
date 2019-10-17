#!/usr/bin/env python
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
from constant import units_cur,calendar_cur,Oneday
import numpy as np
parallel=False
hvs=set(['h11v06', 'h11v07', 'h11v04', 'h11v05', 'h11v03', 'h07v05', 'h07v04', 'h07v07', 'h07v06', 'h13v03', 'h13v04', 'h13v05', 'h14v03', 'h10v03', 'h10v05', 'h10v04', 'h10v07', 'h10v06', 'h09v03', 'h09v07', 'h09v06', 'h09v05', 'h09v04', 'h08v04', 'h08v05', 'h08v06', 'h08v07', 'h12v03', 'h14v04', 'h12v06', 'h12v05', 'h12v04', 'h06v06', 'h06v07'])
hvs=set(['h11v06', 'h11v07', 'h11v04', 'h11v05', 'h11v03', 'h07v05',  'h07v07', 'h07v06', 'h13v03', 'h13v04',  'h14v03', 'h10v03', 'h10v05', 'h10v04', 'h10v07', 'h10v06', 'h09v03',  'h09v06', 'h09v05', 'h09v04', 'h08v04', 'h08v05', 'h08v06', 'h08v07', 'h12v03', 'h14v04', 'h12v05', 'h12v04'])
if parallel:
  from mpi4py import MPI
  comm = MPI.COMM_WORLD
  rank = comm.rank  # The process ID (integer 0-3 for 4-process run)
  nprocs = comm.Get_size()
  YS,MS,DS=1982,01,01
  YE,ME,DE=2009,12,31
  date_beg=datetime(YS,MS,DS,0,0,0)
  date_end=datetime(YE,ME,DE,0,0,0)
else:
  nprocs=1
  rank=0
  import argparse
  parser = argparse.ArgumentParser(description='Process daiyly data into seasonal the varialbe you choose ')
  parser.add_argument("-YS",type=int,default=2000)
  parser.add_argument("-MS",type=int,default=9)
  parser.add_argument("-DS",type=int,default=5)
  parser.add_argument("-YE",type=int,default=2000)
  parser.add_argument("-ME",type=int,default=9)
  parser.add_argument("-DE",type=int,default=5)
  args = parser.parse_args()
  YS,MS,DS=args.YS,args.MS,args.DS
  date_beg=datetime(YS,MS,DS,0,0,0)
  date_org=datetime(YS,1,1,0,0,0)
  julianday=date_beg-date_org
  julianday=julianday.days+1
  date_end=date_beg+Oneday
year_end=datetime(YS,12,31,0,0,0)


grids={}
#vname="tpw_l"
from  collections import OrderedDict
outputnames=OrderedDict()
#outputnames["ctt"]="Cloud_Top_Temperature_Mean"
outputnames["LAI"]="Lai_1km"
fname="/glade/u/home/sunchao//data/wrfinput_d01"
fname="/glade/u/home/sunchao/scratch/us_15/1992120100-1993010100/wrfinput_d01"
fname="/glade/u/home/sunchao/scratch/us_10/1993010100-1994010100/wrfinput_d01"

nx,ny=getnxny(fname)
#nx,ny=(nx-1)*3,(ny-1)*3
#ny,nx=13701,19401

print("read landmask")
landmask=getlandmask(fname)
print("read watermask")
scwater=getscwater(fname)
print("get project")
truelat1,truelat2,cen_lat,cen_lon,stand_lon,map_proj,dx,dy =getprojectinfo(fname)

print("dx= ",dx,"dy= ",dy)
#dx=10000
#dy=10000

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
ndays=(date_end-date_beg)
ndays=ndays.days
nday_loc,nday_beg= Taskditributor(ndays,nprocs,rank)
date_cur=date_beg+nday_beg*Oneday
date_end_loc=date_cur+nday_loc*Oneday
irec=0
FillValues=np.ones((nx,ny))
firsttime=True
# more information visit:https://modis-land.gsfc.nasa.gov/MODLAND_grid.html
"""
remaproj.remap(nx_src, ny_src, mapprj, deltax, deltay, stdlon, stdlat, &
                     orglat, orglon, &
                     numcol, numrow,                   &
                     numtile ,listih,listjv,data_src , &
                     missing_value, &
                     project_method, &
                     data_dst)
"""


numcol=1200
numrow=1200
numtile=0
totaltile=len(hvs)
srcdatas=np.zeros((numcol,numrow,totaltile),order='F',dtype=np.float32)
#data_dst=np.zeros((numcol,numrow,numtile),order='F',dtype=np.float32)
#data_dst=np.zeros((ny,nx),order='F',dtype=np.float32)
#data_dst=np.zeros((nx,ny),order='F',dtype=np.float32)
outputnc=None

# from their website http://globalchange.bnu.edu.cn/research/lai 
scale_factor=0.1
units="m^2/m^2"
# from their website http://globalchange.bnu.edu.cn/research/lai 
while date_cur<date_end_loc:
  casename="modis_%s"%(date_cur.strftime("%Y%m%d"))
  julianday=date_cur-date_org
  julianday=julianday.days+1
  listih,listjv=[],[]

  for ihv,hv in enumerate(hvs):
    h=int(hv[1:3])
    v=int(hv[4:6])
    pattern   = "MOD15A2.h%02dv%02d/MOD15A2.A%s%03d.h%02dv%02d*hdf"%(h,v,date_cur.strftime("%Y"),julianday,h,v)
    print(pattern)
    fnames=glob(pattern)
    print("Reading %s"%fnames)
    print(pattern)
    if len(fnames):
      listih.append(h)
      listjv.append(v)
      fname =fnames[0]
      f   =SD(fname,SDC.READ)
      print(fname)
      for vname,modisname in outputnames.iteritems():
        srcdata=f.select(modisname)
        #ET_QC=f.select("LAI_1km_QC")
        long_name="LAI" #srcdata.long_name
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
        #ET_QC=np.asarray(ET_QC[:,:])
        #srcdata[ET_QC!=0]=FillValue
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


        #x[unmappedDstList<0]=FillValue_unscale
  data_dst=np.transpose(data_dst)
  #data_dst[landmask==0]=FillValue
  data_dst[scwater==8]=FillValue
  i,j=np.where(data_dst!=FillValue)

  data_dst[i,j]=data_dst[i,j]*scale_factor
  remday=year_end-date_cur
  remday=min(8,remday.days)
  for iday in range(remday): 
    outputnc.variables[vname][iday,0,:,:]=data_dst
    outputtime=date2num( date_cur,units=units_cur,calendar=calendar_cur)
    outputnc.variables["time"][iday]=outputtime
    date_cur+=Oneday
  #outputnc.variables[vname][0,0,:,:]=data_dst
  outputnc.variables[vname].units=units
  outputnc.variables[vname].long_name=long_name
  if vname=="tpw_m":
    outputnc.variables[vname][0,0,:,:]=(outputnc.variables["tpw_m"][0,0,:,:]
                                       -outputnc.variables["tpw_h"][0,0,:,:]
                                       -outputnc.variables["tpw_l"][0,0,:,:])

  outputnc.close()
  irec    +=1
  """
      pattern   = "MOD08_D3.A2016001*"
      fname=glob(pattern)[0]
      f   =SD(fname,SDC.READ)
      for vname,modisname in outputnames.iteritems():
        srcdata=f.select(modisname)
        FillValue_unscale=srcdata._FillValue
        long_name=srcdata.long_name
        units=srcdata.units
        if firsttime:
          FillValues=FillValues*FillValue_unscale
          firsttime=False
        if not outputnc:
          outputnc=createnc_serial(casename,"tpw","daily",units_cur,calendar_cur,
                                 outputnames,nx,ny,units=units,
                                 long_name=long_name,nz=nz,FillValue=FillValue_unscale)
        outputnc.variables[vname][0,0,:,:]=FillValues
  """
