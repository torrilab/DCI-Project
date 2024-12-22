#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Importing Packages
import numpy as np
import xarray as xr

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as ticker
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import ScalarFormatter
import matplotlib.gridspec as gridspec


# In[160]:


# #TESTING
# ######################################
dir='/mnt/lustre/koa/koastore/torri_group/air_directory/'
data=xr.open_dataset(dir+'/cm1r20.3/run/cm1out_test7tundra-7_062217.nc') #***
f=data['w'].interp(zf=data['zh']).data


# In[254]:


def VertContour(f, units, xax, ax=None, ny=None, nx=None):
    # Create an axis if one is not provided
    if ax is None:
        fig, ax = plt.subplots()
    if ny is None: ny=2

    # Plot the contour on the specified axis
    if xax=='t':
        c = ax.contourf(f.T);
    else:
        c = ax.contourf(f);

    # Scientific Notation
    if units == "sci":
        from matplotlib.ticker import ScalarFormatter
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((-3, 3))
        ax.xaxis.set_major_formatter(formatter)

    # Set labels
    if xax=='t':
        if nx is None: nx=1
        ax.set_xlabel('time')
    elif xax=='y':
        ax.set_xlabel('y (km)')
    elif xax=='x':
        ax.set_xlabel('x (km)')

    # Fixing Vertical Ticks
    tick_inds = np.arange(0, len(data['zh'].values), ny)
    ax.set_yticks(tick_inds)
    ax.set_yticklabels(np.round(data['zh'].values[tick_inds], 1))

    if xax=='y':
        if nx is None: nx=5
        tick_inds = np.arange(0, len(data['yh'].values), nx)
        ax.set_xticks(tick_inds)
        ax.set_xticklabels(np.round(data['yh'].values[tick_inds], 1))
        
    elif xax=='x':
        if nx is None: nx=60
        tick_inds = np.arange(0, len(data['xh'].values), nx)
        ax.set_xticks(tick_inds)
        ax.set_xticklabels(np.round(data['xh'].values[tick_inds], 1))
        
    # plt.close(fig)
    return ax
    
def HorizContour(f, units, ax=None, nx=None, ny=None):
    # Create an axis if one is not provided
    if ax is None:
        fig, ax = plt.subplots()
    if nx is None: nx=60
    if ny is None: ny=5

    # Plot the contour on the specified axis
    c = ax.contourf(f);

    # Scientific Notation
    if units == "sci":
        from matplotlib.ticker import ScalarFormatter
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((-3, 3))
        ax.xaxis.set_major_formatter(formatter)

    # Set labels
    ax.set_xlabel('x (km)')
    ax.set_ylabel('y (km)')

    # Fixing Horizontal Ticks
    tick_inds = np.arange(0, len(data['xh'].values), nx)
    ax.set_xticks(tick_inds)
    ax.set_xticklabels(np.round(data['xh'].values[tick_inds], 1))
    
    tick_inds = np.arange(0, len(data['yh'].values), ny)
    ax.set_yticks(tick_inds)
    ax.set_yticklabels(np.round(data['yh'].values[tick_inds], 1))
    
    # plt.close(fig)
    return ax


# In[258]:


# #TESTING
# ######################################
# VertContour(f[:,:,10,10], units="sci", xax='t')
# VertContour(f[10,:,:,10], units="sci", xax='y',nx=10)
# VertContour(f[10,:,10,:], units="sci", xax='x')
# HorizContour(f[10,10,:,:], units="sci")


# In[221]:


# #How To Plot Multiple GridSpec Subplots
# fig = plt.figure(figsize=(10, 5))
# gs = gridspec.GridSpec(1, 2, figure=fig)

# # Create first subplot
# ax1 = fig.add_subplot(gs[0, 0])
# VertContour(f[:,:,10,10], units="sci", ax=ax1)

# # Create second subplot
# ax2 = fig.add_subplot(gs[0, 1])
# VertContour(f[:,:,10,10], units="sci", ax=ax2)


# In[ ]:


#TIME 00:00:00 Function
#Gets the realtime for the current timestep
def get_time(t):
    init_day,init_hour,init_min=0,0,0
    times=data['time'].values/(1e9 * 60); time_inc=times.astype(int)[1]-times.astype(int)[0]
    current_min=init_hour*60+init_min+time_inc*t;
    
    days = init_day + (current_min // (24 * 60))
    
    remain_min = (init_min+time_inc*t) % (24 * 60); 
    hours = (init_hour + (remain_min // 60)) % 24
    mins = remain_min % 60

    ##############################################
    days=str(days);hours=str(hours);mins=str(mins)
    if len(days)==1:days='0'+days
    if len(hours)==1:hours='0'+hours
    if len(mins)==1:mins='0'+mins
    ##############################################

    combo=days+":"+hours+":"+mins
    return(days,hours,mins),(combo)


# In[ ]:


#ANIMATION FUNCTION
#MUST CREATE A SINGLE TIME PLOTTING FUNCTION TITLED single_plot(args) 

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


# In[ ]:


#CONVERT GIF TO MP4
def convert_gif_to_mp4(input_file, output_file, fps):
    from moviepy.editor import VideoFileClip
    # Load the GIF file
    gif_clip = VideoFileClip(input_file)

    # Set the desired framerate if provided
    if fps:
        gif_clip = gif_clip.set_fps(fps)

    # Write the GIF as an MP4 file
    gif_clip.write_videofile(output_file, codec="libx264")

