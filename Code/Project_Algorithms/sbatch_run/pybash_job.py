#Loading in Packages and Data

#Importing Packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as ticker
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import ScalarFormatter
import matplotlib.gridspec as gridspec
import xarray as xr
import os; import time
import pickle
import h5py
###############################################################
def coefs(coefficients,degree):
    coef=coefficients
    coefs=""
    for n in range(degree, -1, -1):
        string=f"({coefficients[len(coef)-(n+1)]:.1e})"
        coefs+=string + f"x^{n}"
        if n != 0:
            coefs+=" + "
    return coefs
###############################################################

#Importing Model Data
check=False
dir='/mnt/lustre/koa/koastore/torri_group/air_directory/DCI-Project/'
netCDF=xr.open_dataset(dir+'../cm1r20.3/run/cm1out_test7tundra-7_062217.nc') #***
true_time=netCDF['time']
parcel=xr.open_dataset(dir+'../cm1r20.3/run/cm1out_pdata_test5tundra-7_062217.nc') #***
times=netCDF['time'].values/(1e9 * 60); times=times.astype(float);

#Restricts the timesteps of the data from timesteps0 to 140
data=netCDF.isel(time=np.arange(0,140+1))
parcel=parcel.isel(time=np.arange(0,140+1))

# #uncomment if using 250m data
# #Importing Model Data
# check=False
# dir2='/home/air673/koa_scratch/'
# data=xr.open_dataset(dir2+'cm1out_250m.nc') #***
# parcel=xr.open_dataset(dir2+'cm1out_pdata_250m.nc') #***

# # Restricts the timesteps of the data from timesteps0 to 140
# data=data.isel(time=np.arange(0,400+1))
# parcel=parcel.isel(time=np.arange(0,400+1))

#job array setup
num_jobs=30 #how many total jobs are being run? i.e. array=1-100 ==> num_jobs=100 #***
job_id = int(os.environ.get('SLURM_ARRAY_TASK_ID', 0)) #this is the current SBATCH job id
if job_id==0: job_id=1

num_parcels=len(parcel['xh']) #total num of variables
job_range = num_parcels//num_jobs #number of parcels per job 
start_job = (job_id - 1) * job_range
end_job = start_job + job_range
if job_id==num_jobs: end_job=num_parcels-1

parcel=parcel.isel(xh=slice(start_job,end_job))




# Loading Important Variables
##############
if 'emptylike' not in globals():
    print('loading neccessary variables')
    variable='w'; w_data=data[variable] #get w data
    w_data=w_data.interp(zf=data['zh']).data #interpolation w data z coordinate from zh to zf
    variable='qv'; qv_data=data[variable].data # get qc data
    variable='qc'; qc_data=data[variable].data # get qc data
    variable='qi'; qi_data=data[variable].data # get qc data
    qc_plus_qi=qc_data+qi_data
    print('done')
    empty_like=True




#Eulerian General Cloudy Updrafts
##############
w_thresh1=0.1
w_thresh2=0.5
qcqi_thresh=1e-6
D=np.zeros_like(w_data) 
where1g=np.where((w_data>=w_thresh1)&(qc_plus_qi<qcqi_thresh))
where1c=np.where((w_data>=w_thresh2)&(qc_plus_qi>=qcqi_thresh))
where1c

#Lagrangian Position Arrays
##############
def grid_location(x,y,z): #faster
    #finding xf and yf
    ybins=data['yf'].values*1000; dy=ybins[1]-ybins[0] #1000
    xbins=data['xf'].values*1000; dx=xbins[1]-xbins[0] #1000
    dy=np.round(dy);dx=np.round(dx)

    #digitizing
    zf=data['zf'].values*1000; which_zh=np.searchsorted(zf,z)-1; which_zh=np.where(which_zh == -1, 0, which_zh) #finds which z layer parcel in 
    if which_zh.ndim==0:
        which_zh=np.array([which_zh])
    which_yh=np.floor(y/dy).astype(int)+np.where(data['yf']==0)[0]
    which_xh=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0]

    #fixing boundaries
    which_zh[np.where(which_zh==len(data['zh']))]-=1
    which_yh[np.where(which_yh==len(data['yh']))]-=1
    which_xh[np.where(which_xh==len(data['xh']))]-=1
    return which_zh,which_yh,which_xh
x=parcel['x'].data;y=parcel['y'].data;z=parcel['z'].data
Z,Y,X=grid_location(x,y,z)




#Calculating Lagrangian Binary Array 
############################

A_g=np.zeros_like(Z)
A_c=np.zeros_like(Z)

# max_count= 1 #TESTING
max_count = len(parcel['xh'])

start_time = time.time()    
for count,p in enumerate(np.arange(A_g.shape[1])):
    #CONDITION FOR GENERAL UPDRAFT BINARY ARRAY
    condz=Z[where1g[0],p]==where1g[1]
    condy=Y[where1g[0],p]==where1g[2]
    condx=X[where1g[0],p]==where1g[3]
    where2g=np.where(condz&condy&condx)

    #find (t,p) to index
    t_inds=where1g[0][where2g]
    p_ind=p
    
    #indexing T(t,p)
    A_g[t_inds,p]=1

    #CONDITION FOR CLOUDY UPDRAFT BINARY ARRAY
    condz=Z[where1c[0],p]==where1c[1]
    condy=Y[where1c[0],p]==where1c[2]
    condx=X[where1c[0],p]==where1c[3]
    where2c=np.where(condz&condy&condx)

    #find (t,p) to index
    t_inds=where1c[0][where2c]
    p_ind=p
    
    #indexing T(t,p)
    A_c[t_inds,p]=1

    #PRINT STATEMENTS
    if np.mod(count,1000)==0: print(f'p={p}/{A_g.shape[1]}\n')
    if count==max_count: break #TESTING

end_time = time.time()
print(f"Time taken: {end_time - start_time:.6f} seconds")
# secs_per_p=(end_time-start_time)/max_count #seconds per parcel
# tot_secs=secs_per_p*len(parcel['xh']) #seconds for 1.25e5 parcels
# tot_mins=tot_secs/60**2
# tot_mins #19 mins calculated from 566 parcels

# Saving Data
##############
import h5py
with h5py.File(dir+f'lagrangian_binary_threshold_job{job_id}.h5', 'w') as f:
    # Save the array as a variable in the file
    f.create_dataset('A_g', data=A_g) #binary array for general updraft (w>=0.1)
    f.create_dataset('A_c', data=A_c) #binary array for general updraft (w>=0.5 & qc+qi>=1e-6)
    
    f.create_dataset('Z', data=Z)
    f.create_dataset('Y', data=Y)
    f.create_dataset('X', data=X)