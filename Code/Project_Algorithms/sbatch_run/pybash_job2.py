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


import sys
dir2='/mnt/lustre/koa/koastore/torri_group/air_directory/DCI-Project/'
path=dir2+'../Functions/'
sys.path.append(path)

import NumericalFunctions
from NumericalFunctions import * # import NumericalFunctions 
import PlottingFunctions
from PlottingFunctions import * # import PlottingFunctions


# # Get all functions in NumericalFunctions
# import inspect
# functions = [f[0] for f in inspect.getmembers(NumericalFunctions, inspect.isfunction)]
# functions


# Reading Back Data Later
##############
import h5py
dir2=dir+'Project_Algorithms/Lagrangian_Binary_Array/job_array/'
with h5py.File(dir2+'lagrangian_binary_array.h5', 'r') as f:
    # Load the dataset by its name
    A_g = f['A_g'][:]
    A_c = f['A_c'][:]
    Z = f['Z'][:]
    Y = f['Y'][:]
    X = f['X'][:]

# #Making Time Matrix
# rows, cols = A.shape[0], A.shape[1]
# T = np.arange(rows).reshape(-1, 1) * np.ones((1, cols), dtype=int)

#job array setup #UNCOMMENT IF USING JOB_ARRAY
num_jobs=60 #how many total jobs are being run? i.e. array=1-100 ==> num_jobs=100 #***
job_id = int(os.environ.get('SLURM_ARRAY_TASK_ID', 0)) #this is the current SBATCH job id
if job_id==0: job_id=30
    
num_parcels=len(data['time']) #total num of variables
job_range = num_parcels//num_jobs #number of parcels per job 
start_job = (job_id - 1) * job_range
end_job = start_job + job_range
if job_id==num_jobs: end_job=num_parcels-1


#FOR ENTRAINMENT THE PREVIOUS TIMESTEP IS ALWAYS NEEDED, SO SLICED WILL CAUSE WRAP AROUND DATA
#INSTEAD NP.WHERE RESULTS MUST BE SUBSETTED
# data=data.isel(time=slice(start_job,end_job))
# parcel=parcel.isel(time=slice(start_job,end_job))

# #SLICING LAGRANGIAN BINARY ARRAY
# A_g=A_g[slice(start_job,end_job)]
# A_c=A_c[slice(start_job,end_job)]
# Z=Z[slice(start_job,end_job)]
# Y=Y[slice(start_job,end_job)]
# X=X[slice(start_job,end_job)]

#constants
Cp=1004 #Jkg-1K-1
Cv=717 #Jkg-1K-1
Rd=Cp-Cv #Jkg-1K-1
eps=0.608

Lx=data['xf'][-1].item()-data['xf'][0].item() #x length (km)
Ly=data['yf'][-1].item()-data['yf'][0].item() #y length (km)
Np=len(parcel['xh']) #number of lagrangian parcles
dt=data['time'][1].item()/1e9 #sec
dx=(data['xf'][1].item()-data['xf'][0].item())*1e3 #meters
dy=(data['yf'][1].item()-data['yf'][0].item())*1e3 #meters
xs=data['xf'].values*1000
ys=data['yf'].values*1000
zs=data['zf'].values*1000

def zf(z):
    k=z #z is the # level of z
    out=data['zf'].values[k]*1000
    return out
# def rho(x,y,z,t):
#     p=data['prs'].isel(xh=x,yh=y,zh=z,time=t).item()
#     p0=101325 #Pa
#     theta=data['th'].isel(xh=x,yh=y,zh=z,time=t).item()
#     T=theta*(p/p0)**(Rd/Cp)
#     qv=data['qv'].isel(xh=x,yh=y,zh=z,time=t).item()
#     # Tv=T*(1+eps*qv)
#     Tv=T*(eps+qv)/(eps*(1+qv))
#     rho = p/(Rd*Tv)
#     out=rho
#     return out
rho_data=data['rho'].data
def rho(x,y,z,t):
    # out=data['rho'].isel(xh=x,yh=y,zh=z,time=t).item()
    out=rho_data[t,z,y,x]
    return out
