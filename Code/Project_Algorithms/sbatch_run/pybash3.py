import numpy as np
import matplotlib.pyplot as plt
import xarray as xr; import time as time

data=xr.open_dataset('/mnt/lustre/koa/koastore/torri_group/air_directory/cm1r20.3/run/cm1out_test7tundra-7_062217.nc')
parcel=xr.open_dataset('/mnt/lustre/koa/koastore/torri_group/air_directory/cm1r20.3/run/cm1out_pdata_test5tundra-7_062217.nc')


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


#Define Indicator Functions
if 'emptylike' not in globals():
    print('loading neccessary variables')
    variable='w'; w_data=data[variable] #get w data
    w_data=w_data.interp(zf=data['zh']).data #interpolation w data z coordinate from zh to zf
    variable='qv'; qv_data=data[variable].data # get qc data
    variable='qc'; qc_data=data[variable].data # get qc data
    variable='qi'; qi_data=data[variable].data # get qc data
    qc_plus_qi=qc_data+qi_data
    # variable='th'; th_data=data[variable].data # get qc data
    # variable='buoyancy'; buoyancy_data=data[variable].data # get qc data

    x_data=parcel['x'].data
    y_data=parcel['y'].data
    z_data=parcel['z'].data
    print('done loading')
    emptylike=True


def A_ind3d(i,t):
    #1s or 0s if parcel evaluates threshold for ith parcel at time t

    #(x,y,z) eulerian grid location
    # x=parcel['x'].isel(time=t,xh=i).values
    # y=parcel['y'].isel(time=t,xh=i).values
    # z=parcel['z'].isel(time=t,xh=i).values

    x=x_data[t,i]
    y=y_data[t,i]
    z=z_data[t,i]
    # xh_val=data['xh'].values*1000; which_xh=np.searchsorted(xh_val,x)-1; which_xh=np.where(which_xh == -1, 0, which_xh) #finds which xh layer parcel in
    # yh_val=data['yh'].values*1000; which_yh=np.searchsorted(yh_val,y)-1; which_xh=np.where(which_xh == -1, 0, which_xh) #finds which yh layer parcel in
    ybins=data['yf'].values*1000; dy=ybins[1]-ybins[0];which_y=np.floor(y/dy).astype(int)+np.where(data['yf']==0)[0].item()
    xbins=data['xf'].values*1000; dx=xbins[1]-xbins[0];which_x=np.floor(x/dx).astype(int)+np.where(data['xf']==0)[0].item()
    zf_val=data['zf'].values*1000; which_z=np.searchsorted(zf_val,z)-1; which_z=np.where(which_z == -1, 0, which_z) #finds which zf layer parcel in 

    
    #Data
    # qc=data['qc'].isel(time=t,xh=which_x,yh=which_y,zh=which_z).values
    # qi=data['qi'].isel(time=t,xh=which_x,yh=which_y,zh=which_z).values
    # w=data['w'].isel(time=t).interp(zf=data['zh']).isel(xh=which_x,yh=which_y,zh=which_z).values
    qc=qc_data[t,which_z,which_y,which_x]
    qi=qi_data[t,which_z,which_y,which_x]
    w=w_data[t,which_z,which_y,which_x]

    #Threshholds
    qcqi_thresh=1e-6 #kg/kg
    w_thresh=0.1 #1 #m/s
    
    A=np.where((w > w_thresh), 1, 0).item() #general updraft
    # A=np.where((qc + qi > qcqi_thresh) & (w > w_thresh), 1, 0).item() #cloudy updraft

    # if A==1: print(f'qc+qi: {qc+qi}',f'w: {w}') #TESTING***
    return A 
    
def I_ind3d(x,y,z,i,t): #z interval indictator function 
    k=z
    dz=zf(k+1)-zf(k)
    Ix=[xs[x]-dx/2,xs[x]+dx/2]
    Iy=[ys[y]-dy/2,ys[y]+dy/2]    
    Iz=[zs[z]-dz/2,zs[z]+dz/2]
    # X=parcel['x'].isel(xh=i,time=t)
    # Y=parcel['y'].isel(xh=i,time=t)
    # Z=parcel['z'].isel(xh=i,time=t)
    X=x_data[t,i]
    Y=y_data[t,i]
    Z=z_data[t,i]

    if (Ix[0] <= X <= Ix[1]) & (Iy[0] <= Y <= Iy[1]) & (Iz[0] <= Z <= Iz[1]):
        out=1
    else: 
        out=0
    return out

def which_parcel3d(x,y,z,t): #finds which parcels are in the gridbox at time t 
    # X=parcel['x'].isel(time=t).values
    # Y=parcel['y'].isel(time=t).values
    # Z=parcel['z'].isel(time=t).values
    X=x_data[t]
    Y=y_data[t]
    Z=z_data[t]

    dz=zf(z+1)-zf(z)
    Ix=[xs[x]-dx/2,xs[x]+dx/2]
    Iy=[ys[y]-dy/2,ys[y]+dy/2]    
    Iz=[zs[z]-dz/2,zs[z]+dz/2]

    # X[:]=Ix[0];Y[:]=Iy[0];Z[:]=Iz[0] #TESTING
    # print(Ix,Iy,Iz) #TESTING

    out=np.where((X >= Ix[0]) & (X <= Ix[1]) &
                 (Y >= Iy[0]) & (Y <= Iy[1]) & 
                 (Z >= Iz[0]) & (Z <= Iz[1]))
    return out

def H_ind_e(x): #Heaviside unit step function
    if x>0:
        out=1
    else:
        out=0 
    return out
    
def H_ind_d(x): #Heaviside unit step function
    if x<0:
        out=-1
    else:
        out=0 
    return out

