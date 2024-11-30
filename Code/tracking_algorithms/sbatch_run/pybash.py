##### viewing tracking algorithm results
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as ticker
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import matplotlib.gridspec as gridspec
import xarray as xr
import os; import time

# check=False
# dir='/mnt/lustre/koa/koastore/torri_group/air_directory/'
# data=xr.open_dataset(dir+'cm1r20.3/run/cm1out_test7tundra-7_062217.nc') #***
# true_time=data['time']
# parcel=xr.open_dataset(dir+'cm1r20.3/run/cm1out_pdata_test5tundra-7_062217.nc') #***
# times=data['time'].values/(1e9 * 60); times=times.astype(float);
# parcel=parcel.isel(time=times.astype(int)) 
dir='/mnt/lustre/koa/koastore/torri_group/air_directory/'
data=xr.open_dataset(dir+'cm1r20.3/run/cm1out_test7tundra-7_062217.nc') #***
times=data['time'].values/(1e9 * 60); times=times.astype(float);
parcel=xr.open_dataset(dir+'cm1r20.3/run/cm1out_pdata_test5tundra-7_062217.nc') #***
whereCL=xr.open_dataset(dir+'tracking_algorithms/whereCL_4_0622.nc').load() #***
whereCL=whereCL.isel(time=slice(0,len(data['time'])))

# out=xr.open_dataset(dir+'tracking_algorithms/trackout/parcel_tracking4tundra-7_062217.nc')['out_arr'].values;out=out.astype(object);out[:, [0,1,2,4,5]] = out[:, [0,1,2,4,5]].astype(int) #***
# save=xr.open_dataset(dir+'tracking_algorithms/trackout/parcel_tracking4tundra-7_062217.nc')['save_arr'].values;save=save.astype(object);save[:, [0,1,2,4,5]] = save[:, [0,1,2,4,5]].astype(int) #***

out=xr.open_dataset(dir+'tracking_algorithms/trackout/parcel_tracking_combined.nc')['out_arr'].values;out=out.astype(object);out[:, [0,1,2,4,5]] = out[:, [0,1,2,4,5]].astype(int) #***
save=xr.open_dataset(dir+'tracking_algorithms/trackout/parcel_tracking_combined.nc')['save_arr'].values;save=save.astype(object);save[:, [0,1,2,4,5]] = save[:, [0,1,2,4,5]].astype(int) #***

out_nz=out[~np.all(out == 0, axis=1)];print('list of first 10 SBZ parcels'); print(out_nz[:15])
save_nz=save[~np.all(save == 0, axis=1)];save_nz=save_nz[np.where(np.unique(save_nz[1:-1,0]))];print('list of first 10 ignored parcels');print(save_nz[:5])

###############################################################################
#remove duplicates
lst=[]
unique_values, counts = np.unique(out_nz[:,0], return_counts=True); duplicates = unique_values[counts > 1]
for elem in duplicates:
    idx = np.where(out_nz[:,0] == elem)[0] 
    extras=idx[np.where(out_nz[idx,5]!=np.min(out_nz[idx,5]))]
    lst.extend([x for x in extras])
mask=np.ones(len(out_nz), dtype=bool); mask[lst] = False
out_nz=out_nz[mask]; 
placeholder=out_nz.copy(); run=True
###############################################################################
print(f'there are a total of {len(out_nz)} SBZ parcels and {len(save_nz)} non-SBZ parcels')

# #################################################################################################################################
# if check==True:
#     list=[]
#     print('checking if all found SBZ parcels originate from CL')
#     for ind in range(0,out_nz.shape[0]):
#         x=parcel['x'].isel(time=out_nz[ind,4],xh=out_nz[ind,0]).values/1000;xf=data['xf'].values; which_x=np.searchsorted(xf,x)-1 
#         y=parcel['y'].isel(time=out_nz[ind,4],xh=out_nz[ind,0]).values/1000;yf=data['yf'].values; which_y=np.searchsorted(yf,y)-1 
#         # xbins=data['xf'].values; dx=xbins[1]-xbins[0]; which_x=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0].item() #faster
#         # ybins=data['yf'].values; dy=ybins[1]-ybins[0]; which_y=np.floor(y/dy).astype(int)+np.where(data['yf']==0)[0].item() #faster
#         z=parcel['z'].isel(time=out_nz[ind,4],xh=out_nz[ind,0]).values/1000; zf=data['zf'].values; which_z=np.searchsorted(zf,z)-1;
#         maxconv_x=whereCL['maxconv_x'].isel(time=out_nz[ind,4],y=which_y,z=which_z).values
#         list.append(any(np.isin(maxconv_x, np.arange(which_x-2,which_x+3))))
#     print(list[:20])
#     list=[]
#     print('checking if all found SBZ parcels hit LFC')
#     for ind in range(0,out_nz.shape[0]):
#         xloc=parcel['x'].isel(time=out_nz[ind,5],xh=out_nz[ind,0]).values/1000; yloc=parcel['y'].isel(time=out_nz[ind,5],xh=out_nz[ind,0]).values/1000
#         xf=data['xf'].values; which_x=np.searchsorted(xf,xloc)-1; yf=data['yf'].values; which_y=np.searchsorted(yf,yloc)-1; 
#         # xbins=data['xf'].values; dx=xbins[1]-xbins[0]; which_x=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0].item() #faster
#         # ybins=data['yf'].values; dy=ybins[1]-ybins[0]; which_y=np.floor(y/dy).astype(int)+np.where(data['yf']==0)[0].item() #faster
#         z=parcel['z'].isel(time=out_nz[ind,5],xh=out_nz[ind,0]).values/1000 
#         lfc=data['lfc'].isel(time=out_nz[ind,5],xh=which_x,yh=which_y).values/1000
#         list.append(z>=lfc)
#     print(list[:20])
# #################################################################################################################################

