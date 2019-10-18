
! Min Xu 
! ISWS
!
! 2009/12/25: This program is used 
!             1. to remap the MODIS Sinusoidal projection to the map projects 
!                set by user. Currently only the projections supported by
!                module_map_util.f90 are supported since the major map transfer 
!                function is directly from this module. (area/near)
!                Supported map projection
!                Cylindrical Lat/Lon (code = PROJ_LATLON)
!                Mercator (code = PROJ_MERC)
!                Lambert Conformal (code = PROJ_LC)
!                Polar Stereographic (code = PROJ_PS)
!             2. to get the ranges of Lat/Lons to hold the specific domain in
!                specific map projection. (domain)
!             3. to get the station values and the locations of sites are set by user. (point)
!
!
!
! 2010/12/05: find the bug in determing the domain lat/lon domain., fixed it by:
!             1. get the max lats in the north boundary
!             2. get the min lats in the south boundary
!             3. get the max lons in east
!             4. get the min lons in west
!
! 2012/06/01: fixed the bug, that missing tiles in domain will be set to -1.2e27 value
!             since the missing tiles are the ocean tiles, to avoid the confusing with 
!             filtering missing and filling value in original hdf, we set the new missing
!             value is -1.0e20

! 2012/08/08: Attn: the point and area functions may have some problem, please check when you use

  subroutine remap(nx_src, ny_src, mapprj, deltax, deltay, stdlon,&
                     truelat1,truelat2, &
                     ctrlat, ctrlon, &
                     numcol, numrow,                   &
                     numtile ,listih,listjv,data_src , &
                     missing_value, &
                     project_method, &
                     data_dst)



  use map_utils
  implicit none
  real, parameter :: large_dist=1000

  real,   intent(in) :: missing_value 
  integer  ,   intent(in)          :: nx_src, ny_src, mapprj
  character (10),intent(in)        :: project_method
  integer  ,   intent(in)          :: numcol, numrow
  integer  ,   intent(in)          :: numtile 
  real     ,   intent(in)          :: deltay, deltax                        ! meters
  real     ,   intent(in)          :: stdlon, truelat1,truelat2, ctrlat, ctrlon
  integer, dimension(numtile      ), intent(in) :: listih, listjv
  real,    dimension(numcol, numrow,numtile  ), intent(in) :: data_src
  !real,    dimension(numrow, numcol,numtile  ), intent(in) :: data_src
  !real,    dimension(ny_src, nx_src)  , intent(inout) :: data_dst
  real,    dimension(ny_src, nx_src)  , intent(out) :: data_dst
  !real,    dimension(nx_src, ny_src)  , intent(out) :: data_dst
 
  !local var
  ! map relation 
  type (proj_info)   :: prjout

  ! coefficients for albedo

  integer, dimension(:, :   ), allocatable :: iw, jw
  real,    dimension(:, :   ), allocatable :: sw
  real,    dimension(:, :   ), allocatable :: glat, glon, xprj, yprj
  real,    dimension(:, :   ), allocatable             :: wght, ngrd
  integer                                  :: mnlocs(2)

  real                                     :: dis2
  real                                     :: x0,y0


  integer     :: ih, jv, i, j,  itile, ik, im, jm, is, js, iu, ju
  integer     :: nx_prj,ny_prj
  real            :: knowni,knownj
  real            ::  orglat, orglon

! 

! -----------------------------------
! set up proj_out for rcm output data
! -----------------------------------

  ! for point mode, no need to have map transfer
  ! 

  knowni=1
  knownj=1
  call map_set(proj_lc,  ctrlat, ctrlon, deltax, stdlon, truelat1,truelat2, nx_src, ny_src, prjout)

  !call ij_to_latlon(prjout, -float(ny_src+1)/2.+2., -float(nx_src+1)/2.+2., orglat, orglon)

  !call map_set(proj_lc,  orglat, orglon, deltax, stdlon, truelat1,truelat2, nx_src, ny_src, prjout)

  !data_dst: varibles, wght: weighting coefs, ngrd: number of fine grids  
  allocate(wght(ny_src, nx_src))
  allocate(ngrd(nx_src, ny_src))


  allocate(glon(numrow, numcol))
  allocate(glat(numrow, numcol))
  allocate(xprj(numrow, numcol))
  allocate(yprj(numrow, numcol))
  allocate(iw(numrow, numcol), jw(numrow, numcol), sw(numrow, numcol))

! ========================================================================================================================
! get the lat/lon for each tiles 
! call latlon_to_ij(prjout, 49.08019, -52.10629, x0, y0)