def H_ind_m(x): #Heaviside unit step function
    if x>0:
        out=1
    elif x<0:
        out=-1 #why not allow for negative entrainement (detrainment)
    elif x==0: 
        out=0
    return out



#Calculating 3-Dimensional Entrainment Rate (KYONGMIN YEO AND DAVID M. ROMPS 2012)
#In the Lagrangian framework, the local entrainment rate e(x, t) is the number of particles that switch from inactive to active in each grid cell over some averaging time
def e3d(x,y,z,t): #horizontal averaged entrainment rate
    m_out=m(t)
    dz=zf(z+1)-zf(z)
    constant=(m_out/dx/dy/dz/dt) 

    #subsets only parcel that are entrainment candidates
    one=which_parcel3d(x,y,z,t) #checks if parcel is in the box at time t,
    # which_parcel_out=one[0]
    two=which_parcel3d(x,y,z,t-1) 
    which_parcel_out=(one or two)[0]

    print(which_parcel_out)
    
    out=0 #initialize output
    # for i in range(Np):
    for i in which_parcel_out:
        if np.mod(i,5000)==0: print(f'{i}/{Np}')
        A1=A_ind3d(i,t);A2=A_ind3d(i,t-1); 
        H=H_ind_e(A1-A2)
        I=I_ind3d(x,y,z,i,t)
        out+=constant*H*I

        # print('A1','A2','H','I');print(A1,A2,H,I);print('-'*40); #TESTING***
        # print(f'entrainment: {out}')
    return out #num/s

def d3d(x,y,z,t): #horizontal averaged entrainment rate
    m_out=m(t)
    dz=zf(z+1)-zf(z)
    constant=(m_out/dx/dy/dz/dt) 

    #subsets only parcel that are entrainment candidates
    one=which_parcel3d(x,y,z,t) #checks if parcel is in the box at time t,
    # which_parcel_out=one[0]
    two=which_parcel3d(x,y,z,t-1) 
    which_parcel_out=(one or two)[0]
    
    out=0 #initialize output
    # for i in range(Np):
    for i in which_parcel_out:
        if np.mod(i,5000)==0: print(f'{i}/{Np}')
        A1=A_ind3d(i,t);A2=A_ind3d(i,t-1); 
        H=H_ind_d(A1-A2)
        I=I_ind3d(x,y,z,i,t)
        out+=constant*H*I

        # print('A1','A2','H','I');print(A1,A2,H,I);print('-'*40); #TESTING***
        # print(f'entrainment: {out}')
    return out #num/s

def m3d(x,y,z,t): #horizontal averaged entrainment rate
    m_out=m(t)
    dz=zf(z+1)-zf(z)
    constant=(m_out/dx/dy/dz/dt) 

    #subsets only parcel that are entrainment candidates
    one=which_parcel3d(x,y,z,t) #checks if parcel is in the box at time t,
    # which_parcel_out=one[0]
    two=which_parcel3d(x,y,z,t-1) 
    which_parcel_out=(one or two)[0]
    
    out=0 #initialize output
    # for i in range(Np):
    for i in which_parcel_out:
        if np.mod(i,5000)==0: print(f'{i}/{Np}')
        A1=A_ind3d(i,t);A2=A_ind3d(i,t-1); 
        H=H_ind_m(A1-A2)
        I=I_ind3d(x,y,z,i,t)
        out+=constant*H*I

        # print('A1','A2','H','I');print(A1,A2,H,I);print('-'*40); #TESTING***
        # print(f'entrainment: {out}')
    return out #num/s

# # TESTING e3d()
# x=5
# y=5
# z=1 #parcels moved from 2 to 1,3
# t=5
# e3d(x=x,y=y,z=z,t=t)







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
netCDF=xr.open_dataset(dir+'cm1r20.3/run/cm1out_test7tundra-7_062217.nc') #***
true_time=netCDF['time']
parcel=xr.open_dataset(dir+'cm1r20.3/run/cm1out_pdata_test5tundra-7_062217.nc') #***
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




#Making vertical profile of cloudy updrafts

def entrainment_profile(type):
    global w_thresh
    #thresholds
    w_thresh=0.1
    qcqithresh=1e-6

    nt=len(data['time'])
        
    #get qc and interpolated w 

    # finds regions that match the threshold
    if type=="general":
        where_updraft=np.where((w_data>=w_thresh)) #uncomment for "general updraft"
    elif type=='cloudy': 
        where_updraft=np.where((w_data>=w_thresh) & (qc_plus_qi>=qcqithresh)) #uncomment for "cloudy updraft" 
    
    #creates profile storage and adds z column    
    zhs=data['zh'].values
    profile_array=np.zeros((len(zhs), 3)) #column 1: var, column 2: counter, column 3: list of zhs
    profile_array[:,2]=zhs

    #get incidies associated with threshold mask
    t_ind, z_ind, y_ind, x_ind = where_updraft

    #bin masked values by z level
    for count,(th,kh,jh,ih) in enumerate(zip(t_ind,z_ind,y_ind,x_ind)):
        if np.mod(count,100)==0: print(f'{count*100/len(t_ind):.2f} %')
        value=e3d(ih,jh,kh,th)
        profile_array[kh,0]+=value #adds data to first column
        if value!=0:
            profile_array[kh,1]+=1 #adds +1 counter to 2nd column
        
    return profile_array


# print('running general entrainment profile'); e_profile=entrainment_profile('general')
print('running cloudy entrainment profile'); e_profile=entrainment_profile('cloudy');
# np.save(dir+'tracking_algorithms/ENTRAINMENT_PROFILE_Updraft_Entrain.npy', e_profile)
np.save(dir+'tracking_algorithms/ENTRAINMENT_PROFILE_Cloudy_Entrain.npy', e_profile)