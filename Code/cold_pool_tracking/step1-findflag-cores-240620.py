## Cold pool tracking (step1-4) by Mingyue Tang
## step 1 for tracking cold pools
## already calculate density potential temperature
# 4-D BFS 


# In[ ]:


import xarray as xr
import numpy as np
import glob
import torch
import time as timer


# In[49]:


### Sensitive thresholds ########################################
Nz_sc    = 10   # bottom 10 layers for PBL
qp_thr_1 = 1.0/1000 #kg/kg   #*** 
cp_thr_1 = 1.0 #K(kg/kg)       #***

####### read data #################################################
path = '/mnt/lustre/koa/koastore/torri_group/air_directory/cold pool tracking/'
path_3D = path+'*'
list_of_paths = glob.glob(path_3D)
list_of_paths.sort()

nc_path_0 = [path for path in list_of_paths if path.split('/')[-1].startswith('QPDPTAnomaly')][0]
ncfile_0 = xr.open_dataset(nc_path_0)
x = ncfile_0["xh"] #coordinates from euler (xh) also background wind speed
y = ncfile_0["yh"] 
z = ncfile_0["zh"] 
z_sc = z[:Nz_sc]  #Only select PBL
nt = len(ncfile_0['time']) # nt = len(list_of_paths) OLD
time = range(0, nt, 1)

x_grd = range(0, len(x), 1)
y_grd = range(0, len(y), 1)
z_grd = range(0, len(z_sc), 1)  

################# Return variables ########################################
flag_return  = np.ndarray( shape=(len(time), len(z), len(y_grd), len(x_grd)), dtype=int)
cores_tzyx_gn = torch.zeros(0, 5) 


# In[56]:


################ Find cores at every time step 06/20/2022 ################### ******
start_time=timer.time()
for prnt,it in enumerate(range(nt)):
    if np.mod(prnt,25)==0: print(f'current time step: {prnt}/{nt}')
    # ncapth_i = list_of_paths[it] OLD
    ncfile = ncfile_0.isel(time=it) # ncfile = xr.open_dataset(ncapth_i) OLD
    flag_return_i = np.ndarray( shape=( len(z), len(y_grd), len(x_grd)), dtype=int)

    thr_a = ncfile["DPTAnomaly"] [:Nz_sc]  # PBL 10 levels
    qp    = ncfile["QP"] [:Nz_sc]          # PBL 10 levels

    ## Flag cold cores
    sum_tzyx =  len(z)*len(y)*len(x)
    which_cold_core = np.where( (thr_a <= -cp_thr_1) & (qp >= qp_thr_1) )
    flag_return_i[which_cold_core]  = 1  
    flag_return[it,:,:,:] = flag_return_i[:,:,:]

    ######## add flag_return as tensor to original tensor at every time step 06/23/2022 ########
    cores_yzx_gn_it = torch.zeros(len(which_cold_core[0]), 5) 
    cores_yzx_gn_it[:,0] = it
    for i in range(len(which_cold_core[0])):
        for j in range(3):
            cores_yzx_gn_it[i,j+1] = which_cold_core[j][i]

    cores_tzyx_gn = torch.cat([cores_tzyx_gn, cores_yzx_gn_it], dim=0) 
end_time = timer.time(); elapsed_time = end_time - start_time; print(f"Total Elapsed Time: {elapsed_time} seconds")


# In[ ]:


######## save flag_return & gn_return  ######################################################
# ds = xr.Dataset(
#     data_vars = dict(
#         flag_return = (['time','z','y','x'], flag_return), 
#     ),
#     coords = dict(
#         x = x.values,
#         y = y.values,
#         z = z.values,
#         time = time,
#     ),
#     attrs=dict(description="flag cold cores without searching clusters"),
# )

from datetime import datetime
date=datetime.now()
date=f'{date.strftime("%y")}{date.strftime("%m")}{date.strftime("%d")}'
# ds.to_netcdf(path+f'step1-FindFlag_Cores-{date}.nc')

######## save flag_return as tensor ######################################################
torch.save(cores_tzyx_gn, path+f'step1-findflag_cores_tzyx_tensor-{date}.pt')

