time = 1;
load(['3210_profil0d_tep.mat']);
[~,index_time] = min(abs(signal.time_axis.data-time));
Te = signal.data(index_time,:);
load(['3210_profil0d_rmx.mat']);
r = signal.data(index_time,:);

figure
plot(r,Te)
xlabel('Averaged radius [m]')
ylabel('Te [eV]')