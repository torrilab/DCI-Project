.. code:: ipython3

    #THIS FUNCTION IS FOR RUNNING WITH SLURM JOB ARRAY
    #(SPLITS UP JOB_ARRAY BELOW INTO EVEN MORE TASKS)
    def StartSlurmJobArray(num_jobs,num_slurm_jobs, ISRUN):
        job_id = int(os.environ.get('SLURM_ARRAY_TASK_ID', 0)) #this is the current SBATCH job id
        if job_id==0: job_id=1
        if ISRUN==False:
            start_job=1;end_job=num_jobs
            return start_job,end_job
        total_elements=num_jobs #total num of variables
    
        job_range = total_elements // num_slurm_jobs  # Base size for each chunk
        remaining = total_elements % num_slurm_jobs   # Number of chunks with 1 extra 
        
        # Function to compute the start and end for each job_id
        def get_job_range(job_id, num_slurm_jobs):
            job_id-=1
            # Add one extra element to the first 'remaining' chunks
            start_job = job_id * job_range + min(job_id, remaining)
            end_job = start_job + job_range + (1 if job_id < remaining else 0)
        
            if job_id == num_slurm_jobs - 1: 
                end_job = total_elements 
            return start_job, end_job
        # def job_testing():
        #     #TESTING
        #     start=[];end=[]
        #     for job_id in range(1,num_slurm_jobs+1):
        #         start_job, end_job = get_job_range(job_id)
        #         print(start_job,end_job)
        #         start.append(start_job)
        #         end.append(end_job)
        #     print(np.all(start!=end))
        #     print(len(np.unique(start))==len(start))
        #     print(len(np.unique(end))==len(end))
        # job_testing()
    
        # if sbatch==True:
            
        start_job, end_job = get_job_range(job_id, num_slurm_jobs)
        index_adjust=start_job
        # print(f'start_job = {start_job}, end_job = {end_job}')
        if start_job==0: start_job=1
        if end_job==total_elements: end_job+=1
        return start_job,end_job
    
    # job_id=1
    # [start_slurm_job,end_slurm_job,slurm_index_adjust]=StartSlurmJobArray(num_jobs,num_slurm_jobs,ISRUN)
    # parcel=parcel1.isel(xh=slice(start_job,end_job))

.. code:: ipython3

    #Loading in Packages and Data
    
    #Importing Packages
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
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
    
    # Importing Model Data
    check=False
    dir='/mnt/lustre/koa/koastore/torri_group/air_directory/DCI-Project/'
    
    # # dx = 1 km; Np = 1M; Nt = 5 min
    # data1=xr.open_dataset(dir+'../cm1r20.3/run/cm1out_1km_5min.nc') #***
    # parcel1=xr.open_dataset(dir+'../cm1r20.3/run/cm1out_pdata_1km_5min_1e6.nc') #***
    # res='1km';t_res='5min'
    # Np_str='1e6'
    
    # dx = 1km; Np = 50M
    #Importing Model Data
    check=False
    dir2='/home/air673/koa_scratch/'
    data1=xr.open_dataset(dir2+'cm1out_1km_1min.nc') #***
    parcel1=xr.open_dataset(dir2+'cm1out_pdata_1km_1min_50M.nc') #***
    res='1km'; t_res='1min'; Np_str='50e6'
    
    # # dx = 1km; Np = 100M
    # #Importing Model Data
    # check=False
    # dir2='/home/air673/koa_scratch/'
    # data1=xr.open_dataset(dir2+'cm1out_1km_1min.nc') #***
    # parcel1=xr.open_dataset(dir2+'cm1out_pdata_1km_1min_100M.nc') #***
    # res='1km'; t_res='1min'; Np_str='100e6'
    
    # #uncomment if using 250m data
    # #Importing Model Data
    # check=False
    # dir2='/home/air673/koa_scratch/'
    # data1=xr.open_dataset(dir2+'cm1out_250m.nc') #***
    # # # parcel1=xr.open_dataset(dir2+'cm1out_pdata_250m.nc') #***