# out_min=np.round(np.min(out_nz[:,3]),3);out_max=np.round(np.max(out_nz[:,3]),3); print(f"CL zlev range is {out_min}:{out_max:.3f} km")
# out_mean=np.round(np.mean(out_nz[:,3]),3); print(f'mean CL zlev is {out_mean} km')




#Plotting Selected Parcel Individual Plots
dir='/mnt/lustre/koa/koastore/torri_group/air_directory/'
folder_path = '/mnt/lustre/koa/koastore/torri_group/air_directory/tracking_algorithms/trackout/plots/SBZ'
import os; os.makedirs(folder_path, exist_ok=True)
start_time=time.time()
for k in range(len(out_nz)):

    print(f'{k}/{len(out_nz)}')


    
    print(f'parcel number {out_nz[k:k+1,0]}')
    for xh in out_nz[k:k+1,0]:
        #plotting full z trajectory
        z=parcel['z'].isel(xh=xh).values/1000; 
        channel_aspect_ratio = 3
        plt.figure(figsize=(10, 10/channel_aspect_ratio)) 
        plt.plot(range(len(z)),z)

        #coloring line by x location
        lst=[]
        for t in range(0,len(data['time'])):
            x=parcel['x'].isel(time=t,xh=xh).values/1000; #xf=data['xf'].values; which_x=np.searchsorted(xf,x)-1; 
            xbins=data['xf'].values; dx=xbins[1]-xbins[0]; which_x=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0].item() #faster

            lst.append(which_x)
        colors = plt.cm.viridis  # Choose a colormap, here using 'viridis'
        norm = plt.Normalize(vmin=min(lst), vmax=max(lst))
        plt.scatter(range(len(z)), z, c=lst, cmap=colors, norm=norm,s=4)
        plt.colorbar(label='x grid')

        #data for CL parcel location
        ind=np.where(out_nz[:,0]==xh)[0][0]
        z_CL=parcel['z'].isel(time=out_nz[ind][4],xh=xh).values/1000;

        #data for LFC parcel location
        xloc=parcel['x'].isel(time=out_nz[ind,5],xh=out_nz[ind,0]).values/1000; yloc=parcel['y'].isel(time=out_nz[ind,5],xh=out_nz[ind,0]).values/1000
        xf=data['xf'].values; which_x=np.searchsorted(xf,xloc)-1; yf=data['yf'].values; which_y=np.searchsorted(yf,yloc)-1; 
        # xbins=data['xf'].values; dx=xbins[1]-xbins[0]; which_x=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0].item() #faster
        # ybins=data['yf'].values; dy=ybins[1]-ybins[0]; which_y=np.floor(y/dy).astype(int)+np.where(data['yf']==0)[0].item() #faster
        z=parcel['z'].isel(time=out_nz[ind,5],xh=out_nz[ind,0]).values/1000
        z_lfc=data['lfc'].isel(time=out_nz[ind,5],xh=which_x,yh=which_y).values/1000

        #plotting points for CL and LFC parcel location
        plt.scatter(out_nz[ind][4],z_CL,color='red',zorder=10,label='Convergence Max') #plotting max CL point
        plt.scatter(out_nz[ind][5],z,color='orange',zorder=10,label='LFC') #plotting LFC points
        plt.legend()

        #add some text with the velocity at the CL
        x_center = sum(plt.xlim()) / 2
        y_center = sum(plt.ylim()) / 2
        text='CL w: '+str(parcel['w'].isel(time=out_nz[ind][4],xh=xh).values)
        plt.text(x_center, y_center,text, ha='center', va='center')

        #add some text with the velocity at the LFC
        x_center = sum(plt.xlim()) / 3
        y_center = sum(plt.ylim()) / 3
        text='CL w: '+str(parcel['w'].isel(time=out_nz[ind][5],xh=xh).values)
        plt.text(x_center, y_center,text, ha='center', va='center')

        #plotting the line for LFC at all timesteps
        lst=[]
        for t in range(0,len(data['time'])):
            x=parcel['x'].isel(time=t,xh=xh).values/1000; xf=data['xf'].values; which_x=np.searchsorted(xf,x)-1; 
            y=parcel['y'].isel(time=t,xh=xh).values/1000; yf=data['yf'].values; which_y=np.searchsorted(yf,y)-1; 
            # xbins=data['xf'].values; dx=xbins[1]-xbins[0]; which_xf=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0].item() #faster
            # ybins=data['yf'].values; dy=ybins[1]-ybins[0]; which_yf=np.floor(y/dy).astype(int)+np.where(data['yf']==0)[0].item() #faster
            lfc=data['lfc'].isel(time=t,xh=which_x,yh=which_y).values/1000
            lst.append(lfc)
        plt.plot(np.arange(0, len(data['time'])), lst,color='purple',linewidth=0.75) #plotting LFC line

        #plotting all times the parcel is near the CL including where it doesn't go above LFC
        whereCL=xr.open_dataset(dir+'tracking_algorithms/whereCL_4_0622.nc')['maxconv_x'] #***
        for t in range(0,len(data['time'])):
            x=parcel['x'].isel(time=t,xh=xh).values/1000; xf=data['xf'].values; which_x=np.searchsorted(xf,x)-1; 
            y=parcel['y'].isel(time=t,xh=xh).values/1000; yf=data['yf'].values; which_y=np.searchsorted(yf,y)-1; 
            # xbins=data['xf'].values; dx=xbins[1]-xbins[0]; which_xf=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0].item() #faster
            # ybins=data['yf'].values; dy=ybins[1]-ybins[0]; which_yf=np.floor(y/dy).astype(int)+np.where(data['yf']==0)[0].item() #faster
            z=parcel['z'].isel(time=t,xh=xh).values/1000; zf=data['zf'].values; which_z=np.searchsorted(zf,z)-1; 
            
            if z<750/1000:
                maxconv_x=whereCL.isel(time=t,y=which_y,z=which_z);
                tf=np.any(np.isin(maxconv_x,np.arange(which_x-2,which_x+3)))
                if tf==True:
                    plt.scatter(t,z,color='red') #plotting additional max CL points

    plt.legend()            
    plt.savefig(os.path.join(folder_path, f"parcel_{out_nz[ind,0]}.png")) 
    plt.close()    