def m(t):
    m=0
    #triple sum
    for k in range(len('zh')):
        for j in range(len('yh')):
            for i in range(len('xh')):
                rho_out=rho(i,j,k,t)
                m+=rho_out*(zf(k+1)-zf(k))
    #triple sum
    m=m*dx*dy/Np
    out=m
    return out


def ed3d(A,t,z,y,x,type):
    #Get Z Locations
    zs=Z[t,:]
    ys=Y[t,:]
    xs=X[t,:]
    
    #Essential A_t-A_(t-1)
    D=A[t,:]-A[t-1,:]
    
    #Essentially the I function
    zyx_ind=np.where((zs==z)&(ys==y)&(xs==x))
    A_z=D[zyx_ind]
    
    #Esentially the H function

    if type=='e':
        A_z[A_z<0]=0 #entrainment
    if type=='d':
        A_z[A_z>0]=0 #detrainment

    #Essentially the sumnation
    A_sum=np.sum(A_z)

    if type=='d': 
        A_sum*=-1

    #CONSTANT
    ############
    m_out=m(t)
    dz=zf(z+1)-zf(z);dy=1000;dx=1000
    constant=(m_out/dx/dy/dz/dt) 
    # constant=1
    A_sum*=constant
    return A_sum

#LOADING VARIABLES
if 'emptylike' not in globals():
    print('loading neccessary variables')
    variable='w'; w_data=data[variable] #get w data
    w_data=w_data.interp(zf=data['zh']).data #interpolation w data z coordinate from zh to zf
    # variable='qv'; qv_data=data[variable].data # get qc data
    variable='qc'; qc_data=data[variable].data # get qc data
    variable='qi'; qi_data=data[variable].data # get qc data
    qc_plus_qi=qc_data+qi_data

    print('done loading')
    emptylike=True


##############################################################################################
#JOB ARRAY FOR SUBSETTING NP.WHERE OUTPUTS
def job_subset_where(where):
    array1, array2, array3, array4 = where
    mask = (array1 >= start_job) & (array1 < end_job)
    filtered_data = tuple(arr[mask] for arr in where) #USE IN INITIALIZING FULL ARRAY EACH TIME
    return filtered_data


#SET UP TO RUN WITH JOB_ARRAY
calc_entrain=True
calc_detrain=True

#creates 2d storage array

# tlen=len(data['time'])
tlen=end_job-start_job
zlen=len(data['zh'])
ylen=len(data['yh'])
xlen=len(data['xh'])

profile_array_e_g=np.zeros((tlen,zlen,ylen,xlen))
profile_array_d_g=np.zeros((tlen,zlen,ylen,xlen))
profile_array_e_c=np.zeros((tlen,zlen,ylen,xlen))
profile_array_d_c=np.zeros((tlen,zlen,ylen,xlen))
    
#Adding to Profile Array
# import itertools
# ts = range(0, 141)  # ts from 0 to 140
# zs = range(0, 34)   # zs from 0 to 34
# for count, (t, z) in enumerate(itertools.product(ts, zs)):

#GENERAL UPDRAFTS

#ENTRAINMENT
if calc_entrain==True:
    w_thresh1=0.1
    indices=np.where((w_data>=w_thresh1))
    indices_e=job_subset_where(indices) #USE FOR JOB_ARRAY ONLY***
    if np.any(indices_e)==True:
        tmin=np.min(indices_e[0]) #USE FOR JOB_ARRAY ONLY***
    else: 
        tmin=0
    for count, (t, z, y, x) in enumerate(zip(*indices_e)):
        if np.mod(count,10000)==0: print(f'{count*100/len(indices_e[0]):.2f}%')
        
        A_sum_e_g=ed3d(A_g,t,z,y,x,type='e')
        # profile_array_e_g[t,z,y,x]+=A_sum_e_g
        profile_array_e_g[t-tmin,z,y,x]+=A_sum_e_g #CORRECT FOR JOB_ARRAY

