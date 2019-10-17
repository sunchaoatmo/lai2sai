#!/usr/bin/env python
import numpy as np
from netCDF4 import Dataset
vname ="XBFDIR"
with Dataset("wrfinput_d01","a") as fin:
  var = fin.variables[vname]
  var = np.asarray(var)
  print(len(var==0))
  var[var==0] =1
  print(len(var==0))
  fin.variables[vname][:] = var[:]
