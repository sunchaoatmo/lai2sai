
import numpy as np
cimport numpy as np
ctypedef np.float32_t DTYPE_f
ctypedef np.int32_t DTYPE_i

from cpython cimport array
import array

cdef array.array alpha = array.array("f", 
         [0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 
         0.50, 0.50, 0.50, 0.50, 0.50, 0.00, 
         0.00, 0.25, 0.00, 0.50])
         #0.00, 0.25, np.nan, 0.50])
# technically we should use nan however that will introduce model break for some points
cdef  float [:] calpha = alpha 


cdef array.array sai_min = array.array("f",
         [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 
          1.00, 1.00, 1.00, 1.00, 1.00, 0.10, 
          0.10, 0.50, 0.00, 1.00 ])
          #0.10, 0.50, np.nan, 1.00 ])

cdef  float [:] csai_min =sai_min 

def lai2sai0(float [:] sai0,float [:] lai0,int igbp0):
  from numpy import abs
  cdef int nloop,im
  nloop = 0
  im    = 0
  while(nloop<1000):
    """
    print(igbp0)
    print(lai0[im-1] , lai0[im])
    print(lai0)
    print(csai_min[igbp0])
    print(calpha[igbp0] * sai0[im-1])
    print(lai0[im-1] - lai0[im])
    """
    sai0_new = max( csai_min[igbp0], calpha[igbp0] * sai0[im-1] + max(lai0[im-1] - lai0[im], 0.) )
    if abs(sai0_new-sai0[im])<0.1 and nloop>20:
       break
    else:
       sai0[im] = sai0_new
    im = 0 if im==11 else im+1
    nloop = nloop +1




def lai2sai(np.ndarray[DTYPE_f, ndim=3] lai,np.ndarray[DTYPE_i, ndim=2] igbp):
  cdef int nmonth = lai.shape[0]
  cdef int nx     = lai.shape[1]
  cdef int ny     = lai.shape[2]
  cdef np.ndarray sai = np.zeros([nmonth,nx,ny], dtype=np.float32)
  cdef int ix,iy
  igbp = igbp-1
  cdef int   [:,:]    cigbp = igbp
  cdef float [:,:,:]  clai  = lai
  cdef float [:,:,:]  csai  = sai

  for ix in range(nx):
    for iy in range(ny):
      if cigbp[ix,iy]>0 and cigbp[ix,iy]<16:
        lai2sai0(csai[:,ix,iy],clai[:,ix,iy],cigbp[ix,iy])

  return sai
