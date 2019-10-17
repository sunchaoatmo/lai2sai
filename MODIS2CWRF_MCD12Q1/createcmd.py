#!/usr/bin/env python
import time
from subprocess import Popen
import os.path
import os
import argparse
import datetime
import argparse
parser = argparse.ArgumentParser(description='Process daiyly data into seasonal the varialbe you choose ')
parser.add_argument("--sub","-s", action="store_true")
args = parser.parse_args()

YB=2000
YE=2016 
Oneday=datetime.timedelta(days=1)

surfixs=[]
juliandays=[]
for year in range(YB,YE):
  date_beg=datetime.datetime(year,1,1)
  date_end=datetime.datetime(year,12,31)
  cur_date=date_beg
  while cur_date<date_end:
    surfixs.append(cur_date)
    julianday=cur_date-date_beg
    julianday=julianday.days+1
    juliandays.append(julianday)
    cur_date=cur_date+8*Oneday

nlines=0
ncmdfile=0
cmdfname="cmdfile_%04d"%ncmdfile
maximumtask=36
#maximumtask=5

if os.path.isfile(cmdfname):
  os.remove(cmdfname)
jobdefault="job.cmdfile_default"
print(len(surfixs))

for surfix,julianday in zip(surfixs,juliandays):
  cmd="/glade/u/home/sunchao/scratch/Dai_LAI/ALL/MODIS2CWRF.py -YS %s -MS %s -DS %s \n"%(surfix.year,surfix.month,surfix.day)
  with open(cmdfname,"a") as fo:
    fo.write(cmd)
  nlines+=1
  if nlines==maximumtask:
    jobfile_loc="job.mpmd_%04d"%ncmdfile
    with open(jobdefault,"r") as fi:
      with open(jobfile_loc,"w") as fo:
        for line in fi:
          line=line.replace("cmdfname",cmdfname)
          line=line.replace("NCPU",str(maximumtask))
          fo.write(line)
    cmd="qsub %s"%jobfile_loc
    if args.sub:
      time.sleep(.5)
      Popen(cmd,shell=True)
    nlines=0
    ncmdfile+=1
    cmdfname="cmdfile_%04d"%ncmdfile
    if os.path.isfile(cmdfname):
      os.remove(cmdfname)
if nlines>0:
    cmdfname="cmdfile_%04d"%ncmdfile
    jobfile_loc="job.mpmd_%04d"%ncmdfile
    with open(jobdefault,"r") as fi:
      with open(jobfile_loc,"w") as fo:
        for line in fi:
          line=line.replace("cmdfname",cmdfname)
          line=line.replace("NCPU",str(nlines))
          fo.write(line)
    if args.sub:
      cmd="qsub %s"%jobfile_loc
      Popen(cmd,shell=True)
