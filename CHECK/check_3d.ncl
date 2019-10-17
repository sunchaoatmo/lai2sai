load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
; ";" for description ";;" for debug.


begin
    fw=addfile("geo_em.d01_new.nc","w")
    name =        (/"FR_PH","FR_SAND","CEC","XSALF","FR_CLAY","GRAVEL","LANDUSEF","OC" ,"RBD","SOILCBOT","SOILCTOP","XSGSRF"/)
    upbd =        (/9      ,1        ,150  ,3      ,1        ,50      ,1         ,100   ,3    ,1         ,1         ,5/)
    lwbd =        (/0      ,0.01     ,0    ,0.01   ,0.001     ,0.001    ,0.0       ,0.001,0.0  ,0         ,0         ,0.00/)
    typicalvalue =(/5      ,0.2      ,20   ,1      ,0.2      ,1       ,0.1       ,0.1  ,0.1  ,0         ,0         ,0.1/)
    landmask=fw->LANDMASK
    cnt = dimsizes(name)

do idx=0,cnt-1
    field_3d=fw->$name(idx)$ ; sci
    print("Checking"+name(idx))
    dim=dimsizes(field_3d)
    do i=0,dim(2)-1
        do j=0,dim(3)-1
		if ((landmask(0,i,j).gt.0.5))then
          do k=0,dim(1)-1
             if (ismissing(field_3d(0,k,i,j)).or.(field_3d(0,k,i,j)).gt.upbd(idx).or.(field_3d(0,k,i,j).lt.lwbd(idx))) then
             print("i="+i+" j="+j+" k="+k+name(idx)+"="+field_3d(0,k,i,j))
             field_3d(0,k,i,j)=(/typicalvalue(idx)/)
             end if

          end do
            end if
        end do
    end do

   fw->$name(idx)$=field_3d ; sci
   delete(field_3d)
end do
end
