## Cold pool tracking (step0) by Mingyue Tang and Abraham Roseman
## step 0 for calculating total precipitation mixed ratio (QP) and density potential temperature
## (kerry emanual 1994 (torri 2015 check mingyues manuscript) density theta minus horizontal average at every layer)
# 4-D BFS


# In[ ]:


####### read data #################################################
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as ticker
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import matplotlib.gridspec as gridspec
import xarray as xr
import os; import time as timer

check=False
dir='/mnt/lustre/koa/koastore/torri_group/air_directory/'
data=xr.open_dataset(dir+'cm1r20.3/run/cm1out_test7tundra-7_062217.nc') #***
true_time=data['time']
parcel=xr.open_dataset(dir+'cm1r20.3/run/cm1out_pdata_test5tundra-7_062217.nc') #***
times=data['time'].values/(1e9 * 60); times=times.astype(float);
parcel=parcel.isel(time=times.astype(int)) 

#getting mixed ratio variable names
data_vars=list(data.data_vars)
mixedratios=[var for var in data_vars if var.startswith('q') and len(var)==2]
for var in mixedratios:
    print(var)


# In[ ]:


#picking out time range of interest
time1=7200 #when first cold pools start forming shortly after 1sst SBZ begins
time2=30900 #when 1st SBZ hits right boundary
#time1=83700 #future 2nd SBZ phase
#time2=112800 #future 2nd SBZ phase

time1=int(time1/60/5) #convert seconds to timesteps
time2=int(time2/60/5) #convert seconds to timesteps
data=data.isel(time=np.arange(time1,time2))


# In[ ]:


start_time = timer.time()
####### calculating QP #################################################
#creating zeroed out arrays to fill
print('making zeroed out xarray and added mixed ratios')
shape=list(data['qv'].shape)
QP=np.ndarray((shape[0], shape[1], shape[2], shape[3]))
shape=list(data['th'].shape)
DTPAnomaly=np.ndarray((shape[0], shape[1], shape[2], shape[3]))

for t in np.arange(QP.shape[0]):
    if np.mod(t,50)==0: print(f'{t}/{QP.shape[0]-1} timesteps')

    ####### calculating QP #################################################
    for var in mixedratios:
        QP[t,:,:,:]+=data[var].isel(time=t).values
    ####### calculating DTPAnomaly #################################################
    Rd = 287.1 #J kg-1 K-1 (dry air specific gas constant)
    Rv = 461.5 #J kg-1 K-1 (water vapor specific gas constant)
    Qv=data['qv'].isel(time=t)
    Qr=data['qr'].isel(time=t)
    Qc=data['qc'].isel(time=t)
    Ql=Qr+Qc
    Th=data['th'].isel(time=t)
    DTPAnomaly[t,:,:,:]=Th*(1+(Rv/Rd-1)*Qv - Ql)
    broadcast_mean = np.nanmean(DTPAnomaly[t,:,:,:], axis=(-2, -1), keepdims=True)
    DTPAnomaly[t,:,:,:]-=broadcast_mean
print('done')

# In[ ]:


# ####### combining datasets into single xarray object #################################################

####### calculating QP to nc file #################################################
QP_nc = xr.DataArray(QP, dims=('time', 'zh', 'yh', 'xh'))
# Assign coordinates
QP_nc['time'] = data['qv']['time']
QP_nc['zh'] = data['qv']['zh']
QP_nc['yh'] = data['qv']['yh']
QP_nc['xh'] = data['qv']['xh']

# Assign attributes
QP_nc.name = 'QP'
QP_nc.attrs['long_name'] = "water vapor mixing ratio"
QP_nc.attrs['units'] = "kg/kg"

####### calculating DTPAnomaly to nc file #################################################
DTPAnomaly_nc = xr.DataArray(DTPAnomaly, dims=('time', 'zh', 'yh', 'xh'))
# Assign coordinates
DTPAnomaly_nc['time'] = data['th']['time']
DTPAnomaly_nc['zh'] = data['th']['zh']
DTPAnomaly_nc['yh'] = data['th']['yh']
DTPAnomaly_nc['xh'] = data['th']['xh']

# Assign attributes
DTPAnomaly_nc.name = 'DPTAnomaly'
DTPAnomaly_nc.attrs['long_name'] = 'density potential temperature anomaly'
DTPAnomaly_nc.attrs['units'] = "Kkg/kg"

####### combining variables into single nc file #################################################
output=xr.merge([QP_nc, DTPAnomaly_nc])

from datetime import datetime
date=datetime.now()
date=f'{date.strftime("%y")}{date.strftime("%m")}{date.strftime("%d")}'
output.to_netcdf(f'{dir}cold pool tracking/QPDPTAnomaly_{date}.nc/')
# xr.open_dataset(f'{dir}cold pool tracking/QPDTPAnomaly.nc') 

end_time = timer.time(); elapsed_time = end_time - start_time; print(f"Total Elapsed Time: {elapsed_time} seconds")
#576t34z100y512x 3 minutes