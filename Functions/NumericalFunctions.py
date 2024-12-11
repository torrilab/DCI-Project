#!/usr/bin/env python
# coding: utf-8

# In[2]:


# #How to Import to Code Document
# import sys
# dir='/mnt/lustre/koa/koastore/torri_group/air_directory/Project/'
# path=dir+'../Functions'
# sys.path.append(path)
# from NumericalFunctions import *


# In[8]:


def Ddt(f,dt):
    # dt=(data['time'][1]-data['time'][0]).item()/1e9
    _ddt=np.zeros_like(f)
    _ddt[1:-1] = (f[2:] - f[:-2]) / (dt)
    return _ddt

def Ddz(f,dz):    
    _ddz=np.zeros_like(f)
    _ddz[:, 1:-1] = (f[:, 2:] - f[:, :-2]) / (2 * dz)
    _ddz[:, 0] = (f[:, 1] - f[:, 0]) / dz  # Forward difference 
    _ddz[:, -1] = (f[:, -1] - f[:, -2]) / dz  # Backward difference 
    return _ddz

def DdzStretch(f):
    #f must be interpolated to cell centers
    dz=np.diff(data['zf'].values)
    dz=dz.copy()[np.newaxis, :, np.newaxis, np.newaxis]
    
    ddz=np.zeros_like(f)
    ddz[:, 1:-1] = (f[:, 2:] - f[:, :-2]) / (2 * dz[:, 1:-1])
    ddz[:, 0] = (f[:, 1] - f[:, 0]) / dz[:, 0]  # Forward difference 
    ddz[:, -1] = (f[:, -1] - f[:, -2]) / dz[:, -1]  # Backward difference 
    return ddz

def Ddy(f,dy):    
    _ddy=np.zeros_like(f)
    _ddy[:, :, 1:-1] = (f[:, :, 2:] - f[:, :, :-2]) / (2 * dy)
    _ddy[:, :, 0] = (f[:, :, 1] - f[:, :, 0]) / dy  # Forward difference 
    _ddy[:, :, -1] = (f[:, :, -1] - f[:, :, -2]) / dy  # Backward difference 
    return _ddy

def Ddx(f,dx):    
    _ddx=np.zeros_like(f)
    _ddx[:, :, :, 1:-1] = (f[:, :, :, 2:] - f[:, :, :, :-2]) / (2 * dx)
    _ddx[:, :, :, 0] = (f[:, :, :, 1] - f[:, :, :, 0]) / dx  # Forward difference 
    _ddx[:, :, :, -1] = (f[:, :, :, -1] - f[:, :, :, -2]) / dx  # Backward difference 
    return _ddx


def DivergenceHoriz(f,dx,dy):
    out=Ddy(f,dy)+Ddx(f,dx)
    return out

def Divergence3D(f,dx,dy,dz):
    out=Ddz(f,dz)+Ddy(f,dy)+Ddx(f,dx)
    return out

def Divergence3DStretch(f,dx,dy):
    out=DdzStretch(f)+Ddy(f,dy)+Ddx(f,dx)
    return out

def LaplacianHoriz(f,dx,dy):
    # Initialize the second derivatives arrays with zeros, same shape as f
    d2f_dx2 = np.zeros_like(f)
    d2f_dy2 = np.zeros_like(f)
    
    # Second derivatives using central differences
    d2f_dx2[:, :, 1:-1, :] = (f[:, :, :-2, :] - 2 * f[:, :, 1:-1, :] + f[:, :, 2:, :]) / dx**2
    d2f_dy2[:, :, :, 1:-1] = (f[:, :, :, :-2] - 2 * f[:, :, :, 1:-1] + f[:, :, :, 2:]) / dy**2
    
    # Combine to reconstruct the Laplacian (RHS)
    out = d2f_dx2 + d2f_dy2
    return out