.. code:: ipython3

    times=data1['time'].values/(1e9 * 60); times=times.astype(float);
    minutes=1/times[1] #1 / minutes per timestep = timesteps per minute
    kms=np.argmax(data1['xh'].values-data1['xh'][0].values >= 1)

.. code:: ipython3

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
    
    # # Get all functions in NumericalFunctions
    # import inspect
    # functions = [f[0] for f in inspect.getmembers(PlottingFunctions, inspect.isfunction)]
    # functions

.. code:: ipython3

    ########################
    #READING BACK IN
    def LoadFinalData(in_file):
        dict = {}
        with h5py.File(in_file, 'r') as f:
            for key in f.keys():
                dict[key] = f[key][:]
        return dict
    
    def LoadAllCloudBase():
        dir2 = dir + f'Project_Algorithms/Tracking_Algorithms/'
        in_file = dir2 + f"all_cloudbase_{res}_{t_res}_{Np_str}.pkl"
        with open(in_file, 'rb') as f:
            all_cloudbase = pickle.load(f)
        return(all_cloudbase)
    min_all_cloudbase=np.nanmin(LoadAllCloudBase())
    print(f"Minimum Cloudbase is: {min_all_cloudbase}\n")
    
    dir2 = dir + f'Project_Algorithms/Tracking_Algorithms/'
    in_file=dir2+f"parcel_tracking_SUBSET_{res}_{t_res}_{Np_str}"
    final_dict=LoadFinalData(in_file)
    
    
    #DYNAMICALLY CREATING VARIABLES
    for key, value in final_dict.items():
        globals()[key] = value
    
    # #DYNAMICALLY PRINTING VARIABLE SIZES
    # for key in final_dict:
    #     print(f"{key} has {final_dict[key].shape[0]} parcels")
    
    # PRINTING VARIABLE SIZES (ONE BY ONE)
    print(f'ALL: {len(CL_ALL_out_arr)} CL parcels and {len(nonCL_ALL_out_arr)} nonCL parcels')
    print(f'SHALLOW: {len(CL_SHALLOW_out_arr)} CL parcels and {len(nonCL_SHALLOW_out_arr)} nonCL parcels')
    print(f'DEEP: {len(CL_DEEP_out_arr)} CL parcels and {len(nonCL_DEEP_out_arr)} nonCL parcels')
    print('\n')
    print(f'ALL: {len(SBZ_ALL_out_arr)} SBZ parcels and {len(nonSBZ_ALL_out_arr)} nonSBZ parcels')
    print(f'SHALLOW: {len(SBZ_SHALLOW_out_arr)} SBZ parcels and {len(nonSBZ_SHALLOW_out_arr)} nonSBZ parcels')
    print(f'DEEP: {len(SBZ_DEEP_out_arr)} SBZ parcels and {len(nonSBZ_DEEP_out_arr)} nonSBZ parcels')
    print('\n')
    print(f'ALL: {len(ColdPool_ALL_out_arr)} ColdPool parcels')
    print(f'SHALLOW: {len(ColdPool_SHALLOW_out_arr)} ColdPool parcels')
    print(f'DEEP: {len(ColdPool_DEEP_out_arr)} ColdPool parcels')
    
    
    def apply_job_array_filter(start_job, end_job):
        # print("APPLYING JOB ARRAY")
    
        def job_filter(arr):
            return arr[(arr[:, 0] >= start_job) & (arr[:, 0] < end_job)]
    
        target_names = [
            'CL_ALL_out_arr', 'nonCL_ALL_out_arr',
            'CL_SHALLOW_out_arr', 'nonCL_SHALLOW_out_arr',
            'CL_DEEP_out_arr', 'nonCL_DEEP_out_arr',
            'SBZ_ALL_out_arr', 'nonSBZ_ALL_out_arr',
            'SBZ_SHALLOW_out_arr', 'nonSBZ_SHALLOW_out_arr',
            'SBZ_DEEP_out_arr', 'nonSBZ_DEEP_out_arr',
            'ColdPool_ALL_out_arr', 'ColdPool_SHALLOW_out_arr', 'ColdPool_DEEP_out_arr'
        ]
    
        for name in target_names:
            globals()[name+'_2'] = job_filter(globals()[name])