#DETRAINMENT
if calc_detrain==True:
    w_thresh1=0.1
    indices=np.where((w_data<w_thresh1)) #NEGATION OF THRESHOLD
    indices_d=job_subset_where(indices) #USE FOR JOB_ARRAY ONLY***
    if np.any(indices_d)==True:
        tmin=np.min(indices_d[0]) #USE FOR JOB_ARRAY ONLY***
    else: 
        tmin=0
    for count, (t, z, y, x) in enumerate(zip(*indices_d)):
        if np.mod(count,10000)==0: print(f'{count*100/len(indices_d[0]):.2f}%')
        
        A_sum_d_g=ed3d(A_g,t,z,y,x,type='d')
        # profile_array_d_g[t,z,y,x]+=A_sum_d_g
        profile_array_d_g[t-tmin,z,y,x]+=A_sum_d_g #CORRECT FOR JOB_ARRAY


#CLOUDY UPDRAFTS

#ENTRAINMENT
if calc_entrain==True:
    w_thresh2=0.5
    qcqi_thresh=1e-6
    indices=np.where((w_data>=w_thresh2)&(qc_plus_qi>=qcqi_thresh))
    indices_e=job_subset_where(indices) #USE FOR JOB_ARRAY ONLY***
    if np.any(indices_e)==True:
        tmin=np.min(indices_e[0]) #USE FOR JOB_ARRAY ONLY***
    else: 
        tmin=0
    for count, (t, z, y, x) in enumerate(zip(*indices_e)):
        if np.mod(count,10000)==0: print(f'{count*100/len(indices_e[0]):.2f}%')
            
        A_sum_e_c=ed3d(A_c,t,z,y,x,type='e')
        # profile_array_e_c[t,z,y,x]+=A_sum_e_c
        profile_array_e_c[t-tmin,z,y,x]+=A_sum_e_c #CORRECT FOR JOB_ARRAY


#DETRAINMENT
if calc_detrain==True:
    w_thresh2=0.5
    qcqi_thresh=1e-6
    indices=np.where((w_data<w_thresh2)|(qc_plus_qi<qcqi_thresh))
    indices_d=job_subset_where(indices) #USE FOR JOB_ARRAY ONLY***
    if np.any(indices_d)==True:
        tmin=np.min(indices_d[0]) #USE FOR JOB_ARRAY ONLY***
    else: 
        tmin=0
    for count, (t, z, y, x) in enumerate(zip(*indices_d)):
        if np.mod(count,10000)==0: print(f'{count*100/len(indices_d[0]):.2f}%')
        
        A_sum_d_c=ed3d(A_c,t,z,y,x,type='d')
        # profile_array_d_c[t,z,y,x]+=A_sum_d_c
        profile_array_d_c[t-tmin,z,y,x]+=A_sum_d_c #CORRECT FOR JOB_ARRAY


#SAVING
if calc_entrain==True:
    dir3=dir+f'Project_Algorithms/Entrainment/job_out/3D_entrainment_profiles{job_id}.h5'
    with h5py.File(dir3, "w") as h5f:
        h5f.create_dataset("profile_array_e_g", data=profile_array_e_g)
        h5f.create_dataset("profile_array_e_c", data=profile_array_e_c)
if calc_detrain==True:
    dir3=dir+f'Project_Algorithms/Entrainment/job_out/3D_detrainment_profiles{job_id}.h5'
    with h5py.File(dir3, "w") as h5f:
        h5f.create_dataset("profile_array_d_g", data=profile_array_d_g)
        h5f.create_dataset("profile_array_d_c", data=profile_array_d_c)