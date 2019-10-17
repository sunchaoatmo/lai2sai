load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
; ";" for description ";;" for debug.


begin
;    system("cp -f ./geo_em.d01.nc a.nc")
    fw=addfile("geo_em.d01_new.nc","w")
    
upoint=0
    landmask=fw->XLANDMASK
    fsand=fw->FR_SAND ; sci
    fclay=fw->FR_CLAY ; sci
    dim=dimsizes(fsand)
print(dim)
printVarSummary(fsand)
    do i=0,dim(2)-1
        do j=0,dim(3)-1
		if (landmask(0,i,j).eq.-1)then
          do k=0,dim(1)-1
             if (((fsand(0,k,i,j)).le.0).or.((fsand(0,k,i,j)).gt.100)) then
            ; if (((fsand(0,k,i,j)).gt.0).and.((fsand(0,k,i,j)).lt.100)) then
             print("i="+i+" j="+j+" k="+k+" fsand="+fsand(0,k,i,j)+" landmask="+landmask(0,i,j))
upoint=upoint+1
             end if
            ; if (((landmask(0,i,j)).gt.100).or.((fsand(0,k,i,j)).gt.100)) then
            ; print("i="+i+" j="+j+" k="+k+" fsand="+fsand(0,k,i,j)+" landmask="+landmask(0,i,j))
            ; end if
             if (((fclay(0,k,i,j)).le.0).or.((fclay(0,k,i,j)).gt.100)) then
             print("i="+i+" j="+j+" k="+k+" fsand="+fsand(0,k,i,j)+" landmask="+landmask(0,i,j))
upoint=upoint+1
             end if


          end do
            end if
        end do
    end do
print("undefied points= "+upoint)
end