.. parsed-literal::

    Minimum Cloudbase is: 1.2463867664337158
    
    ALL: 1626279 CL parcels and 1309531 nonCL parcels
    SHALLOW: 1183083 CL parcels and 1022774 nonCL parcels
    DEEP: 146770 CL parcels and 117460 nonCL parcels
    
    
    ALL: 109090 SBZ parcels and 1517189 nonSBZ parcels
    SHALLOW: 58778 SBZ parcels and 1124305 nonSBZ parcels
    DEEP: 26208 SBZ parcels and 120562 nonSBZ parcels
    
    
    ALL: 1517189 ColdPool parcels
    SHALLOW: 1124305 ColdPool parcels
    DEEP: 120562 ColdPool parcels


.. code:: ipython3

    ##############################################
    #SETUP 

.. code:: ipython3

    def MakeDictionary(**vars):
        return vars
        
    def GetData1(start_job,end_job):
        dir2=dir+'Project_Algorithms/Lagrangian_Arrays/'
        in_file=dir2+f'lagrangian_binary_array_{res}_{t_res}_{Np_str}.h5'
        
        var_names = ['W', 'QCQI']
        data_dict = make_data_dict(in_file,var_names,read_type,start_job,end_job)
        W, QCQI = (data_dict[k] for k in var_names)
        
        # #Making Time Matrix
        # rows, cols = A.shape[0], A.shape[1]
        # T = np.arange(rows).reshape(-1, 1) * np.ones((1, cols), dtype=int)
        
        dir2=dir+'Project_Algorithms/Lagrangian_Arrays/'
        in_file=dir2+f'VARS_binary_array_{res}_{t_res}_{Np_str}.h5'
        
        var_names = ['QV','TH','TH_E','BUOYANCY','HMC']
        data_dict = make_data_dict(in_file,var_names,read_type,start_job,end_job)
        QV, TH, TH_E, BUOYANCY, HMC = [data_dict[k] for k in var_names]
    
        VARs=MakeDictionary(W=W, QCQI=QCQI, QV=QV, 
                            TH=TH, TH_E=TH_E, BUOYANCY=BUOYANCY, HMC=HMC)
        return VARs
    
    def GetData2(start_job,end_job):
        dir2=dir+'Project_Algorithms/Lagrangian_Arrays/'
        in_file=dir2+f'VARS_binary_array_{res}_{t_res}_{Np_str}.h5'
        
        var_names = ['VMF_c','VMF_g']
        data_dict = make_data_dict(in_file,var_names,read_type,start_job,end_job)
        VMF_c, VMF_g = [data_dict[k] for k in var_names]
        
        dir2=dir+'Project_Algorithms/Lagrangian_Arrays/'
        in_file=dir2+f'ED_binary_array_{res}_{t_res}_{Np_str}.h5'
        
        var_names = ['E_G','E_C','D_C','D_G']
        data_dict = make_data_dict(in_file,var_names,read_type,start_job,end_job)
        E_G, E_C, D_C, D_G = (data_dict[k] for k in var_names)
    
        NET_G, NET_C = E_G-D_G, E_C-D_C
    
        VARs=MakeDictionary(VMF_c=VMF_c, VMF_g=VMF_g, E_G=E_G, E_C=E_C, D_C=D_C, D_G=D_G, NET_G=NET_G, NET_C=NET_C)
        return VARs

.. code:: ipython3

    ################################
    #DATA SETUP
    ################################
    #*#*
    data_type="Tracked_Properties_Histogram" 
    data_type="Tracked_Entrainment_VMF_Histogram"
    
    if data_type=="Tracked_Properties_Histogram":
        GetData=GetData1
        variables = ["W","QCQI","QV","TH","TH_E","BUOYANCY","HMC"]
    elif data_type=="Tracked_Entrainment_VMF_Histogram":
        GetData=GetData2
        variables = ["VMF_c","VMF_g","E_G","E_C","D_C","D_G","NET_G","NET_C"]
    ##############################