def Laplacian3D(f, dx, dy, dz):
    #f must be provided at a specific 
    
    # Initialize the second derivatives arrays with zeros, same shape as f
    d2f_dz2 = np.zeros_like(f)
    d2f_dy2 = np.zeros_like(f)
    d2f_dx2 = np.zeros_like(f)
    
    # Second derivatives using central differences
    d2f_dz2[:, 1:-1, :, :] = (f[:, :-2, :, :] - 2 * f[:, 1:-1, :, :] + f[:, 2:, :, :]) / dz**2
    d2f_dy2[:, :, 1:-1, :] = (f[:, :, :-2, :] - 2 * f[:, :, 1:-1, :] + f[:, :, 2:, :]) / dy**2
    d2f_dx2[:, :, :, 1:-1] = (f[:, :, :, :-2] - 2 * f[:, :, :, 1:-1] + f[:, :, :, 2:]) / dx**2
    
    # Combine to reconstruct the Laplacian (RHS)
    out = d2f_dx2 + d2f_dy2 + d2f_dz2
    return out

def Laplacian3DStretch(f, dx, dy):
    # Initialize the second derivatives arrays with zeros, same shape as f
    #f must be interpolated to cell centers
    #f must be an array array with f for face and h for center (e.g. zf/zh)
    dz=np.diff(data['zf'].values)
    dz=dz.copy()[np.newaxis, :, np.newaxis, np.newaxis]
    
    # Initialize the second derivatives arrays with zeros, same shape as f
    d2f_dz2 = np.zeros_like(f)
    d2f_dy2 = np.zeros_like(f)
    d2f_dx2 = np.zeros_like(f)
    
    # Second derivatives using central differences
    d2f_dz2[:, 1:-1, :, :] = (f[:, :-2, :, :] - 2 * f[:, 1:-1, :, :] + f[:, 2:, :, :]) / dz[:,1:-1]**2
    d2f_dy2[:, :, 1:-1, :] = (f[:, :, :-2, :] - 2 * f[:, :, 1:-1, :] + f[:, :, 2:, :]) / dy**2
    d2f_dx2[:, :, :, 1:-1] = (f[:, :, :, :-2] - 2 * f[:, :, :, 1:-1] + f[:, :, :, 2:]) / dx**2
    
    # Combine to reconstruct the Laplacian (RHS)
    out = d2f_dx2 + d2f_dy2 + d2f_dz2
    return out

# #TESTING
# ######################################
# import numpy as np
# f = np.random.random((4, 4, 4, 4))
# Ddt(f,1)
# Ddz(f,1)
# Ddy(f,1)
# Ddx(f,1)
# DivergenceHoriz(f,1,1)
# Divergence3D(f,1,1,1)

# HorizLaplacian(f,1,1)
# Laplacian3D(f,1,1,1)

# import xarray as xr
# dir='/mnt/lustre/koa/koastore/torri_group/air_directory/'
# data=xr.open_dataset(dir+'/cm1r20.3/run/cm1out_test7tundra-7_062217.nc') #***
# f=data['w'].interp(zf=data['zh']).data
# DdzStretch(f)
# Divergence3DStretch(f,1,1)
# Laplacian3DStretch(f,1,1)


# In[ ]:


#Averaging and Slicing Functions
def HorizAvg_zt(f): 
    out=np.mean(f, axis=(2,3)) #takes horizontal average leaving f(t,z)
    return out
def VertProfile_z(f): 
    out=np.mean(f, axis=(0,2,3)) #takes horizontal + time average leaving f(z)
    return out
def HorizProfile_txy(f): 
    out=np.mean(f, axis=(1)) #takes horizontal + time average leaving f(z)
    return out    
def Slice(type,f,ind):
    if type=='t':
        out=f[ind]
    if type=='z':
        out=f[:,ind]
    if type=='y':
        out=f[:, :, ind]
    if type=='x':
        out=f[:, :, :, ind]
    return out
    
# #TESTING
# ######################################
# import numpy as np
# f = np.random.random((4, 4, 4, 4))
# HorizAvg_zt(f)
# VertProfile_z(f)
# HorizProfile_txy(f)
# Slice('t',f,2)
# Slice('z',f,2)
# Slice('y',f,2)
# Slice('x',f,2)

