load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
; ";" for description ";;" for debug.


begin
    fw=addfile("geo_em.d01_new.nc","w")
    name =        (/"BEDROCK","XFSKY","XFVEG","XHSDV","XMOANG","XMOANI","XMOSTD","XORASP","XORO","XORSLO","XSGASP","XSLPXS","XSLPYS","XSOSLO","XSOSTD"/)
    upbd =        (/10       ,1      ,1      ,1000   ,20      ,1       ,8000    ,10      ,1     ,1       ,5       ,1,1,1,500/)
    lwbd =        (/0.3      ,0.5    ,0.0    ,0.001  ,0.0001  ,0       ,0.000  ,0.001   ,0     ,0       ,0.01    ,0,0,0,0/)
    typicalvalue= (/1.2      ,0.7    ,0.1    ,0.01   ,0.1     ,0.7     ,0    ,0.1     ,1     ,0       ,0.1     ,0,0,0,0/)
    landmask=fw->LANDMASK
    cnt = dimsizes(name)

do idx=0,cnt-1
    field_2d=fw->$name(idx)$ ; sci


    print("Checking"+name(idx))
    dim=dimsizes(field_2d)
    do i=0,dim(1)-1
        do j=0,dim(2)-1
		if ((landmask(0,i,j).gt.0.5))then
          if (ismissing(field_2d(0,i,j))) then 
            print("i="+i+" j="+j+name(idx)+"="+field_2d(0,i,j))
            field_2d(0,i,j)=(/typicalvalue(idx)/)
          else
            if ((field_2d(0,i,j)).gt.upbd(idx).or.(field_2d(0,i,j).lt.lwbd(idx))) then
             print("i="+i+" j="+j+name(idx)+"="+field_2d(0,i,j))
             field_2d(0,i,j)=(/typicalvalue(idx)/)
            end if
          end if
        end if

		if ((landmask(0,i,j).lt.0.5))then
        if (name(idx).eq."XFVEG")
            if ((field_2d(0,i,j)).gt.0) then
             print("i="+i+" j="+j+name(idx)+"="+field_2d(0,i,j)+" XFVEG bigger than zero for land")
             field_2d(0,i,j)=0
            end if
        end if
        end if
        end do
    end do

   fw->$name(idx)$=field_2d ; sci
   delete(field_2d)
end do
end
