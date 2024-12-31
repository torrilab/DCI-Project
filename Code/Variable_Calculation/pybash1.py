#250 M DATA
###########################################################################################

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
dir='/home/air673/koa_scratch/'

netCDF=xr.open_dataset(dir+'cm1out.nc') #***
res='250m'

#LOAD VARIABLES
################################################################################
def load_vars(data):
    
    ###########################
    # Equivalent Potential Temperature (theta_e)
    # surface_prs=data['prs'].mean(dim=("time",'yh','xh')); surface_prs=surface_prs[0]
    
    
    print('PRESSURE VARIABLES'); ################################# PRESSURE VARIABLES
    p0=1e5
    P=data['prs'].data
    
    # print('MIXING RATIO'); ################################# MIXING RATIO
    qv=data['qv'].data
    qt=(data['qv']+data['qc']+data['qr']+data['qi']+data['qs']+data['qg']).data #total mixing ratio
    
    # print('THERMODYNAMICS'); ################################# THERMODYNAMICS
    Rd=287.04
    Rv=461.5
    Cpd=1005.7 #+-2.5
    Cpv=1870 #+-25
    Cpl=4190 #+-30
    Lv0=2.501e6
    def Lv(T): #Kirchoff's formula L_i,ii= L_i,ii0+(Cpii-Cpi)*(T-273.15)
        Llv=Lv0+(Cpv-Cpl)*(T-273.15) #should it be Cpl. is Cl the same?***
        return Llv
    
    # print('TEMPERATURE'); ################################# TEMPERATURE
    theta=data['th'].data
    T=theta*(P/p0)**(Rd/Cpd)
    
    # print('RELATIVE HUMIDITY'); ################################# RELATIVE HUMIDITY
    eps=0.622
    #qv=eps*(e/(P-e)) ==> e = qv*P/(eps+qv)
    e=qv*P/(qv+eps)
    Pd=P-e #P=Pd+e ==> Pd=P-e

    e_s0=611
    T0=273.15
    inner=(Lv(T)/Rv)*((1/T0)-(1/T))
    e_s=e_s0*np.exp(inner)
    H = e/e_s ########

    return P, p0, qv, qt, Rd, Rv, Cpd, Cpv, Cpl, Lv, T, e, Pd, e_s, H

def make_theta_e(P, p0, qv, qt, Rd, Rv, Cpd, Cpv, Cpl, Lv, T, e, Pd, e_s, H):
    divisor=(Cpd+Cpl*qt)
    theta_e=(T*(p0/Pd)**(Rd/divisor))*(H**(-qv*Rv/divisor))*np.exp(Lv(T)*qv/(divisor*T))
    return theta_e

dir2='/mnt/lustre/koa/koastore/torri_group/air_directory/DCI-Project/'
def initiate_array():
    # Define array dimensions (adjust based on your netCDF)
    t_size = len(netCDF['time'])  # Number of timesteps
    z_size = len(netCDF['zh'])    # Number of vertical levels
    y_size = len(netCDF['yh'])    # Number of y-axis points
    x_size = len(netCDF['xh'])    # Number of x-axis points
    
    with h5py.File(dir2 + 'Variable_Calculation/' + 'theta_e'+f'_{res}'+'.h5', 'a') as f:
        # Check if the dataset 'theta_e' already exists
        if 'theta_e' not in f:
            # Create a dataset with the full size for all time steps (initially empty)
            f.create_dataset('theta_e', 
                             (t_size, z_size, y_size, x_size),  # Full size for all timesteps
                             maxshape=(None, z_size, y_size, x_size),  # Unlimited timesteps (can grow along time dimension)
                             dtype='float64', 
                             chunks=(1, z_size, y_size, x_size))  # Chunks for time axis to allow resizing

            
def add_timestep_at_index(timestep_data, index):
    with h5py.File(dir2 + 'Variable_Calculation/' + 'theta_e'+f'_{res}'+'.h5', 'a') as f:
        # Access the existing dataset 'theta_e'
        dataset = f['theta_e']
        
        # Assign the new timestep data at the specified index
        dataset[index] = timestep_data



#MAKING ARRAY TO STORE THETA_E
initiate_array()

#CALCULATING AND APPENDING TO DATA EACH TIMESTEP
for t in range(len(netCDF['time'])):
    if np.mod(t,1)==0: print(f'Current time {t}')
    data=netCDF.isel(time=t)
    [P, p0, qv, qt, Rd, Rv, Cpd, Cpv, Cpl, Lv, T, e, Pd, e_s, H] = load_vars(data)
    theta_e=make_theta_e(P, p0, qv, qt, Rd, Rv, Cpd, Cpv, Cpl, Lv, T, e, Pd, e_s, H)
    add_timestep_at_index(theta_e, t)


#Fast for 1KM, 1.5 hours for 250M