end_time = time.time(); elapsed_time = end_time - start_time; print(f"Total Elapsed Time: {elapsed_time} seconds") #15 minutes for 100 parcels #5 minutes for 20 parcels




#Plotting Selected non-SBZ Parcel Individual Plots
dir='/mnt/lustre/koa/koastore/torri_group/air_directory/'
folder_path = '/mnt/lustre/koa/koastore/torri_group/air_directory/tracking_algorithms/trackout/plots/non-SBZ'
import os; os.makedirs(folder_path, exist_ok=True)
start_time=time.time()
for k in range(len(save_nz)):

    print(f'{k}/{len(save_nz)}')


    
    print(f'parcel number {save_nz[k:k+1,0]}')
    for xh in save_nz[k:k+1,0]:
        #plotting full z trajectory
        z=parcel['z'].isel(xh=xh).values/1000; 
        channel_aspect_ratio = 3
        plt.figure(figsize=(10, 10/channel_aspect_ratio)) 
        plt.plot(range(len(z)),z)

        #coloring line by x location
        lst=[]
        for t in range(0,len(data['time'])):
            x=parcel['x'].isel(time=t,xh=xh).values/1000; #xf=data['xf'].values; which_x=np.searchsorted(xf,x)-1; 
            xbins=data['xf'].values; dx=xbins[1]-xbins[0]; which_x=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0].item() #faster

            lst.append(which_x)
        colors = plt.cm.viridis  # Choose a colormap, here using 'viridis'
        norm = plt.Normalize(vmin=min(lst), vmax=max(lst))
        plt.scatter(range(len(z)), z, c=lst, cmap=colors, norm=norm,s=4)
        plt.colorbar(label='x grid')

        #data for CL parcel location
        ind=np.where(save_nz[:,0]==xh)[0][0]
        z_CL=parcel['z'].isel(time=save_nz[ind][4],xh=xh).values/1000;

        #data for LFC parcel location
        xloc=parcel['x'].isel(time=save_nz[ind,5],xh=save_nz[ind,0]).values/1000; yloc=parcel['y'].isel(time=save_nz[ind,5],xh=save_nz[ind,0]).values/1000
        xf=data['xf'].values; which_x=np.searchsorted(xf,xloc)-1; yf=data['yf'].values; which_y=np.searchsorted(yf,yloc)-1; 
        # xbins=data['xf'].values; dx=xbins[1]-xbins[0]; which_x=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0].item() #faster
        # ybins=data['yf'].values; dy=ybins[1]-ybins[0]; which_y=np.floor(y/dy).astype(int)+np.where(data['yf']==0)[0].item() #faster
        z=parcel['z'].isel(time=save_nz[ind,5],xh=save_nz[ind,0]).values/1000
        z_lfc=data['lfc'].isel(time=save_nz[ind,5],xh=which_x,yh=which_y).values/1000

        #plotting points for CL and LFC parcel location
        plt.scatter(save_nz[ind][4],z_CL,color='red',zorder=10,label='Convergence Max') #plotting max CL point
        plt.scatter(save_nz[ind][5],z,color='orange',zorder=10,label='LFC') #plotting LFC points
        plt.legend()

        #add some text with the velocity at the CL
        x_center = sum(plt.xlim()) / 2
        y_center = sum(plt.ylim()) / 2
        text='CL w: '+str(parcel['w'].isel(time=save_nz[ind][4],xh=xh).values)
        plt.text(x_center, y_center,text, ha='center', va='center')

        #add some text with the velocity at the LFC
        x_center = sum(plt.xlim()) / 3
        y_center = sum(plt.ylim()) / 3
        text='CL w: '+str(parcel['w'].isel(time=save_nz[ind][5],xh=xh).values)
        plt.text(x_center, y_center,text, ha='center', va='center')

        #plotting the line for LFC at all timesteps
        lst=[]
        for t in range(0,len(data['time'])):
            x=parcel['x'].isel(time=t,xh=xh).values/1000; xf=data['xf'].values; which_x=np.searchsorted(xf,x)-1; 
            y=parcel['y'].isel(time=t,xh=xh).values/1000; yf=data['yf'].values; which_y=np.searchsorted(yf,y)-1; 
            # xbins=data['xf'].values; dx=xbins[1]-xbins[0]; which_xf=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0].item() #faster
            # ybins=data['yf'].values; dy=ybins[1]-ybins[0]; which_yf=np.floor(y/dy).astype(int)+np.where(data['yf']==0)[0].item() #faster
            lfc=data['lfc'].isel(time=t,xh=which_x,yh=which_y).values/1000
            lst.append(lfc)
        plt.plot(np.arange(0, len(data['time'])), lst,color='purple',linewidth=0.75) #plotting LFC line

        #plotting all times the parcel is near the CL including where it doesn't go above LFC
        whereCL=xr.open_dataset(dir+'tracking_algorithms/whereCL_4_0622.nc')['maxconv_x'] #***
        for t in range(0,len(data['time'])):
            x=parcel['x'].isel(time=t,xh=xh).values/1000; xf=data['xf'].values; which_x=np.searchsorted(xf,x)-1; 
            y=parcel['y'].isel(time=t,xh=xh).values/1000; yf=data['yf'].values; which_y=np.searchsorted(yf,y)-1; 
            # xbins=data['xf'].values; dx=xbins[1]-xbins[0]; which_xf=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0].item() #faster
            # ybins=data['yf'].values; dy=ybins[1]-ybins[0]; which_yf=np.floor(y/dy).astype(int)+np.where(data['yf']==0)[0].item() #faster
            z=parcel['z'].isel(time=t,xh=xh).values/1000; zf=data['zf'].values; which_z=np.searchsorted(zf,z)-1; 
            
            if z<750/1000:
                maxconv_x=whereCL.isel(time=t,y=which_y,z=which_z);
                tf=np.any(np.isin(maxconv_x,np.arange(which_x-2,which_x+3)))
                if tf==True:
                    plt.scatter(t,z,color='red') #plotting additional max CL points

    plt.legend()            
    plt.savefig(os.path.join(folder_path, f"parcel_{save_nz[ind,0]}.png")) 
    plt.close()    
end_time = time.time(); elapsed_time = end_time - start_time; print(f"Total Elapsed Time: {elapsed_time} seconds") #15 minutes for 100 parcels #5 minutes for 20 parcels