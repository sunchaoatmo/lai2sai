seasonList=[ [12,  2], [3, 5], [6,  8], [9,  11]]
monthlyList=[ [1, 1],[2,2],[3,3],[4,4],[5,5],[6, 6],[7, 7],[8,8], [9, 9 ],[10, 10],[11,11],[12,12]]
wrfout_data_fmt="%Y-%m-%d_%H:%M:%S"
prefix="wrfout*"
dry_lim=1
qvalue=0.95
G = 9.81
Rd = 287.04
Rv = 461.6
Rm = .608 
Cp = 1004.
Cp = 7.*Rd/2.
Cv = Cp-Rd
CPMD = 0.887
RCP = Rd/Cp
p0 = 100000.
Pmb_level_ERI=[1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 100, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 775, 800, 825, 850, 875, 900, 925, 950, 975, 1000]
units_cur = 'days since 0001-01-01 00:00'
calendar_cur='gregorian'
from datetime import timedelta
Oneday=timedelta(days=1)
Oneyear=timedelta(days=365)
