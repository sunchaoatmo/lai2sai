#!/usr/bin/env python
import os
from subprocess import call
import ESMF
from util import Taskditributor
from datetime import datetime,timedelta
from readin import getlatlon,getnxny
from interpolate import grid_create_from_coordinates,create_locstream_spherical
from netCDF4 import Dataset,date2num
from writenc import createnc_serial
from constant import units_cur,calendar_cur,Oneday
import numpy as np
parallel=False
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
  parser.add_argument("-YS",type=int)
  parser.add_argument("-MS",type=int)
  parser.add_argument("-DS",type=int)
  parser.add_argument("-YE",type=int)
  parser.add_argument("-ME",type=int)
  parser.add_argument("-DE",type=int)
  args = parser.parse_args()
  YS,MS,DS=args.YS,args.MS,args.DS
  date_beg=datetime(YS,MS,DS,0,0,0)
  date_end=date_beg+Oneday


grids={}
vname="lwp"
outputnames=[vname]
fname="wrfinput_d01"
nx,ny=getnxny(fname)
nz=1
lat,lon=getlatlon(fname)
lat=np.ravel(lat)
lon=np.ravel(lon)
t_lon=np.array(lon)
lon = ((t_lon + 180) % 360) - 180
lon =lon.astype(np.float64)
lat =lat.astype(np.float64)
dstlocstream=create_locstream_spherical(lon,lat)
dstfield = ESMF.Field(dstlocstream, staggerloc=ESMF.StaggerLoc.CENTER)

ndays=(date_end-date_beg)
ndays=ndays.days


nday_loc,nday_beg= Taskditributor(ndays,nprocs,rank)
date_cur=date_beg+nday_beg*Oneday
date_end_loc=date_cur+nday_loc*Oneday
irec=0
FillValues=np.zeros((nx,ny))
while date_cur<date_end_loc:
  casename="CM_DATA_%06d"%(nday_beg+irec)
  casename="CM_DATA_%s"%(date_cur.strftime("%Y%m%d"))
  outputnc=createnc_serial(casename,vname,"daily",units_cur,calendar_cur,outputnames,nx,ny,ndays,nz=nz)
  #outputnc.variables["lat"][:]=lat
  #outputnc.variables["lon"][:]=lon
  fname="LWPdm%s0000001190040801GL.nc"%(date_cur.strftime("%Y%m%d"))
  if os.path.isfile(fname):
    fh   =Dataset(fname,"r")
    FillValue=fh.variables[vname]._FillValue
    lat,lon=getlatlon(fname)
    t_lon=np.array(lon)
    lon = ((t_lon + 180) % 360) - 180
    lon =lon.astype(np.float64)
    lat =lat.astype(np.float64)
    srcgrid=grid_create_from_coordinates(lon, lat)
    srcdata=np.transpose(np.asarray(fh.variables[vname][0,:,:]))
    mask = srcgrid.add_item(ESMF.GridItem.MASK)
    mask[:] = 0
    mask[srcdata<0] = 1
    mask[srcdata>500] = 1
    srcfield = ESMF.Field(srcgrid, staggerloc=ESMF.StaggerLoc.CENTER)
    regrid = ESMF.Regrid(srcfield, dstfield,
                         src_mask_values=np.array([1]),
                         unmapped_action=ESMF.UnmappedAction.IGNORE,
                         regrid_method=ESMF.RegridMethod.BILINEAR)
    srcfield.data[...]=srcdata 
    mask[:] = 1
    dstfield = regrid(srcfield, dstfield)
    outputnc.variables[vname][0,0,:,:]=dstfield.data[:]
  else:
    outputnc.variables[vname][0,0,:,:]=FillValues
  date_cur+=Oneday
  outputtime=date2num( date_cur,units=units_cur,calendar=calendar_cur)
  outputnc.variables["time"][0]=outputtime
  outputnc.close()
  irec    +=1
