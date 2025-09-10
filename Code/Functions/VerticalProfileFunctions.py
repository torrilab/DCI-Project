#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np


# In[ ]:


#EXAMPLE THRESHOLD-BASED EULERIAN VERTICAL PROFILE CODE
# def final_profile(var,type):
#     global w_thresh
#     #thresholds
#     w_thresh=1; w_thresh=0.5 #TESTING***
#     qcqithresh=1e-6; qcqithresh=1e-9 #TESTING***

#     nt=len(data['time'])
        
#     #get qc and interpolated w 

#     # finds regions that match the threshold
#     if type=="general":
#         where_updraft=np.where((w_data>=w_thresh)) #uncomment for "general updraft"
#     elif type=='cloudy': 
#         where_updraft=np.where((w_data>=w_thresh) & (qc_plus_qi>=qcqithresh)) #uncomment for "cloudy updraft" 
    
#     #creates profile storage and adds z column    
#     zhs=data['zh'].values
#     profile_array=np.zeros((len(zhs), 3)) #column 1: var, column 2: counter, column 3: list of zhs
#     profile_array[:,2]=zhs

#     #get incidies associated with threshold mask
#     t_ind, z_ind, y_ind, x_ind = where_updraft

#     #gets data associated with threshold mask
#     if var=='w':
#         masked_data=w_data[where_updraft]
#     if var=='qv':
#         masked_data=qv_data[where_updraft]
#     if var=='qc':
#         masked_data=qc_plus_qi[where_updraft] #data stored for qc is actually qc+qi
#     if var=='qi':
#         masked_data=qi_data[where_updraft]
#     if var=='th':
#         masked_data=th_data[where_updraft]
#     if var=='th_e':
#         masked_data=theta_e_data[where_updraft]
#     if var=='buoyancy':
#         masked_data=buoyancy_data[where_updraft]
        
#     #converts qv and qc from kg/kg=>g/kg
#     if var in ['qv','qc','qi']:
#         masked_data*=1000

#     #bin masked values by z level
#     for (kh,value) in zip(z_ind,masked_data):
#         profile_array[kh,0]+=value #adds data to first column
#         profile_array[kh,1]+=1 #adds +1 counter to 2nd column
#     return profile_array


# In[ ]:


#EXAMPLE VERTICAL PROFILE FUNCTION FOR TRACKED PARCELS
# def CL_tracked_profile(var_data,type):
#     after=4 #20 minutes

#     if type=='all':
#         out_nz=ALL_out_nz.copy()
#     if type=='deep':
#         out_nz=DEEP_out_nz.copy()
#     if type=='shallow':
#         out_nz=SHALLOW_out_nz.copy()
    
#     zhs=data['zh'].values
#     profile_array =np.zeros((len(zhs), 3)) #column 1: var, column 2: counter, column 3: list of zhs
#     profile_array[:,2]=zhs;
    
#     for row in range(out_nz.shape[0]):
#         p=out_nz[row,0]
        
#         # ts=np.arange(out_nz[row,4],out_nz[row,5]+1 + after)
#         ts_end = min(out_nz[row, 5] + 1 + after, len(data['time'])) #this takes care of exceeding buffers
#         ts = np.arange(out_nz[row, 4], ts_end)
        
#         zs=Z[ts,p]
#         ys=Y[ts,p]
#         xs=X[ts,p]
#         for t, z, y, x in zip(ts, zs, ys, xs):
#             var=var_data[t,z,y,x]
#             profile_array[z,0]+=var;profile_array[z,1]+=1
#     return profile_array


# In[ ]:


def averaged_profiles(profile):
    out_var=profile[ (profile[:, 1] != 0)]; #gets rid of rows that have no data
    out_var=np.array([out_var[:, 0] / out_var[:, 1], out_var[:, 2]]).T #divides the data column by the counter column
    return out_var


# In[ ]:


def average_difference(array1, array2):
    out_var_one=averaged_profiles(array1)
    out_var_two=averaged_profiles(array2)

    #masking out non matches
    second_col_one = out_var_one[:, 1]
    second_col_two = out_var_two[:, 1]
    mask_one = np.isin(second_col_one, second_col_two)
    mask_two = np.isin(second_col_two, second_col_one)
    
    out_var_one = out_var_one.copy()[mask_one]
    out_var_two = out_var_two.copy()[mask_two]
    
    diff=(out_var_one[:,0]-out_var_two[:,0])
    zs=out_var_one[:,1]

    out_profile=np.zeros((len(diff),2))

    out_profile[:,0]=diff;out_profile[:,1]=zs;
    return out_profile