! print*,"x0=",x0,"y0=",y0,"nx_src",nx_src,"ny_src",ny_src,deltax

 
  select case(trim(project_method))
  case('area')
    data_dst = 0.
    wght = 0.
    ngrd = 0.
  case('near')
    data_dst = missing_value
    wght = large_dist
  end select
  
  do itile=1, numtile
     ih = listih(itile)
     jv = listjv(itile)

     if(ih < 0 .or. jv < 0) then
       call sintile2latlon(numrow, numcol, -ih, -jv, glat, glon)
     else
       call sintile2latlon(numrow, numcol, +ih, +jv, glat, glon)
     end if


     do j = 1, numcol
        do i = 1, numrow
           call latlon_to_ij(prjout, glat(i,j), glon(i,j), xprj(i,j), yprj(i,j))
        enddo 
     enddo


     if(maxval(xprj) < 0.5 .or. minval(xprj) > ny_src+0.5) then
        iw = 0
        jw = 0
        sw = 0.0
        cycle
     endif

     if(maxval(yprj) < 0.5 .or. minval(yprj) > nx_src+0.5) then
        iw = 0
        jw = 0
        sw = 0.0
        cycle
     endif
     do j=1, numcol
       do i=1, numrow
         jw(i,j)=ceiling(xprj(i,j)-0.5)
         iw(i,j)=ceiling(yprj(i,j)-0.5)
         sw(i,j)=1.0
       enddo
     enddo

     ! begin interpolation
     ! initialization

     do j=1, numcol
       do i=1, numrow
          if(iw(i,j) <= nx_src .and. iw(i,j) >= 1 .and. &
             jw(i,j) <= ny_src .and. jw(i,j) >= 1 ) then

             select case(trim(project_method))
             case('area')
               print*,"Not fully implemented!"
               stop
               if(data_src(j,i,itile) /= missing_value .and. data_src(j,i,itile) /= -missing_value) then
                 data_dst(jw(i,j),iw(i,j) ) = data_dst(jw(i,j),iw(i,j) ) + sw(i,j) * data_src(j,i,itile)
                 wght(jw(i,j), iw(i,j)) = wght(jw(i,j), iw(i,j)) + sw(i,j)
               endif
               ngrd(iw(i,j), jw(i,j)) = ngrd(iw(i,j), jw(i,j)) + sw(i,j)

             case('near') 
                do ju=0, 0
                  do iu=0, 0
                !do ju=-2, 2
                !  do iu=-2, 2
                     is = min(nx_src,max(1,iw(i,j) + iu))
                     js = min(ny_src,max(1,jw(i,j) + ju))


                     dis2 = (yprj(i,j) - is)**2 + (xprj(i,j) - js)**2
                     !dis2 = (xprj(i,j) - is)**2 + (yprj(i,j) - js)**2
                     if(wght(js, is) > dis2 .and. abs(data_src(numrow-j+1,i,itile) - missing_value).gt.large_dist) then
                     !if(wght(js, is) > dis2 .and. data_src(numrow-j+1,i,itile) /= missing_value) then
                        data_dst(js,is) = data_src(numrow-j+1,i,itile)
                        wght(js, is) = dis2
                        !data_dst(js,is) = data_src(j,i,itile)
                       ! wght(js, is) = dis2
                     endif
                  enddo
                enddo
             end select

          endif
       enddo
     enddo

  enddo

  ! Min Xu, 50% point should have value in 30*30 grid, 450 or 360
  ! for 1 km it is not necessary
  if(project_method == 'area') then 
    print*,"Not fully implemented!"
    stop
    where(wght > 0.)
       data_dst = data_dst / wght
    elsewhere
       data_dst = missing_value
    end where
  endif

  deallocate(iw, jw, sw)
  deallocate(wght, ngrd)
  deallocate(glon, glat)
  deallocate(xprj, yprj)

  end subroutine remap


  subroutine sintile2latlon(mx, my, ih, jv, glat, glon) 
  implicit none

  integer,                 intent(in ) :: mx, my, ih, jv
  real, dimension(mx, my), intent(out) :: glat, glon   ! [-90:90], [-180:180]
  integer                              :: i, j

  real(8), parameter                   :: re=6371007.181
  real(8), parameter                   :: pi=3.141592653589793238
  real(8), parameter                   :: r2d=180/pi
  real(8), parameter                   :: d2r=pi/180

  real                                 :: delta_m, delta_x, delta_y, x0_sin, y0_sin, xc_sin, yc_sin

  delta_m = re * 10.0 * d2r
  delta_x = delta_m / real(mx)
  delta_y = delta_m / real(my)

  x0_sin = -(18-ih)*delta_m
  y0_sin =  (08-jv)*delta_m
  do j=1,my
    do i=1,mx
      !mid

      xc_sin = x0_sin + real(i-0.5) * delta_x
      yc_sin = y0_sin + real(j-0.5) * delta_y
      glat(i,j) = yc_sin / re * r2d
      glon(i,j) = xc_sin /(re * cos(glat(i,j) * d2r)) * r2d
      if(i.eq.1 .and.j.eq.1) then
        print*,"h=",ih,"v=",jv,"lat=",glat(i,j),"lon=",glon(i,j)
      endif
    enddo
  enddo

  end subroutine sintile2latlon
  


!  subroutine sintile2latlon(mx, my, ih, jv, glat, glon) 
!    nrow_half = 180 * 60
!    projParam[8] = nrow_half * 2.0
!    projParam[10] = 1.0
!
!    *nl = PROJ[iproj].nl_grid * pixel_size_ratio;
!    *ns = PROJ[iproj].ns_grid * pixel_size_ratio;
!  
!    tile->nl = *nl;
!    tile->ns = *ns;
!    tile->nl_tile = PROJ[iproj].nl_tile * pixel_size_ratio;
!    tile->ns_tile = PROJ[iproj].ns_tile * pixel_size_ratio;
!    tile->nl_offset = 0;
!    tile->ns_offset = 0;
!    tile->nl_p = *nl;
!    tile->ns_p = *ns;
!    tile->siz_x = tile->siz_y = PROJ[iproj].pixel_size / pixel_size_ratio;
!    tile->ul_x = PROJ[iproj].ul_xul + (0.5 * tile->siz_x);
!   tile->ul_y = PROJ[iproj].ul_yul - (0.5 * tile->siz_y);
