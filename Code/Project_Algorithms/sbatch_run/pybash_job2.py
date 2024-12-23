#Loading in Packages and Data

#Importing Packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as ticker
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
from matplotlib.colors import Normalize
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import ScalarFormatter
import matplotlib.colors as mcolors
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
# parcel=parcel.isel(time=times.astype(int)) 

#Restricts the timesteps of the data from timesteps0 to 140
data=data.isel(time=np.arange(0,140+1))
parcel=parcel.isel(time=np.arange(0,140+1))

def grid_location(x,y,z):
    xf=data['xf'].values*1000; which_xh=np.searchsorted(xf,x)-1; which_xh=np.where(which_xh == -1, 0, which_xh) #finds which x layer parcel in
    yf=data['yf'].values*1000; which_yh=np.searchsorted(yf,y)-1; which_yh=np.where(which_yh == -1, 0, which_yh) #finds which y layer parcel in
    zf=data['zf'].values*1000; which_zh=np.searchsorted(zf,z)-1; which_zh=np.where(which_zh == -1, 0, which_zh) #finds which z layer parcel in     
    return which_zh,which_yh,which_xh
    
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










def shape_search_2d(array): #2-D Shape Searching Algorithm (based on breadth-first search) 
    array=array.copy()
    final_array=np.zeros_like(array)
    #Functions 
    def next_most_1_2d(array): #finds next most 1
        if len(np.where(array==1)[0])!=0:
            result=tuple(arr[0] for arr in np.where(array==1))
            return result
        else:
            return (-1,-1)
    ######################################################################   
    def find_neighbor_index_2d(array,container): #find the indexes of all neighbors
                    
        #neighbors that are 0 or exist in visit or queue are not appended to neighbors
        tup,neighbors=[],[]
        container=[tuple(sub) for sub in container]; 
        nx,ny=array.shape[1]-1,array.shape[0]-1
        
        for index in container:
            if index==(-1,-1):
                pass
            else: 
                ######################################################################   
                #code for inside #all possible neighbors
                tup=[[index[0]-1,index[1]-1],[index[0]-1,index[1]],[index[0]-1,index[1]+1], 
                    [index[0],index[1]-1],[index[0],index[1]+1],
                    [index[0]+1,index[1]-1],[index[0]+1,index[1]],[index[0]+1,index[1]+1]] 
                #code for edges and corners 
                tup=[[np.mod(sublist[0],ny+1),sublist[1]] for sublist in tup] #use if y boundaries are periodic
                # tup=[sublist[0],sublist[1],[np.mod(sublist[1],nx+1)] for sublist in tup] #use if x boundaries are periodic
                tup=[sublist for sublist in tup if 0 <= sublist[1] <= nx] #use if x not periodic 
                if tup: [neighbors.append(sub) for sub in tup]
                ######################################################################             
            if neighbors:  #only unique elements that are not visited
                neighbors=np.unique(neighbors,axis=0).tolist()
                neighbors=[tuple(sub) for sub in neighbors if array[tuple(sub)] != 0 and tuple(sub) not in container]

        if not neighbors:
            neighbors=np.full((0,2),0,dtype=int)    
        else: neighbors=np.array(neighbors)
        return neighbors
    ###################################################################### 
    
    #The Algorithm
    n,k=0,0 #n is current shape, k is number of iterations on current shape 
    while True:
        n+=1;
        # if np.mod(n,5)==0:
        #     print("Current shape number: " + str(n))
        visit=np.full((0,2),0,dtype=int) #creates visit variable for current shapes
        queue=np.full((0,2),0,dtype=int) #creates queue variable for possible neighbors

        ######################################################################
        #finds the first 1 in the array, append to visit, and zero out
        index=next_most_1_2d(array);
        visit=np.concatenate([visit,[index]]);array[index]=0;
        
        #finds neighbors of first index and appends to queue
        neighbors=find_neighbor_index_2d(array,visit) 
        queue=np.concatenate([queue,neighbors]) 

        #for rest of individual shape
        while queue.size!=0: 
            k+=1
            #add all queued indexes to visit and find unique,nonzero,and nonvisited neighbor
            visit=np.concatenate([visit,queue]); neighbors=find_neighbor_index_2d(array,queue) 
            #zero out queued in array and empty out queue
            array[queue[:, 0], queue[:, 1]] = 0; queue=np.full((0,2),0,dtype=int) 
            #append found neighbor to queue
            queue=np.concatenate([queue,neighbors])
                
            #failsafes to end while loop
            if queue.size==0: 
                break #breaks single loop for current shape if no more neighbor
            if k>=array.shape[0]*array.shape[1]: #k failsafe, set to max volume of array
                break    
        #sets output array's value to shape number
        if index!=(-1,-1):
            final_array[visit[:, 0], visit[:, 1]] = n #sets final array location to shape number
        ######################################################################  
        
        #failsafes to end while loop
        if index==(-1,-1):
            # print("no more shapes are left")
            # print(f"total of {n-1} shapes were found")
            break  #break loop if no more 1s
        if n>=array.shape[0]*array.shape[1]:  #n failsafe, set to max volume of array
            print("failsafe reached")
            break  #break loop if no more 1s
    return final_array
##########################################################################################################################################  









#USING W>=0 THRESHOLD

zerowthresh=False
zerowthresh=True #Uncomment if w>=0 is the threshold

