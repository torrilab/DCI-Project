#FULL DOMAIN RUN

# code for tracing particles back to SBZ draft (python version 3.10.9) (not optimized with numpy.where)
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import os; import time

start_time = time.time();

#data loading
################################################################################################################################################################################################################
dir='/mnt/lustre/koa/koastore/torri_group/air_directory/'
data=xr.open_dataset(dir+'cm1r20.3/run/cm1out_test7tundra-7_062217.nc') #***
times=data['time'].values/(1e9 * 60); times=times.astype(float);
parcel=xr.open_dataset(dir+'cm1r20.3/run/cm1out_pdata_test5tundra-7_062217.nc') #***
whereCL=xr.open_dataset(dir+'tracking_algorithms/whereCL_4_0622.nc').load() #***
whereCL=whereCL.isel(time=slice(0,len(data['time'])))
kms=np.argmax(data['xh'].values-data['xh'][0].values >= 1)

####################################################################################
# IF LIMITING TO INVESTIGATE SEABREEZE, UNCOMMENT THIS SECTION
#LIMITING TIME
#t in (0,50)
data=data.isel(time=slice(0,50))

#LIMITING X
#x in (-20,100) ==> (256-20,256+100) #### how to limit xh and xf in data
xf_range=slice(int(256*kms)-20,int(256*kms)+100)
xh_range=slice(int(256*kms)-20,int(256*kms)+100)
data=data.isel(xf=xf_range,xh=xh_range)

# #TESTING
# # data['qvflux'].isel(time=49).plot()
# data['qvflux'].isel(time=50,xh=slice(0,356)).plot()
# plt.axvline(-20,color='white')
# plt.axvline(100-2,color='white')
####################################################################################

#job array things
################################################################################################################################################################################################################

num_jobs=60 #how many total jobs are being run? i.e. array=1-100 ==> num_jobs=100 #***

job_id = int(os.environ.get('SLURM_ARRAY_TASK_ID', 0)) #this is the current SBATCH job id
if job_id==0: job_id=1
num_parcels=len(parcel['xh']) #total number of parcels
job_range = num_parcels//num_jobs #number of parcels per job 

# Calculate start and end based on job_id
start_job = (job_id - 1) * job_range
end_job = start_job + job_range
if job_id==num_jobs: end_job=num_parcels
print(f'running for parcels {start_job}-{end_job-1}')
parcel=parcel.isel(xh=slice(start_job,end_job)) #slices the lagrangian parcel data
index_adjust=parcel['xh'].values.astype(int)[0]-1 #for correction of parcel index name



#code for tracing particles back to SBZ draft (python version 3.10.9) 
#(1) row each row in pinfo:
#(2) if pinfo[row,3]>pinfo[row,4], then find that particle in data and trace back to when w<0.1 m/s
#(3) then report max value of convergence within 2kmx2km box

#initialization
################################################################################################################################################################################################################
w_thresh=1e-1/1000 #1e-4 km/s == 0.1 m/s
CLmaxheight=750
ascend_thresh=0e-1/1000
ascend_percent=1.00 #0.00 0.25 #0.50
ascend=np.argmax(times >= 5) #founds how many timesteps is 5 minutes simulation time (always 1 if data timestep > 10)

starttime= 0 
################################################################################################################################################################################################################

def get_3dtime_data(data,varname,tlev):
    cloud_var=data[varname].isel(time=tlev).values
    return cloud_var 

#--------------Function that collects important data for all parcels at time t
def parcel_info(parcel,data,t,visited_edit): #info for all parcels at single time
    #--------------Finds all parcel locations at time t 
    x=parcel['x'].isel(time=t).values/1000; xf=data['xf'].values; which_x=np.searchsorted(xf,x)-1; which_x[which_x==-1]=0 #finds which x layer parcel in
    y=parcel['y'].isel(time=t).values/1000; yf=data['yf'].values; which_y=np.searchsorted(yf,y)-1; which_y[which_y==-1]=0 #finds which y layer parcel in
    z=parcel['z'].isel(time=t).values/1000; #zf=data['zf'].values; which_z=np.searchsorted(zf,z)-1; which_z[which_z==-1]=0

    #--------------Saves important data 
    #Only looks at parcels that have not been visited before
    looprange=[ind for ind in range(len(parcel['xh'])) if ind not in visited_edit]
    #Initialize storage array 
    pinfo=np.zeros((len(parcel['xh']),6),dtype='object') #num,x,y,z, LFC, LCL
    #Runs through each indicies
    for ind in looprange: 
        #Find LFC levels 
        lfc=data['lfc'].isel(time=t,xh=which_x[ind],yh=which_y[ind]).values/1000;
        lcl=data['lcl'].isel(time=t,xh=which_x[ind],yh=which_y[ind]).values/1000;
        
        # #If LFC is a NAN value, use average of surrounding 10x10 box of LFC values (-don't use-)
        # if lfc<0:
        #     # print(f'no lfc value available for parcel {num} at time {t}. using neighboring lfc average.')
        #     xrange=np.mod(np.arange(which_x[ind]-10,which_x[ind]+10),len(data['xh'])); yrange=np.mod(np.arange(which_y[ind]-10,which_y[ind]+10),len(data['yh'])); 
        #     lfc=data['lfc'].isel(time=t,xh=xrange,yh=yrange).mean().values/1000
        # #If LCL is a NAN value, use average of surrounding 10x10 box of LFC values
        # if lcl<0:
        #     # print(f'no lcl value available at time {t} for parcel {num}. using neighboring lfc.')
        #     xrange=np.mod(np.arange(which_x[ind]-10,which_x[ind]+10),len(data['xh'])); yrange=np.mod(np.arange(which_y[ind]-10,which_y[ind]+10),len(data['yh'])); 
        #     lcl=data['lcl'].isel(time=t,xh=xrange,yh=yrange).mean().values/1000   
        
        #--------------Saves the variables 
        #parcel_num, whichx, whichy, whichz, whichlfc, whichlcl
        pinfo[ind,0]=ind; pinfo[ind,1]=which_x[ind]; 
        pinfo[ind,2]=which_y[ind]; pinfo[ind,3]=z[ind]; pinfo[ind,4]=lfc
        pinfo[ind,5]=lcl #marks tracer number at individual columns
    pinfo=pinfo[~(pinfo == 0).all(axis=1)]
    return(pinfo)

#--------------Function that collects important data for a single parcel_num at time t
def parcel_info_single(parcel,data,t,num): #info for single parcels at single time
     #--------------Finds parcel location at time t 
    x=parcel['x'].isel(time=t,xh=num).values/1000; xf=data['xf'].values; which_x=np.searchsorted(xf,x)-1; 
    if which_x==-1: which_x=0 #finds which x layer parcel in
    y=parcel['y'].isel(time=t,xh=num).values/1000; yf=data['yf'].values; which_y=np.searchsorted(yf,y)-1; 
    if which_y==-1: which_y=0 #finds which y layer parcel in
    z=parcel['z'].isel(time=t,xh=num).values/1000; zf=data['zf'].values; which_z=np.searchsorted(zf,z)-1; 
    if which_z==-1: which_z=0
    
    #--------------Saves important data 
    #Gets parcel velocities
    # w=parcel['w'].isel(time=t,xh=num).values/1000; #OLD
    w=data['w'].isel(time=t,xh=which_x,yh=which_y).interp(zf=data['zh']).isel(zh=which_z)/1000 #NEW


    #Find LFC levels
    lfc=data['lfc'].isel(time=t,xh=which_x,yh=which_y).values/1000; 
    lcl=data['lcl'].isel(time=t,xh=which_x,yh=which_y).values/1000;
    # #If LFC is a NAN value, use average of surrounding 10x10 box of LFC values (-don't use-)
    # if lfc<0:
    #     xrange=np.mod(np.arange(which_x-10,which_x+10),len(data['xh'])); yrange=np.mod(np.arange(which_y-10,which_y+10),len(data['yh'])); 
    #     lfc=data['lfc'].isel(time=t,xh=xrange,yh=yrange).mean().values/1000
    # #If LCL is a NAN value, use average of surrounding 10x10 box of LFC values
    # if lcl<0:
    #     xrange=np.mod(np.arange(which_x-10,which_x+10),len(data['xh'])); yrange=np.mod(np.arange(which_y-10,which_y+10),len(data['yh'])); 
    #     lcl=data['lcl'].isel(time=t,xh=xrange,yh=yrange).mean().values/1000   
    
    #--------------Saves the variables 
    #parcel_num, whichx, whichy, whichz, whichlfc, whichlcl
    pinfo_s=np.zeros((1,8+1),dtype='object') #parcel_num,x,y,z, LFC, LCL, u, v, w
    pinfo_s[0,0]=num; pinfo_s[0,1]=which_x; pinfo_s[0,2]=which_y; pinfo_s[0,3]=z; pinfo_s[0,4]=lfc
    pinfo_s[0,5]=lcl; pinfo_s[0,6]=w; pinfo_s[0,7]=which_z; pinfo_s[0,8]=x #marks tracer number,which_x,which_y,z,lfc,lcl,u,v, and w at individual columns
    return(pinfo_s)

################################################################################################################################################################################################################
visited=[] #marks parcel_num that has been visited already
out_arr=np.zeros((len(parcel['xh']),6),dtype='object') #stores parcel_num,x,y,z,time
save_arr=np.zeros((len(parcel['xh']),6),dtype='object') #saves "forgotten" parcels

#1--------------Looping over time
for t in range(starttime,len(whereCL['time'].values)):
    if np.mod(t,10)==0: print(f'current time step: {t}')
    
    #Remove visited parcels from pinfo 
    #And loads parcel_info for all parcels
    ###################################################################################################################################
    visited_edit=[num for num in visited if num in pinfo[:, 0]] #parcel number to delete that are stored in pinfo
    pinfo=parcel_info(parcel,data,t,visited_edit) #array storing information about all parcels
    ###################################################################################################################################
  
    #2--------------Runs through each parcel
    for ind in range(pinfo.shape[0]):

        if pinfo[ind,4] < 0: #new***
            print(f'LFC is negative, forgetting parcel')
            visited.append(pinfo[ind,0]) #adds the parcel to forget to visited to 
            continue
        
        #3--------------If parcel is within 1000m of the LFC, check ascent for several timesteps afterwards
        if (pinfo[ind,4] <= pinfo[ind,3] <= pinfo[ind,4] + 1000/1000) and pinfo[ind,4]>0: #if above LFC (LFC must have a value)
            # above_LFC+=1 #TESTING
            
            #check if parcel continues to ascend for at least 30 minutes simulation time
            #checks if for ascend_percent % of 60 minutes, w is positive
            ascend_range=np.arange(t+1,t+1+ascend,1); ascend_range=ascend_range[ascend_range<len(times)]
            if np.any(ascend_range): ascend_array=parcel['w'].isel(time=ascend_range,xh=pinfo[ind,0]).values/1000
            
            #4--------------If parcel ascends (w>ascend_thresh) for ascend_percent% for ascend timesteps, track back in time
            if np.sum(ascend_array >= ascend_thresh)/len(ascend_array) >= ascend_percent:
                #trace back in time until w<thresh or reach t=0 without w>thresh
                for back_t in np.arange(t-1, starttime-1, -1): #counts from current time down to starttime 
                    
                    #gets info of current parcel
                    pinfo_s=parcel_info_single(parcel,data,back_t,pinfo[ind,0]) 

                    #if current parcel leaves the boundaries, forgets and saves parcel
                    ###################################################################################################################################
                    if pinfo_s[0,8]+pinfo_s[0,6]>np.max(data['xf'].values) or pinfo_s[0,3]+pinfo_s[0,6]>np.max(data['zf'].values): #x is radiative, z non-periodic, forget parcel
                        print(f'parcel {pinfo[ind,0]} crossed x,y,or,z boundary, will forget')
                        visited.append(pinfo[ind,0]) #adds the parcel to forget to visited to delete at next time step
                        break                
                    ###################################################################################################################################

                    #5--------------Tracks when parcel slows down enough to be in gust front (and below 750 m)
                    ###################################################################################################################################
                    #checks if parcel w < w_thresh
                    if pinfo_s[0,6]<w_thresh: 
                        #if parcel is above 750m (or LCL), forget parcel, and move on
                        if pinfo_s[0,3]>=CLmaxheight/1000: 
                            
                            print(f'parcel {pinfo[ind,0]} is above PBL when w < {w_thresh*1000} m/s')
                            #forget parcels that slow down too high up in boundary layer
                            visited.append(pinfo[ind,0]) #adds the parcel to forget to visited to delete at next time step
                            # save_arr[ind,0]=pinfo_s[0,0];save_arr[ind,1]=pinfo_s[0,1];save_arr[ind,2]=pinfo_s[0,2];
                            # save_arr[ind,3]=pinfo_s[0,3];save_arr[ind,4]=back_t;save_arr[ind,5]=t;  #stores parcel num,x,y,z,back_t,t
                            break
                        #6--------------if parcel below 750m (or LCL), check data for max convergence within 2km
                        elif pinfo_s[0,3]<CLmaxheight/1000: #if parcel below 750m (or LCL), check data for max convergence within 2km
                            print(f'parcel {pinfo[ind,0]} w < {w_thresh*1000} m/s at time and below LCL = {back_t}')
                            visited.append(pinfo[ind,0]) #append the visited particle number to delete at next time step #comment if previous append uncommented
                            
                            #Get the data for the x grid location for the CL (at t,z,y)
                            ###################################################################################################################################
                            maxconv_x=whereCL.isel(time=back_t,z=pinfo_s[0,7],y=pinfo_s[0,2])['maxconv_x'].values; #(z level must be < 5)
                            maxconv_x=maxconv_x[maxconv_x>=0] #get rid of non-max nan values (-1)
                            print(f'Current Parcel Info: {pinfo_s}')              
                            ###################################################################################################################################                                              
                            
                            #7--------------Store parcel if parcel is within 2 km of the CL in the x direction
                            ###################################################################################################################################
                            kms=np.argmax(data['xh'].values-data['xh'][0].values >= 1) #finds how many x grids is 1 km
                            tf=np.any(np.isin(maxconv_x, np.arange(pinfo_s[0,1]-2*kms,pinfo_s[0,1]+3*kms)))
                            #checks if the x,y CL indicies match the x,y incidicies of the current parcel
                            if tf==True: #if there is an incidies match with max CL indicies, save parcel
                                print(f'parcel {pinfo[ind,0]} is near CL at t = {back_t}. parcel saved.')
                                out_arr[ind,0]=pinfo_s[0,0];out_arr[ind,1]=pinfo_s[0,1];out_arr[ind,2]=pinfo_s[0,2];
                                out_arr[ind,3]=pinfo_s[0,3];out_arr[ind,4]=back_t;out_arr[ind,5]=t;  #stores parcel num,x,y,z,back_t,t
                                # visited.append(pinfo[ind,0]) #append the visited particle number to delete at next time step #uncomment if previous append commented
                            elif tf==False:
                                #saves parcels that encountered non-CL updraft
                                print(f"parcel number {pinfo_s[0,0]} at time {back_t} saved")
                                save_arr[ind,0]=pinfo_s[0,0];save_arr[ind,1]=pinfo_s[0,1];save_arr[ind,2]=pinfo_s[0,2];
                                save_arr[ind,3]=pinfo_s[0,3];save_arr[ind,4]=back_t;save_arr[ind,5]=t;  #stores parcel num,x,y,z,back_t,t
                            break                
                             ###################################################################################################################################
                    ###################################################################################################################################
    # if np.mod(t,10)==0: print(f'number of parcels above LFC: {above_LFC}') #TESTING
###################################################################################################################################

#Storing output and save data
###################################################################################################################################
out_arr[np.where(np.any(out_arr != 0, axis=1))[0],0]+=index_adjust #*needed for job array*+=index_adjust #*needed for job array*
save_arr[np.where(np.any(save_arr != 0, axis=1))[0],0]+=index_adjust #*needed for job array*+=index_adjust #*needed for job array*
ds=xr.Dataset({
    'out_arr': (['rows', 'columns'], out_arr.astype(float)),
    'save_arr': (['rows', 'columns'], save_arr.astype(float)),
})
ds.to_netcdf(dir+'tracking_algorithms/trackout/SBZlimited_parcel_tracking'+str(job_id)+'.nc') #*needed for job array*
###################################################################################################################################
end_time = time.time(); elapsed_time = end_time - start_time; print(f"Total Elapsed Time: {elapsed_time} seconds")  
#2d5m10,000p30j: 26 minutes
#2d5m125,00030j: max 50-370 minutes (recommended use 500-1000 job arrays for 10 days)