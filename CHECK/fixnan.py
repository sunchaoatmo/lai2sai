#!/usr/bin/env python
from netCDF4 import Dataset
import numpy as np
with Dataset("geo_em.d01_new.nc","a") as fi:
  for vname in fi.variables:
    var =fi.variables[vname]
    var = np.asarray(var)
    try:
      print(vname,np.sum(np.isnan(var)))
    except:
      pass
  vname = "DPLAKE"
  dplake = fi.variables[vname]
  dplake = np.asarray(dplake)
  dplake[np.isnan(dplake)] = 5
  dplake[dplake>150]=150
  fi.variables["DPLAKE"][:]= dplake
  dplake=fi.variables["FLAKE"]
  dplake = np.asarray(dplake)
  print(np.sum(np.isnan(dplake)))
  """
  """