.. code:: ipython3

    ################################
    #JOB ARRAY SETUP
    ################################
    #*#*
    # how many total jobs are being run? i.e. array=1-100 ==> num_jobs=100
    # num_jobs=60 #1M parcels
    num_jobs=300 #50M parcels
    ##############################

.. code:: ipython3

    ##############################################
    #DATA LOADING FUNCTIONS

.. code:: ipython3

    #JOB ARRAY SETUP
    def StartJobArray(job_id,num_jobs):
        total_elements=len(parcel1['xh']) #total num of variables
    
        if num_jobs >= total_elements:
            raise ValueError("Number of jobs cannot be greater than or equal to total elements.")
        
        job_range = total_elements // num_jobs  # Base size for each chunk
        remaining = total_elements % num_jobs   # Number of chunks with 1 extra 
        
        # Function to compute the start and end for each job_id
        def get_job_range(job_id, num_jobs):
            job_id-=1
            # Add one extra element to the first 'remaining' chunks
            start_job = job_id * job_range + min(job_id, remaining)
            end_job = start_job + job_range + (1 if job_id < remaining else 0)
        
            if job_id == num_jobs - 1: 
                end_job = total_elements #- 1
            return start_job, end_job
        # def job_testing():
        #     #TESTING
        #     start=[];end=[]
        #     for job_id in range(1,num_jobs+1):
        #         start_job, end_job = get_job_range(job_id)
        #         print(start_job,end_job)
        #         start.append(start_job)
        #         end.append(end_job)
        #     print(np.all(start!=end))
        #     print(len(np.unique(start))==len(start))
        #     print(len(np.unique(end))==len(end))
        # job_testing()
    
        # if sbatch==True:
        #     job_id = int(os.environ.get('SLURM_ARRAY_TASK_ID', 0)) #this is the current SBATCH job id
        #     if job_id==0: job_id=1
            
        start_job, end_job = get_job_range(job_id, num_jobs)
        index_adjust=start_job
        # print(f'start_job = {start_job}, end_job = {end_job}')
        return start_job,end_job,index_adjust
    
    # job_id=1
    # [start_job,end_job,index_adjust]=StartJobArray(job_id,num_jobs)
    # parcel=parcel1.isel(xh=slice(start_job,end_job))

.. code:: ipython3

    # Reading Back Data Later
    ##############
    def make_data_dict(in_file,var_names,read_type,start_job,end_job):
        if read_type=='h5py':
            with h5py.File(in_file, 'r') as f:
               data_dict = {var_name: f[var_name][:,start_job:end_job] for var_name in var_names}
                
        elif read_type=='xarray':
            in_data = xr.open_dataset(
                in_file,
                engine='h5netcdf',
                phony_dims='sort',
                chunks={'phony_dim_0': 100, 'phony_dim_1': 1_000_000} 
            )
            data_dict = {k: in_data[k][:,start_job:end_job].compute().data for k in var_names}
        return data_dict
    
    # read_type='xarray'
    read_type='h5py'

.. code:: ipython3

    def GetSpatialData(start_job,end_job):
        dir2=dir+'Project_Algorithms/Lagrangian_Arrays/'
        in_file=dir2+f'lagrangian_binary_array_{res}_{t_res}_{Np_str}.h5'
        
        var_names = ['Z', 'Y', 'X', 'z']
        data_dict = make_data_dict(in_file,var_names,read_type,start_job,end_job)
        Z, Y, X, parcel_z = (data_dict[k] for k in var_names)
        
        # #Making Time Matrix
        # rows, cols = A.shape[0], A.shape[1]
        # T = np.arange(rows).reshape(-1, 1) * np.ones((1, cols), dtype=int)
        
        return Z,Y,X,parcel_z