if zerowthresh==True:
    #import parcel_flag_array
    import h5py
    input_file = dir+'tracking_algorithms/plots/parcel_flag_array.h5' 
    with h5py.File(input_file, 'r') as f:
        parcel_flag_array = np.array(f['flag_array'])
    
    # input_file = dir+'tracking_algorithms/plots/deep_parcel_flag_array.h5' 
    # with h5py.File(input_file, 'r') as f:
    #     deep_parcel_flag_array = np.array(f['flag_array'])
    
    #import cloudy, updraft, or updraft_cloudy flag_array
    input_file = dir+'tracking_algorithms/plots/cloudy_flag_array.h5' 
    with h5py.File(input_file, 'r') as f:
        cloudy_flag_array = np.array(f['flag_array'])
    
    input_file = dir+'tracking_algorithms/plots/updraft_flag_arrayw>=0.h5' 
    with h5py.File(input_file, 'r') as f:
        updraft_flag_array = np.array(f['flag_array'])
    
    input_file = dir+'tracking_algorithms/plots/cloudyupdraft_flag_arrayw>=0.h5' 
    with h5py.File(input_file, 'r') as f:
        cloudyupdraft_flag_array = np.array(f['flag_array'])



#Job Array

num_jobs=30 #how many total jobs are being run? i.e. array=1-100 ==> num_jobs=100 #***

job_id = int(os.environ.get('SLURM_ARRAY_TASK_ID', 0)) #this is the current SBATCH job id
if job_id==0: job_id=1
num_parcels=len(data['time']) #total number of parcels
job_range = num_parcels//num_jobs #number of parcels per job 

# Calculate start and end based on job_id
start_job = (job_id - 1) * job_range
end_job = start_job + job_range
if job_id==num_jobs: end_job=num_parcels-1
print(f'running for timesteps {start_job}-{end_job-1}')

data=data.isel(time=slice(start_job,end_job))
# index_adjust = int(data['time'][0].values/1e9/60)
parcel=parcel.isel(time=slice(start_job,end_job))

parcel_flag_array=parcel_flag_array[slice(start_job,end_job)]
cloudy_flag_array=cloudy_flag_array[slice(start_job,end_job)]
updraft_flag_array=updraft_flag_array[slice(start_job,end_job)]
cloudyupdraft_flag_array=cloudyupdraft_flag_array[slice(start_job,end_job)]



#Collected data of averaged BFS clouds for all clouds, updrafts, and cloudy updrafts (need to change the code up to make it a 2d histogram)
types=['cloudy','updraft','cloudyupdraft']

for type in types:
    print(f'current type: {type}')
    # if type=='cloudyupdraft': break #TESTING
    
    if type=='cloudy':
        flag_array=cloudy_flag_array.copy()
    elif type=='updraft':
        flag_array=updraft_flag_array.copy()
    elif type=='cloudyupdraft':
        flag_array=cloudyupdraft_flag_array.copy()
    
    def all_clouds_single_layer(t,which_zh,cloudy_bfs,vars):
        #appends the means of each individual cloud into a list
        max_ind=int(np.max(cloudy_bfs))
        for ind in np.arange(1,max_ind+1):
            position=np.where(cloudy_bfs==ind)
    
            if np.any(position)==True:
                for variable in vars:
                    if variable=='w':
                        var_cloud_data=data[variable].isel(time=t).interp(zf=data['zh']).isel(zh=which_zh)[position].values
                    else:
                        var_cloud_data=data[variable].isel(time=t).isel(zh=which_zh)[position].values
                    if variable=='qv' or variable=='qc':
                        var_cloud_data*=1000
                        
                    var_cloud_data=np.mean(var_cloud_data)
                    globals()[f"{variable}_values"].append(var_cloud_data)
                    if variable=='w': #only perform once
                        zlevels.append(which_zh)
        return (globals()[f"{variable}_values"] for variable in vars), zlevels
    
    def average_clouds(t,vars):
        global zlevels
        parcel_flag=flag_array[t]
        for which_zh in np.arange(len(data['zh'])):
            if np.mod(which_zh,5)==0: print(f'currently working on zlevel: {which_zh}')
            flag_plane=parcel_flag[which_zh]
            cloudy_bfs=shape_search_2d(flag_plane)
            (w_values, qv_values, qc_values, th_values),zlevels=all_clouds_single_layer(t,which_zh,cloudy_bfs,vars) #outputs list of cloud averages
        return (globals()[f"{variable}_values"] for variable in vars), zlevels
            
    vars=['w','qv','qc','th']
    for variable in vars:
        globals()[f"{variable}_values"] = []
        zlevels=[]
    for t in np.arange(len(data['time'])):
    # for t in [33,34,35]: #TESTING
        if np.mod(t,1)==0: print(f'current time: {t}')
        (w_values, qv_values, qc_values, th_values),zlevels=average_clouds(t,vars) #already includes all variables

    # if zerowthresh==False:
        # output_file=dir+f'tracking_algorithms/plots/h5/cloud_BFS_{type}_{job_id}.h5'
    if zerowthresh==True:
        output_file=dir+f'tracking_algorithms/plots/h5/cloud_BFS_{type}_{job_id}w>=0.h5'
    with h5py.File(output_file, 'w') as hdf: 
        hdf.create_dataset('w_values', data=w_values)
        hdf.create_dataset('qv_values', data=qv_values)
        hdf.create_dataset('qc_values', data=qc_values)
        hdf.create_dataset('th_values', data=th_values)
        hdf.create_dataset('zlevels', data=zlevels)
print('done')

