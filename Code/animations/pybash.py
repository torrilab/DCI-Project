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

qv_data=data['qv'].data
th_data=data['th'].data
import h5py
with h5py.File(dir + 'theta_e.h5', 'r') as f:
    theta_e_data = f['theta_e'][:]
surface_qvflux_data=data['qvflux'].data
surface_thflux_data=data['thflux'].data

surface_qv_data=qv_data[:,0,:,:]
surface_th_data=th_data[:,0,:,:]
surface_th_e_data=theta_e_data[:,0,:,:]

# Store vmin and vmax for each variable in a list of tuples
vmin_max_values = [
    (np.min(surface_qv_data), np.max(surface_qv_data)),  # (vmin_qv, vmax_qv)
    (np.min(surface_th_data), np.max(surface_th_data)),  # (vmin_th, vmax_th)
    (np.min(surface_th_e_data), np.max(surface_th_e_data)),  # (vmin_the, vmax_the)
    (np.min(surface_qvflux_data), np.max(surface_qvflux_data)),  # (vmin_qvflux, vmax_qvflux)
    (np.min(surface_thflux_data), np.max(surface_thflux_data)),  # (vmin_thflux, vmax_thflux)
]

def single_plot(fig, t, vmin_max_values):
    gs = gridspec.GridSpec(5, 1, figure=fig, hspace=0.1)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[2, 0])
    ax4 = fig.add_subplot(gs[3, 0])
    ax5 = fig.add_subplot(gs[4, 0])

    # Extract vmin and vmax from the tuple list for each variable
    vmin_qv, vmax_qv = vmin_max_values[0]
    vmin_th, vmax_th = vmin_max_values[1]
    vmin_th_e, vmax_th_e = vmin_max_values[2]
    vmin_qvflux, vmax_qvflux = vmin_max_values[3]
    vmin_thflux, vmax_thflux = vmin_max_values[4]

    # Define the levels using linspace for each variable to ensure consistent color mapping
    qv_levels = np.linspace(vmin_qv, vmax_qv, 100)
    th_levels = np.linspace(vmin_th, vmax_th, 100)
    th_e_levels = np.linspace(vmin_th_e, vmax_th_e, 100)
    qvflux_levels = np.linspace(vmin_qvflux, vmax_qvflux, 100)
    thflux_levels = np.linspace(vmin_thflux, vmax_thflux, 100)

    # Create contour plots with consistent levels for each variable
    cf1 = ax1.contourf(surface_qv_data[t], levels=qv_levels)
    ax1.set_title("Surface " + r"$q_v$")
    
    cf2 = ax2.contourf(surface_th_data[t], levels=th_levels)
    ax2.set_title("Surface " + r"$\theta$")
    
    cf3 = ax3.contourf(surface_th_e_data[t], levels=th_e_levels)
    ax3.set_title("Surface " + r"$\theta_e$")
    
    cf4 = ax4.contourf(surface_qvflux_data[t], levels=qvflux_levels)
    ax4.set_title("Surface " + r"$q_v$" + " Flux")
    
    cf5 = ax5.contourf(surface_thflux_data[t], levels=thflux_levels)
    ax5.set_title("Surface " + r"$\theta$" + " Flux")
    
    # Add colorbars to each subplot
    fig.colorbar(cf1, ax=ax1)
    fig.colorbar(cf2, ax=ax2)
    fig.colorbar(cf3, ax=ax3)
    fig.colorbar(cf4, ax=ax4)
    fig.colorbar(cf5, ax=ax5)

from matplotlib.animation import FuncAnimation, PillowWriter
def create_animation(start_t, end_t, output_file, vmin_max_values, fps=2):
    # Create a figure each time for the animation
    fig = plt.figure(figsize=(18, 25))

    # Define the update function for the animation
    def update(t):
        plt.clf()  # Clear the current figure
        if np.mod(t, 20) == 0:
            print(f'current t: {t}')
        single_plot(fig, t, vmin_max_values)  # Pass the figure and vmin_max_values to single_plot

    # Create the animation object
    ani = FuncAnimation(fig, update, frames=np.arange(start_t, end_t), repeat=False)

    # Save the animation as a GIF file using PillowWriter
    writer = PillowWriter(fps=fps)
    ani.save(output_file, writer=writer)


# Example usage
output_filename = dir+'animations/QV_TH_animation_1km.gif'
# create_animation(start_t=0, end_t=5, output_file=output_filename, vmin_max_values=vmin_max_values)
create_animation(start_t=0, end_t=5, output_file=len(data['time'])-1, vmin_max_values=vmin_max_values)