.. code:: ipython3

    ################################################################################

.. code:: ipython3

    ##############################################
    #MAKE PROFILES FUNCTIONS

.. code:: ipython3

    #HISTOGRAM BIN SETTINGS
    ####################################
    def GetBinSettings(var_name):    
    
        pre_calculated=False
        pre_calculated=True
    
        if pre_calculated==False:
            bin_settings = {
                'W':        (W.min(), W.max(), 1000),
                'QV':       (QV.min(), QV.max(), 1000),
                'QCQI':     (QCQI.min(), QCQI.max(), 1000),
                'TH':       (TH.min(), TH.max(), 5000),
                'TH_E':     (TH_E.min(), TH.max(), 5000),
                'BUOYANCY': (BUOYANCY.min(), BUOYANCY.max(), 1000),
                'HMC':      (HMC.min(), HMC.max(), 1000),
            }
        elif pre_calculated==True:
            bin_settings = {
                'W': (-18.99606, 47.273865, 1000),
                'QV': (9.235839e-07, 0.022054985, 1000),
                'QCQI': (0.0, 0.0061959606, 1000),
                'TH': (297.87912, 463.44125, 5000),
                'TH_E': (324.8358, 463.43524, 5000),
                'BUOYANCY': (-0.78747416, 0.599328, 1000),
                'HMC': (-0.00031354488, 0.0001856628, 1000),
                'E_C': (0, 7e-3, 1000),
                'D_C': (0, 7e-3, 1000),
                'E_G': (0, 2e-2, 1000),
                'D_G': (0, 2e-2, 1000),
                'D_G': (0, 2e-2, 1000),
                'VMF_C': (-2, 7, 1000),
                'VMF_G': (-2, 4, 1000),
            }
    
        
        # Select bin range based on var_name
        if var_name is not None and var_name in bin_settings:
            bin_left, bin_right, num_bins = bin_settings[var_name]
        else:
            # fallback default
            bin_left, bin_right, num_bins = -50, 50, 1000
        return bin_left,bin_right,num_bins

.. code:: ipython3

    def TrackedHistogram(var_data,var_name, Z,Y,X, type,type2):
        global index_adjust
        out_arr=globals()[f"{type2}_{type.upper()}_out_arr"+"_2"].copy()
    
        zhs=data1['zh'].values
        # profile_array =np.zeros((len(zhs), 3)) #column 1: var, column 2: counter, column 3: list of zhs
        # profile_array[:,2]=zhs;
    
        [bin_left,bin_right,num_bins]=GetBinSettings(var_name) 
        # if var_name=='th': #TESTING
        #     bin_left=var_data.min();bin_right=var_data.max() 
        profile_array =np.zeros((len(zhs), num_bins)) #TESTING***
        bin_list=np.linspace(bin_left,bin_right,num_bins)
        
        for row in range(out_arr.shape[0]):
            after=out_arr[row,3]
            # if np.mod(row,3000)==0: print(f'{row}/{out_arr.shape[0]}')
            p=out_arr[row,0]
            
            # ts=np.arange(out_arr[row,4],out_arr[row,5]+1 + after)
            ts_end = min(out_arr[row, 2] + 1 + after, len(data1['time'])) #this takes care of exceeding buffers
            ts = np.arange(out_arr[row, 1], ts_end)
            
            zs=Z[ts,p-index_adjust] #JOBARRAY INDEX_ADJUST
            ys=Y[ts,p-index_adjust] #JOBARRAY INDEX_ADJUST
            xs=X[ts,p-index_adjust] #JOBARRAY INDEX_ADJUST
            
            vars=var_data[ts,p-index_adjust] #JOBARRAY INDEX_ADJUST
            # print(vars)
            which_bins = np.clip(np.searchsorted(bin_list, vars) - 1, 0, num_bins - 1)
            
            for t, z, bin_idx in zip(ts, zs, which_bins):
                np.add.at(profile_array[:, bin_idx], z, 1)
        return profile_array

.. code:: ipython3

    def TrackedHistogram_Simultaneous(VARs, Z,Y,X, type,type2):
        global index_adjust
        out_arr=globals()[f"{type2}_{type.upper()}_out_arr"+"_2"].copy()
    
        zhs=data1['zh'].values
        # profile_array =np.zeros((len(zhs), 3)) #column 1: var, column 2: counter, column 3: list of zhs
        # profile_array[:,2]=zhs;
    
        ########
        profile_dict={}
        for var_name in VARs:
            key = f"{type2}_{type.upper()}_profile_array_{var_name}"
            [bin_left,bin_right,num_bins]=GetBinSettings(var_name) 
            profile_array =np.zeros((len(zhs), num_bins)) #TESTING***
            profile_dict[key] = profile_array
        ########
        
        for row in range(out_arr.shape[0]):
            after=out_arr[row,3]
            # if np.mod(row,3000)==0: print(f'{row}/{out_arr.shape[0]}')
            p=out_arr[row,0]
            
            # ts=np.arange(out_arr[row,4],out_arr[row,5]+1 + after)
            ts_end = min(out_arr[row, 2] + 1 + after, len(data1['time'])) #this takes care of exceeding buffers
            ts = np.arange(out_arr[row, 1], ts_end)
            
            zs=Z[ts,p-index_adjust] #JOBARRAY INDEX_ADJUST
            ys=Y[ts,p-index_adjust] #JOBARRAY INDEX_ADJUST
            xs=X[ts,p-index_adjust] #JOBARRAY INDEX_ADJUST
    
            for var_name, var_data in VARs.items():
                key = f"{type2}_{type.upper()}_profile_array_{var_name}"
                
                vars=var_data[ts,p-index_adjust]
                #########
                [bin_left,bin_right,num_bins]=GetBinSettings(var_name) 
                bin_list=np.linspace(bin_left,bin_right,num_bins)
                #########
                which_bins = np.clip(np.searchsorted(bin_list, vars) - 1, 0, num_bins - 1)
                for t, z, bin_idx in zip(ts, zs, which_bins):
                    np.add.at(profile_dict[key][:, bin_idx], z, 1)
        return profile_dict

.. code:: ipython3

    def RunCalculation(VARs, Z,Y,X):
        #VARs is a dictionary created by the function MakeDictionary
        Dictionary = {}
    
        type1_options = ['all', 'shallow', 'deep']
        type2_options = ['CL', 'nonCL', 'SBZ', 'nonSBZ', 'ColdPool']
    
        for t1 in type1_options:
            for t2 in type2_options:
                for var_name, VAR in VARs.items():
                    key = f"{t2}_{t1.upper()}_profile_array_{var_name}"
                    Dictionary[key] = TrackedHistogram(VAR, var_name, Z,Y,X, t1, t2)
        return Dictionary

.. code:: ipython3

    def RunCalculation_Simultaneous(VARs, Z,Y,X):
        #VARs is a dictionary created by the function MakeDictionary
        Dictionary = {}
    
        type1_options = ['all', 'shallow', 'deep']
        type2_options = ['CL', 'nonCL', 'SBZ', 'nonSBZ', 'ColdPool']
    
        for t1 in type1_options:
            for t2 in type2_options:
                Single_Dictionary=TrackedHistogram_Simultaneous(VARs, Z,Y,X, t1, t2)
                Dictionary.update(Single_Dictionary)
        return Dictionary

.. code:: ipython3

    def SaveProfile(Dictionary,data_type):
        # print("Saving all profiles...")
    
        # Construct the output file path
        dir2 = dir + 'Project_Algorithms/Tracked_Profiles/job_out2/'
        output_file = dir2 + f"{data_type}_" + f"tracked_profiles_{res}_{t_res}_{Np_str}"
        output_file += f"_{job_id}.h5"
    
        # Write the entire dictionary to HDF5
        with h5py.File(output_file, "w") as h5f:
            for key, profile_data in Dictionary.items():
                h5f.create_dataset(key, data=profile_data)
                
        # print("Done saving.\n")

