#!/usr/bin/env python
# coding: utf-8

# In[2]:


# #How to Import to Code Document
# import sys
# dir2='/mnt/lustre/koa/koastore/torri_group/air_directory/DCI-Project/'
# path=dir2+'../Functions/'
# sys.path.append(path)

# import NumericalFunctions
# from NumericalFunctions import * # import NumericalFunctions 
# import PlottingFunctions
# from PlottingFunctions import * # import PlottingFunctions


# # # Get all functions in NumericalFunctions
# # import inspect
# # functions = [f[0] for f in inspect.getmembers(NumericalFunctions, inspect.isfunction)]
# # functions


# In[ ]:


#INITIALIZE DATA FUNCTION
###############################################################
def initiate_array_2D(out_file,vars,t_chunk_size,z_chunk_size,t_size=None,z_size=None):
    # Define array dimensions (adjust based on your data)

    if t_size==None:
        t_size = len(data['time'])  # Number of timesteps
    if z_size==None:
        z_size = len(data['zh'])    # Number of vertical levels
    
    with h5py.File(out_file, 'w') as f: 
        # Check if the dataset 'theta_e' already exists
        for var_name in vars:
            if var_name not in f:
                # Create a dataset with the full size for all time steps (initially empty)
                f.create_dataset(var_name, 
                                 (t_size, z_size),  # Full size for all timesteps
                                 chunks=(t_chunk_size, z_chunk_size))  # Chunks for time axis to allow resizing

#INITIALIZE DATA FUNCTION
###############################################################
def initiate_array_4D(out_file,vars,t_chunk_size,z_chunk_size,y_chunk_size,x_chunk_size,t_size=None,z_size=None,y_size=None,x_size=None):
    # Define array dimensions (adjust based on your data)

    if t_size==None:
        t_size = len(data['time'])  # Number of timesteps
    if z_size==None:
        z_size = len(data['zh'])    # Number of vertical levels
    if y_size==None:
        y_size = len(data['yh'])    # Number of vertical levels
    if x_size==None:
        x_size = len(data['xh'])    # Number of vertical levels
    
    with h5py.File(out_file, 'w') as f: 
        # Check if the dataset 'theta_e' already exists
        for var_name in vars:
            if var_name not in f:
                # Create a dataset with the full size for all time steps (initially empty)
                f.create_dataset(var_name, 
                                 (t_size, z_size, y_size, x_size),  # Full size for all timesteps
                                 chunks=(t_chunk_size, z_chunk_size, y_chunk_size, x_chunk_size))  # Chunks for time axis to allow resizing


# In[8]:


def Ddt(f,dt):
    import numpy as np
    # dt=(data['time'][1]-data['time'][0]).item()/1e9
    _ddt=np.zeros_like(f)
    _ddt[1:-1] = (f[2:] - f[:-2]) / (dt)
    return _ddt

def Ddz_1D(f,dz):  
    import numpy as np
    _ddz=np.zeros_like(f)
    _ddz[:, 1:-1] = (f[:, 2:] - f[:, :-2]) / (2 * dz)
    _ddz[:, 0] = (f[:, 1] - f[:, 0]) / dz  # Forward difference 
    _ddz[:, -1] = (f[:, -1] - f[:, -2]) / dz  # Backward difference 
    return _ddz

def Ddz_1DStretch(f,data):
    import numpy as np
    #f must be interpolated to cell centers
    dz=np.diff(data['zf'].values)
    
    ddz=np.zeros_like(f)
    ddz[1:-1] = (f[2:] - f[:-2]) / (2 * dz[1:-1])
    ddz[0] = (f[1] - f[0]) / dz[0]  # Forward difference 
    ddz[-1] = (f[-1] - f[-2]) / dz[-1]  # Backward difference 
    return ddz

##################################################################

def Profile_Ddz(profile):
    import numpy as np
    #f must be interpolated to cell centers
    dz=np.diff(profile[:,1])

    f=profile[:,0]
    ddz=np.zeros_like(f)
    denom=dz[1:] + dz[:-1]
    ddz[1:-1] = (f[2:] - f[:-2]) / (2 * denom)
    ddz[0] = (f[1] - f[0]) / dz[0]  # Forward difference 
    ddz[-1] = (f[-1] - f[-2]) / dz[-1]  # Backward difference 
    return np.column_stack([ddz, profile[:,1]])

##################################################################

def Ddz_4DStretch(f,data):
    import numpy as np
    #f must be interpolated to cell centers
    dz=np.diff(data['zf'].values)
    dz=dz.copy()[np.newaxis, :, np.newaxis, np.newaxis]
    
    ddz=np.zeros_like(f)
    ddz[:, 1:-1] = (f[:, 2:] - f[:, :-2]) / (2 * dz[:, 1:-1])
    ddz[:, 0] = (f[:, 1] - f[:, 0]) / dz[:, 0]  # Forward difference 
    ddz[:, -1] = (f[:, -1] - f[:, -2]) / dz[:, -1]  # Backward difference 
    return ddz

