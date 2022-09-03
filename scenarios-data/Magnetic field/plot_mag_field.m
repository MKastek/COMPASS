load(['magfield_3100.mat'],'Br','Bz','Bphi','r','z','time')


time_sel = 1;
[~, index_time] = min(abs(time - time_sel));


figure
pcolor(r,z,squeeze(Bphi(index_time,:,:)))
shading flat
xlabel('R [m]')
ylabel('R [m]')
title('B_{\phi}')
colorbar

figure
pcolor(r,z,squeeze(Br(index_time,:,:)))
shading flat
xlabel('R [m]')
ylabel('R [m]')
title('B_r')
colorbar


figure
pcolor(r,z,squeeze(Bz(index_time,:,:)))
shading flat
xlabel('R [m]')
ylabel('R [m]')
colorbar
title('B_z')