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
dir='/mnt/lustre/koa/koastore/torri_group/air_directory/'
data=xr.open_dataset(dir+'cm1r20.3/run/cm1out_test7tundra-7_062217.nc') #***
true_time=data['time']
parcel=xr.open_dataset(dir+'cm1r20.3/run/cm1out_pdata_test5tundra-7_062217.nc') #***
times=data['time'].values/(1e9 * 60); times=times.astype(float);

#Restricts the timesteps of the data from timesteps0 to 140
data=data.isel(time=np.arange(0,140+1))
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


#Job Array

num_jobs=30 #how many total jobs are being run? i.e. array=1-100 ==> num_jobs=100 #***
#limited by num_parcels

job_id = int(os.environ.get('SLURM_ARRAY_TASK_ID', 0)) #this is the current SBATCH job id
if job_id==0: job_id=1
num_parcels=len(data['time']) #total number of parcels
job_range = num_parcels//num_jobs #number of parcels per job 

# Calculate start and end based on job_id
start_job = (job_id - 1) * job_range
end_job = start_job + job_range
if job_id==num_jobs: end_job=num_parcels-1
print(f'running for times {start_job}-{end_job}')

data=data.isel(time=slice(start_job,end_job))
parcel=parcel.isel(time=slice(start_job,end_job))



#Making vertical profile of cloudy updrafts for single timestep
def single_profile(t,var,type):
    #thresholds
    wthresh=0
    qcqithresh=1e-6

    nt=len(data['time'])
    if np.mod(t,20)==0: print(f'current time is {t}/{nt}') 
        
    #get qc and interpolated w 
    variable='w'; w_data=data[variable].isel(time=t) #get w data
    w_data=w_data.interp(zf=data['zh']) #interpolation w data z coordinate from zh to zf
    variable='qc'; qc_data=data[variable].isel(time=t) # get qc data
    variable='qi'; qi_data=data[variable].isel(time=t) # get qc data
    qc_plus_qi=qc_data+qi_data

    # finds regions that match the threshold
    if type=="general":
        cloudy_updraft=np.where((w_data>=wthresh)) #uncomment for "general updraft"
    elif type=='cloudy': 
        cloudy_updraft=np.where((w_data>=wthresh) & (qc_plus_qi>=qcqithresh)) #uncomment for "cloudy updraft" 
    
    #creates profile storage and adds z column    
    zhs=data['zh'].values
    profile_array=np.zeros((len(zhs), 3)) #column 1: var, column 2: counter, column 3: list of zhs
    profile_array[:,2]=zhs

    #runs through each position and adds to profile
    for position in zip(*cloudy_updraft):
        #loads data of variable of interest to plot (w,qv,qc,th)
        if var=="w": #for w use interpolated w data
            var_data=w_data.isel(zh=position[0],yh=position[1],xh=position[2]).values 
        else:
            var_data=data[var].isel(time=t,zh=position[0],yh=position[1],xh=position[2]).values
            
        #converts qv and qc from kg/kg=>g/kg
        if var in ['qv','qc','qi']:
            var_data*=1000
            
        #add to profile array
        profile_array[position[0],0]+=var_data #adds data to first column
        profile_array[position[0],1]+=1 #adds +1 counter to 2nd column
    return profile_array

#Produce final profiles for each variable
def final_profile(var,type):
    t=0;profile=single_profile(t,var,type).copy() #makes profile for time 0
    for t in np.arange(1,len(data['time'])):
        profile[:,0:2]+=single_profile(t,var,type)[:,0:2].copy() #adds profile to previous profile (applies only to data + counter column) #******* this might be the issue
        # if t==10: break #TESTING***
    return profile


#Final_Profile Function

yes_run=False
yes_run=True #uncomment if running

if yes_run==True: 
    dim='1km' 
    # dim='250m'
    
    for type in ["general","cloudy"]:
        print(f'currently on type {type}')
        
        vars=['w','qv','qc','qi','th','buoyancy']
        # vars=['qc','th'] #TESTING***
        for var in vars:
            print(f'working on {var}')
            globals()[f"profile_{var}"]=final_profile(var,type)
        print('done')
        
        #Saving eulerian_profiles
        import h5py
        if dim=='1km':
            if type == "general":
                output_file = dir+f'tracking_algorithms/plots/job_out/1km_general_eulerian_profiles_{job_id}_w>=0.h5' 
            elif type == "cloudy":
                output_file = dir+f'tracking_algorithms/plots/job_out/1km_cloudy_eulerian_profiles_{job_id}w>=0.h5'
        
        if dim=='250m':
            if type == "general":
                output_file = dir+f'tracking_algorithms/plots/job_out/250m_general_eulerian_profiles_{job_id}w>=0.h5' 
            elif type == "cloudy":
                output_file = dir+f'tracking_algorithms/plots/job_out/250m_cloudy_eulerian_profiles_{job_id}w>=0.h5' 
        
        with h5py.File(output_file, 'w') as f:
            f.create_dataset('profile_w', data=profile_w, compression="gzip")
            f.create_dataset('profile_qv', data=profile_qv, compression="gzip")
            f.create_dataset('profile_qc', data=profile_qc, compression="gzip")
            f.create_dataset('profile_qi', data=profile_qi, compression="gzip")
            f.create_dataset('profile_th', data=profile_th, compression="gzip")
            f.create_dataset('profile_buoyancy', data=profile_buoyancy, compression="gzip")