def Ddy_4D(f,dy):   
    import numpy as np
    _ddy=np.zeros_like(f)
    _ddy[:, :, 1:-1] = (f[:, :, 2:] - f[:, :, :-2]) / (2 * dy)
    _ddy[:, :, 0] = (f[:, :, 1] - f[:, :, 0]) / dy  # Forward difference 
    _ddy[:, :, -1] = (f[:, :, -1] - f[:, :, -2]) / dy  # Backward difference 
    return _ddy

def Ddx_4D(f,dx): 
    import numpy as np
    _ddx=np.zeros_like(f)
    _ddx[:, :, :, 1:-1] = (f[:, :, :, 2:] - f[:, :, :, :-2]) / (2 * dx)
    _ddx[:, :, :, 0] = (f[:, :, :, 1] - f[:, :, :, 0]) / dx  # Forward difference 
    _ddx[:, :, :, -1] = (f[:, :, :, -1] - f[:, :, :, -2]) / dx  # Backward difference 
    return _ddx

##############################

def Ddz_3D(f,dz): 
    import numpy as np
    _ddz=np.zeros_like(f)
    _ddz[1:-1] = (f[2:] - f[:-2]) / (2 * dz)
    _ddz[0] = (f[1] - f[0]) / dz  # Forward difference 
    _ddz[-1] = (f[-1] - f[-2]) / dz  # Backward difference 
    return _ddz

def Ddz_3DStretch(f,data):
    import numpy as np
    #f must be interpolated to cell centers
    dz=np.diff(data['zf'].values)
    dz=dz.copy()[:, np.newaxis, np.newaxis]
    
    ddz=np.zeros_like(f)
    ddz[1:-1] = (f[2:] - f[:-2]) / (2 * dz[1:-1])
    ddz[0] = (f[1] - f[0]) / dz[0]  # Forward difference 
    ddz[-1] = (f[-1] - f[-2]) / dz[-1]  # Backward difference 
    return ddz

def Ddy_3D(f,dy):   
    import numpy as np
    _ddy=np.zeros_like(f)
    _ddy[:, 1:-1] = (f[:, 2:] - f[:, :-2]) / (2 * dy)
    _ddy[:, 0] = (f[:, 1] - f[:, 0]) / dy  # Forward difference 
    _ddy[:, -1] = (f[:, -1] - f[:, -2]) / dy  # Backward difference 
    return _ddy

def Ddx_3D(f,dx): 
    import numpy as np
    _ddx=np.zeros_like(f)
    _ddx[:, :, 1:-1] = (f[:, :, 2:] - f[:, :, :-2]) / (2 * dx)
    _ddx[:, :, 0] = (f[:, :, 1] - f[:, :, 0]) / dx  # Forward difference 
    _ddx[:, :, -1] = (f[:, :, -1] - f[:, :, -2]) / dx  # Backward difference 
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
    import numpy as np
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
    import numpy as np
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
    import numpy as np
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

# u=data['u'].interp(xf=data['xh']).data; dx=1000
# v=data['v'].interp(yf=data['yh']).data; dy=1000
# conv=-(Ddx(u,dx)+Ddy(v,dy))


# In[ ]:


#Averaging and Slicing Functions
def HorizAvg_zt(f): 
    import numpy as np
    out=np.mean(f, axis=(2,3)) #takes horizontal average leaving f(t,z)
    return out
def VertProfile_z(f): 
    import numpy as np
    out=np.mean(f, axis=(0,2,3)) #takes horizontal + time average leaving f(z)
    return out
def HorizProfile_txy(f): 
    import numpy as np
    out=np.mean(f, axis=(1)) #takes horizontal + time average leaving f(z)
    return out    
def Slice(type,f,ind):
    import numpy as np
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


# In[1]:


# def check_memory():
#     import sys
#     ipython_vars = ["In", "Out", "exit", "quit", "get_ipython", "ipython_vars"]
#     print("Top 10 objects with highest memory usage")
#     # Get a sorted list of the objects and their sizes
#     mem = {
#         key: round(value/1e6,2)
#         for key, value in sorted(
#             [
#                 (x, sys.getsizeof(globals().get(x)))
#                 for x in globals()
#                 if not x.startswith("_") and x not in sys.modules and x not in ipython_vars
#             ],
#             key=lambda x: x[1],
#             reverse=True)[:10]
#     }
#     print({key:f"{value} MB" for key,value in mem.items()})
#     print(f"\n{round(sum(mem.values()),2)/1000} GB in use overall")

# check_memory()

def check_memory(namespace):
    import sys
    ipython_vars = ["In", "Out", "exit", "quit", "get_ipython", "ipython_vars"]
    print("Top 10 objects with highest memory usage")
    # Get a sorted list of the objects and their sizes
    mem = {
        key: round(value/1e6, 2)
        for key, value in sorted(
            [
                (x, sys.getsizeof(namespace.get(x)))
                for x in namespace
                if not x.startswith("_") and x not in sys.modules and x not in ipython_vars
            ],
            key=lambda x: x[1],
            reverse=True)[:10]
    }
    print({key: f"{value} MB" for key, value in mem.items()})
    print(f"\n{round(sum(mem.values()), 2)/1000} GB in use overall")


# In[ ]:




