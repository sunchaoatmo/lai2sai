#!/usr/bin/env python
from netCDF4 import Dataset
import numpy as np
vname = "LU_INDEX"
fname = "/glade/u/home/sunchao/scratch/ERI_ICBC/ERI_ICBC2/ICBC/IC_CSSP/wrfinput_d01.2008010100"
with Dataset(fname) as fin:
  lu_index = np.squeeze(np.asarray(fin.variables[vname]))
  lu_index = set(np.unique(lu_index))

print(lu_index)
fname = "geo_em.d01_new.nc"
vnames = ["SC_LAND","LU_INDEX"]
for vname in vnames:

  with Dataset(fname,"a") as fin:
    lu_index_h = np.asarray(fin.variables[vname])
    lu_index_h[lu_index_h==22]=21
    lu_index_h[lu_index_h==24]=16
    fin.variables[vname][:]  = lu_index_h[:]

  with Dataset(fname) as fin:
    lu_index_h = np.squeeze(np.asarray(fin.variables[vname]))
    lu_index_h = set(np.unique(lu_index_h))
  print(lu_index_h)
  print(lu_index.issubset(lu_index_h))
