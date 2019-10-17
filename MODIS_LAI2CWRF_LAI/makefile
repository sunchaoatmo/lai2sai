AR=ar
ARFLAGS         =      ru
INCLUDES = 

F2PY_FLAGS= -I./ -L./ -lmap 

SRCS = remaproj.f90

F2PY = f2py
FC   =ifort
FFLAGS=-fPIC 
OBJS = $(SRCS:.f90=.so)
all:    $(OBJS)
	@echo  ${MODULE}.so has been compiled

remaproj.so: remaproj.f90 libmap.a 
	$(F2PY) $(F2PY_FLAGS) --f90flags=-fPIC  --fcompiler=intelem --f90flags="-O3" -m remaproj -c remaproj.f90





libmap.a: module_map_utils.f90
	ifort -fPIC -c module_map_utils.f90 
	ar crs libmap.a module_map_utils.o



clean:
	$(RM) *.a *.o *.mod  *.so

#depend: $(SRCS)
#	makedepend $(INCLUDES) $^


# DO NOT DELETE THIS LINE -- make depend needs it
