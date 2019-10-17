def getlatlon(fname):
  import numpy as np
  from netCDF4 import Dataset
  fh=Dataset(fname)
  if "lat" in fh.variables:
    lat=fh.variables['lat']
    lon=fh.variables['lon']
  elif "LAT" in fh.variables:
    lat=fh.variables['LAT']
    lon=fh.variables['LON']
  elif "Latitude" in fh.variables:
    lat=fh.variables['Latitude']
    lon=fh.variables['Longitude']
  elif "CLAT" in fh.variables:
    lat=fh.variables['CLAT']
    lon=fh.variables['CLONG']
  else:
    import sys
    sys.exit("no lat lon avaiable in this file stopped!")

  return np.asarray(lat),np.asarray(lon)

def getnxny(fname):
  from netCDF4 import Dataset
  fh=Dataset(fname)
  ny=fh.dimensions['south_north'].size
  nx=fh.dimensions['west_east'].size
  return nx,ny

def getprojectinfo(fname):
  from netCDF4 import Dataset
  fh=Dataset(fname)
  TRUELAT1=fh.TRUELAT1
  TRUELAT2=fh.TRUELAT2
  CEN_LAT=fh.CEN_LAT
  CEN_LON=fh.CEN_LON 
  STAND_LON=fh.STAND_LON
  MAP_PROJ=fh.MAP_PROJ
  DX=fh.DX
  DY=fh.DY
  return TRUELAT1,TRUELAT2,CEN_LAT,CEN_LON,STAND_LON,MAP_PROJ,DX,DY
def getlandmask(fname):
  from netCDF4 import Dataset
  import numpy as np
  fh=Dataset(fname)

  lm=fh.variables["LANDMASK"]
  return np.asarray(lm[0,:,:])


def getscwater(fname):
  from netCDF4 import Dataset
  import numpy as np
  fh=Dataset(fname)
  lm=fh.variables["SC_WATER"]
  return np.asarray(lm[0,:,:])


