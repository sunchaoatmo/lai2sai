#!/usr/bin/env python
from netCDF4 import Dataset
import numpy as np
from clai2sai import lai2sai
with Dataset("modis_20010101_IGBP_daily.nc") as fin:
  igbp = fin.variables["IGBP"][0,:,:]
  igbp = np.squeeze(np.asarray(igbp,dtype=np.int32))
nx,ny=igbp.shape

with Dataset("MODIS_LAI_monmean.nc") as fin:
  lai = fin.variables["LAI"]
  lai = np.squeeze(np.asarray(lai))

sai = lai2sai(lai,igbp)

periods = "monthly"
fname = "modis_sai_monthly.nc"
nt    = 12
vname = "sai"
with Dataset(fname,"w") as fou:
  fou.createDimension("lat"     , nx )
  fou.createDimension("lon"     , ny )
  fou.createDimension(periods   , nt)  #hard coded but usually we consider only 4 seasons
  time = fou.createVariable(periods    , "i4"  , (periods , ))
  time[:]           = range(1,nt+1)
  time.units        = periods
  nc_dim=(periods,"lat","lon",)
  fou.createVariable(vname,"f4",nc_dim)
  fou.variables[vname][:] = sai[:]
 

