from netCDF4 import Dataset
def createsmnc(casename,vname,periods,fields,nx,ny,nz=None):
  filename            = "%s_%s_%s.nc"%(casename,vname,periods)
  rootgrp             = Dataset(filename                   , "w")
  rootgrp.createDimension("lat"      , nx )
  rootgrp.createDimension("lon"      , ny )
  nt=4 if periods=="seasonal" else 12
  rootgrp.createDimension(periods   , nt)  #hard coded but usually we consider only 4 seasons
  subtime              = rootgrp.createVariable(periods    , "i4"  , (periods , ))
  subtime[:]           = range(1,nt+1)
  subtime.units        = periods
  rootgrp.createDimension("time"     , None)
  times               = rootgrp.createVariable("time"      , "i4"  , ("time"   , ))
  times.units         = "year"
  if nz:
    nc_dim=("time",periods,"bottom_top","lat","lon",)
    rootgrp.createDimension("bottom_top"      , nz )
  else:
    nc_dim=("time",periods,"lat","lon",)
  for field in fields:
    rootgrp.createVariable(field,"f4",nc_dim)
  return rootgrp


def createnc(comm,casename,vname,periods,units,calendar,fields,nx,ny,ntime,nz=None):
  from mpi4py import MPI

  filename            = "%s_%s_%s.nc"%(casename,vname,periods)
  rootgrp             = Dataset(filename     , "w" ,
                                parallel=True, comm=comm,
                                info=MPI.Info())
  rootgrp.createDimension("west_east"        , nx )
  rootgrp.createDimension("south_north"      , ny )
  #rootgrp.createDimension("time"     , None)
  rootgrp.createDimension("time"     , ntime)
  T                   = rootgrp.createVariable("time"    , "f4"  , ("time" , ))
  T.units             = units
  T.calendar          = calendar
  if nz:
    rootgrp.createDimension("bottom_top"      , nz )
    nc_dim=("time","bottom_top","south_north","west_east",)
  else:
    nc_dim=("time","south_north","west_east",)
  for field in fields:
    rootgrp.createVariable(field,"f4",nc_dim)
  return rootgrp 

def createnc_s(casename,vname,periods,units_c,calendar,fields,nx,ny,nz=None,long_name=None,units=None):

  filename            = "%s_%s_%s.nc"%(casename,vname,periods)
  rootgrp             = Dataset(filename     , "w" )
  rootgrp.createDimension("west_east"        , nx )
  rootgrp.createDimension("south_north"      , ny )
  rootgrp.createDimension("time"     , None)
  T                   = rootgrp.createVariable("time"    , "f4"  , ("time" , ))
  T.units             = units_c
  T.calendar          = calendar
  if nz:
    rootgrp.createDimension("bottom_top"      , nz )
    nc_dim=("time","bottom_top","south_north","west_east",)
  else:
    nc_dim=("time","south_north","west_east",)
  for field in fields:
    var=rootgrp.createVariable(field,"f4",nc_dim)
    if units:
      var.units=units
    if long_name:
      var.long_name=long_name
  return rootgrp 

def createnc_serial(casename,vname,periods,units_c,calendar,fields,nx,ny,nday=None,
                     nz=None,long_name=None,units=None,FillValue=None,
                    valid_min=None,valid_max=None):

  filename            = "%s_%s_%s.nc"%(casename,vname,periods)
  rootgrp             = Dataset(filename     , "w" )
  rootgrp.createDimension("west_east"        , nx )
  rootgrp.createDimension("south_north"      , ny )
  rootgrp.createDimension("time"     , None)
  #rootgrp.createDimension("time"     , ntime)
  T                   = rootgrp.createVariable("time"    , "f4"  , ("time" , ))
  T.units             = units_c
  T.calendar          = calendar
  if nz:
    rootgrp.createDimension("bottom_top"      , nz )
    nc_dim=("time","bottom_top","south_north","west_east",)
  else:
    nc_dim=("time","south_north","west_east",)
  for field in fields:
    var=rootgrp.createVariable(field,"f4",nc_dim,fill_value=FillValue)
    if units:
      var.units=units
    if long_name:
      var.long_name=long_name
    if valid_min is not None:
      var.valid_min=valid_min
    if valid_max is not None:
      var.valid_max=valid_max
  nc_dim=("south_north","west_east",)
  #rootgrp.createVariable("lat","f4",nc_dim)
  #rootgrp.createVariable("lon","f4",nc_dim)
  return rootgrp 