.. code:: ipython3

    def Recombine(num_jobs):
        global variables
    
        dir2=dir+'Project_Algorithms/Tracked_Profiles/job_out2/'
        dir3=dir+'Project_Algorithms/Tracked_Profiles/OUTPUT_FILES/'
        
        #MAKING OUTPUT FILE PATH
        output_file=dir3 + f"{data_type}_" + f"tracked_profiles_{res}_{t_res}_{Np_str}.h5"
        
        
        #MAKING PROFILES DICTIONARY
        profiles = {}  # Store profiles for all variables
        job_id=1
        input_file=dir2 + f"{data_type}_" + f"tracked_profiles_{res}_{t_res}_{Np_str}_{job_id}.h5"
        with h5py.File(input_file, 'r') as f:
            for var in f:
                profiles[var]=f[f'{var}'][:]
        
        for job_id in np.arange(2,num_jobs+1):
            if np.mod(job_id,20)==0: print(f"job_id = {job_id}")
        
            #CALLING IN DATA
            input_file=dir2 + f"{data_type}_" + f"tracked_profiles_{res}_{t_res}_{Np_str}_{job_id}.h5"
        
            #COMPILING PROFILES
            with h5py.File(input_file, 'r') as f:
                for var in f:
                    profiles[var][:]+=f[f'{var}'][:]
        
        #SAVING INTO FINAL FORM
        print(f"saving as: {output_file}")
        with h5py.File(output_file, 'w') as f:
            for var in profiles:
                profile_var = profiles[var]
                f.create_dataset(f'{var}', data=profile_var, compression="gzip")

.. code:: ipython3

    #RUNNING
    ################################################################################

.. code:: ipython3

    num_slurm_jobs=30
    [start_slurm_job,end_slurm_job]=StartSlurmJobArray(num_jobs=num_jobs,num_slurm_jobs=num_slurm_jobs,ISRUN=True) #if ISRUN is False, then will not run using slurm_job_array
    
    print(f"Running on Slurm_Jobs for Slurm_Job_Ids: {(start_slurm_job,end_slurm_job)}")
    
    job_id_list=np.arange(start_slurm_job,end_slurm_job)
    for job_id in job_id_list:
        if job_id % 1 == 0: print(f'current job_id = {job_id}')
        [start_job,end_job,index_adjust]=StartJobArray(job_id,num_jobs)
    
        #SLICING DATA
        parcel=parcel1.isel(xh=slice(start_job,end_job))
        apply_job_array_filter(start_job, end_job)
    
        #GETTING DATA AND PUTTING IN A DICTIONARY
        [Z,Y,X,parcel_z] = GetSpatialData(start_job,end_job) 
        VARs=GetData(start_job,end_job)
    
        #CALCULATING AND SAVING
        # Dictionary=RunCalculation(VARs, Z,Y,X) #VERSION1: EACH VARIABLE SEPERATELY
        Dictionary=RunCalculation_Simultaneous(VARs, Z,Y,X) #VERSION2: EACH VARIABLE SIMULTANEOUSLY (RECOMMENDED)
        SaveProfile(Dictionary,data_type)
    
        #check_memory(globals())
        del VARs, Dictionary

.. code:: ipython3

    # #########################################
    #RECOMBINE SEPERATE JOB_ARRAYS AFTER
    recombine=False #KEEP FALSE WHEN JOBARRAY IS RUNNING
    # recombine=True

.. code:: ipython3

    if recombine==True:
        Recombine(num_jobs=num_jobs)


.. parsed-literal::

    job_id = 20
    job_id = 40
    job_id = 60
    saving as: /mnt/lustre/koa/koastore/torri_group/air_directory/DCI-Project/Project_Algorithms/Tracked_Profiles/OUTPUT_FILES/Tracked_Entrainment_VMF_Histogram_tracked_profiles_1km_5min_1e6.h5

