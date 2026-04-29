#!/usr/bin/env python
# coding: utf-8

# In[4]:


# ============================================================
# CallVariable_Function
# ============================================================

import os

def CallVariable(ModelData, DataManager, timeString, variableName, zInterpolate = None, printstatement=False):

    ###########################################################################
    
    if variableName in ModelData.varList:
        var_data = DataManager.GetTimestepData(DataManager.inputDataDirectory, timeString, 
                                               variableName=variableName, zInterpolate = zInterpolate)
        
    elif variableName not in ModelData.varList:
        Processed_string = "PROCESSED_" if "PROCESSED_" in variableName else ""
        DivideMassFlux_string = "_DivideMassFlux" if "_DivideMassFlux" in variableName else ""
        
        if variableName in ["A_g","A_c","qcqi"]:
            dataType = "CalculateMoreVariables"
            dataName = "Eulerian_Binary_Array"
            dataFolder = dataName
        elif variableName in ["VMF_g","VMF_c"]:
            dataType = "CalculateMoreVariables"
            dataName = "Eulerian_VMF"
            dataFolder = dataName
        elif variableName in ["MSE"]:
            dataType = "CalculateMoreVariables"
            dataName = "Moist_Static_Energy"
            dataFolder = dataName
        elif variableName in ["theta_v"]:
            dataType = "CalculateMoreVariables"
            dataName = "Virtual_Potential_Temperature"
            dataFolder = dataName
        elif variableName in ["theta_e", "RH_vapor", "RH_ice"]:
            dataType = "CalculateMoreVariables"
            dataName = "Equivalent_Potential_Temperature"
            dataFolder = dataName
        elif variableName in ["convergence"]:
            dataType = "CalculateMoreVariables"
            dataName = "Convergence"
            dataFolder = dataName
        elif variableName in ["HMC"]:
            dataType = "CalculateMoreVariables"
            dataName = "MoistureConvergence"
            dataFolder = dataName

        elif variableName in ['qv_prime','qcqi_prime','RH_vapor_prime',
                              'winterp_prime','VMF_g_prime','VMF_c_prime',
                              'HMC_prime',
                              'theta_v_prime','theta_e_prime','MSE_prime']:
            dataType = "CalculateMoreVariables"
            dataName = "VariablePerturbations"
            dataFolder = dataName

        elif variableName in [f'{Processed_string}Entrainment{DivideMassFlux_string}_g',f'{Processed_string}Entrainment{DivideMassFlux_string}_c',
                              f'{Processed_string}TransferEntrainment{DivideMassFlux_string}_g',
                              f'{Processed_string}TransferEntrainment{DivideMassFlux_string}_c']:
            dataType = "EntrainmentCalculation"
            dataName = f"{Processed_string}Entrainment{DivideMassFlux_string}"
            dataFolder = f"EntrainmentCalculation{DivideMassFlux_string}"
    
        elif variableName in [f'{Processed_string}Detrainment{DivideMassFlux_string}_g',f'{Processed_string}Detrainment{DivideMassFlux_string}_c',
                              f'{Processed_string}TransferDetrainment{DivideMassFlux_string}_g',
                              f'{Processed_string}TransferDetrainment{DivideMassFlux_string}_c']:
            dataType = "EntrainmentCalculation"
            dataName = f"{Processed_string}Detrainment{DivideMassFlux_string}"
            dataFolder = f"EntrainmentCalculation{DivideMassFlux_string}"

        elif variableName in [f'{Processed_string}MassFlux_g',f'{Processed_string}MassFlux_c']:
            dataType = "EntrainmentCalculation"
            dataName = f"{Processed_string}MassFlux"
            dataFolder = "MassFluxCalculation"
        ###########################################################################

        inputDataDirectory = os.path.normpath(
            os.path.join(DataManager.inputDirectory, "..", dataType,
                         f"{DataManager.res}_{DataManager.t_res}_{DataManager.Nz_str}nz", dataFolder)
                        )
        var_data = DataManager.GetTimestepData(inputDataDirectory, timeString, 
                                               variableName=variableName, dataName=dataName, printstatement=printstatement)
    return var_data


# In[3]:


# ============================================================
# CallLagrangianArray_Function
# ============================================================

import os

def CallLagrangianArray(ModelData, DataManager, timeString, variableName, 
                        printstatement=False):
    Processed_string = "PROCESSED_" if "PROCESSED_" in variableName else ""
    DivideMassFlux_string = "_DivideMassFlux" if "_DivideMassFlux" in variableName else ""

    if variableName in ["A_g","A_c","z","x","Z","Y","X","W","QCQI"]:
        dataType = "LagrangianArrays"
        dataName = "Lagrangian_Binary_Array"
        dataFolder = dataName
    elif variableName in [f"{Processed_string}A_g",f"{Processed_string}A_c"]:
        dataType = "LagrangianArrays"
        dataName = f"{Processed_string}Lagrangian_Binary_Array"
        dataFolder = dataName
    elif variableName in  ["QV", "QCQI",
                           "RH_vapor",
                           "VMF_g", "VMF_c",
                           "HMC", "CONVERGENCE",
                           "THETA_v", "THETA_e",
                           "MSE"]:
        dataType = "LagrangianArrays"
        dataName = "VARS"       
        dataFolder = dataName
    elif variableName in ["convergence"]:
        dataType = "LagrangianArrays"
        dataName = "Convergence"
        dataFolder = dataName
    elif variableName in ["HMC"]:
        dataType = "LagrangianArrays"
        dataName = "MoistureConvergence"
        dataFolder = dataName
    elif variableName in ["QV_prime","QCQI_prime","RH_vapor_prime",
                           "W_prime","VMF_g_prime",'VMF_c_prime',
                           "HMC_prime",
                           "THETA_v_prime",'THETA_e_prime','MSE_prime']:
        dataType = "LagrangianArrays"
        dataName = "VARS_Perturbations"       
        dataFolder = dataName
    elif variableName in ['D_c', 'D_g', 'E_c', 'E_g',
                          'TransferD_c', 'TransferD_g', 
                          'TransferE_c', 'TransferE_g']:
        dataType = "LagrangianArrays"
        dataName = "Lagrangian_Entrainment"
        dataFolder = "Lagrangian_Entrainment"

    elif variableName in [f'{Processed_string}D{DivideMassFlux_string}_c', f'{Processed_string}D{DivideMassFlux_string}_g',
                          
                          f'{Processed_string}E{DivideMassFlux_string}_c', f'{Processed_string}E{DivideMassFlux_string}_g',
                          f'{Processed_string}TransferD{DivideMassFlux_string}_c', f'{Processed_string}TransferD{DivideMassFlux_string}_g', 
                          f'{Processed_string}TransferE{DivideMassFlux_string}_c', f'{Processed_string}TransferE{DivideMassFlux_string}_g']:
        dataType = "LagrangianArrays"
        dataName = f"{Processed_string}Lagrangian_Entrainment{DivideMassFlux_string}"
        dataFolder = f"{Processed_string}Lagrangian_Entrainment{DivideMassFlux_string}"

    elif variableName in ['WB_BUOY', 'WB_HADV', 'WB_HIDIFF', 'WB_HTURB',
                    'WB_PGRAD', 'WB_VADV', 'WB_VIDIFF', 'WB_VTURB']:
        dataType = "LagrangianArrays"
        dataName = "BUDGET_VARS_W"       
        dataFolder = "BUDGET_VARS"
    elif variableName in ['QVB_HADV', 'QVB_HIDIFF', 'QVB_HTURB', 'QVB_MP',
                    'QVB_VADV', 'QVB_VIDIFF', 'QVB_VTURB']:
        dataType = "LagrangianArrays"
        dataName = "BUDGET_VARS_QV"       
        dataFolder = "BUDGET_VARS"
    elif variableName in ['PTB_DISS', 'PTB_DIV', 'PTB_HADV', 'PTB_HIDIFF', 
                    'PTB_HTURB', 'PTB_MP', 'PTB_RAD', 'PTB_VADV', 
                    'PTB_VIDIFF', 'PTB_VTURB']:
        dataType = "LagrangianArrays"
        dataName = "BUDGET_VARS_TH"       
        dataFolder = "BUDGET_VARS"
        
    inputDataDirectory = os.path.normpath(
        os.path.join(DataManager.inputDirectory, "..", dataType,
                     f"{DataManager.res}_{DataManager.t_res}_{DataManager.Nz_str}nz", dataFolder))
    var_data = DataManager.GetTimestepData(inputDataDirectory, timeString,
                                           variableName=variableName, dataName=dataName,
                                           printstatement=printstatement)
    return var_data


# In[ ]:


# ============================================================
# Get_LagrangianArrays_Function
# ============================================================

def Get_LagrangianArrays(ModelData, DataManager, t, dataType="VARS", dataName="VARS", varNames=["W"]):
    res = ModelData.res
    t_res = ModelData.t_res
    Nz_str = ModelData.Nz_str
    inputDirectory = os.path.join(DataManager.inputDirectory,
                                  "..","LagrangianArrays",
                                  f"{res}_{t_res}_{Nz_str}nz", dataType)
    timeString = ModelData.timeStrings[t]

    FileName = os.path.join(inputDirectory, f"{dataName}_{res}_{t_res}_{Nz_str}nz_{timeString}.h5")

    dataDictionary = {}
    with h5py.File(FileName, 'r') as f:
        # print("Keys in file:", list(f.keys()))
        for key in varNames:
            dataDictionary[key] = f[key][:]
            # print(f"{key}: shape = {dataDictionary[key].shape}, dtype = {dataDictionary[key].dtype}")
    return dataDictionary


# In[1]:


# ============================================================
# OpenMultipleSingleTimes_LagrangianArray_FUNCTION
# ============================================================

import os
from glob import glob
import xarray as xr

def OpenMultipleSingleTimes_LagrangianArray(directory, ModelData, pattern="Lagrangian_Binary_Array_*.h5"):
    """
    Load a sequence of Lagrangian .h5 files (each a single timestep)
    into one xarray.Dataset with dimensions (time, p),
    enforcing time order from ModelData.timeStrings.
    """
    # --- Find all available files
    files_all = glob(os.path.join(directory, pattern))
    if not files_all:
        raise FileNotFoundError(f"No files found in {directory} matching {pattern}")

    # --- Build the correctly ordered list according to ModelData.timeStrings
    files = []
    for t in ModelData.timeStrings:
        time_pattern = f"_{t}.h5"
        matched = [f for f in files_all if f.endswith(time_pattern)]
        if matched:
            files.append(matched[0])
        else:
            print(f"Missing file for time {t}")

    # --- Open and concatenate along time
    chunk_spec = {'phony_dim_0': -1}  #new
    ds = xr.open_mfdataset(
        files,
        engine="h5netcdf",
        phony_dims="sort",
        combine="nested",
        concat_dim="time",
        
    # 1. Stop xarray from generating tasks to check phony_dim_0 alignment across 661 files
        compat="override", 
        coords="minimal", 
        join="override", 
        
        # 2. Chunking (Prevents massive graph explosion on full dataset)
        chunks=chunk_spec, 
        
        # 3. Parallelize graph generation
        parallel=True 
    )

    # --- Rename the phony dimension to 'p'
    if "phony_dim_0" in ds.dims:
        ds = ds.rename({"phony_dim_0": "p"})

    return ds, files

# #EXAMPLE USAGE
# directory = f"/mnt/lustre/koa/koastore/torri_group/air_directory/Projects/DCI-Project/Code/OUTPUT/Variable_Calculation/LagrangianArrays/{ModelData.res}_{ModelData.t_res}_{ModelData.Nz_str}nz/Lagrangian_Binary_Array/"
# Lagrangian_Binary_Array,files = OpenMultipleSingleTimes_LagrangianArray(directory, ModelData)

def OpenMultipleSingleTimes_LagrangianArray_JobArray(directory, ModelData, start_job,end_job, 
                                                     pattern="Lagrangian_Binary_Array_*.h5"):
    """
    Load a sequence of Lagrangian .h5 files (each a single timestep)
    into one xarray.Dataset with dimensions (time, p),
    enforcing time order from ModelData.timeStrings.
    """
    # --- Find all available files
    files_all = glob(os.path.join(directory, pattern))
    if not files_all:
        raise FileNotFoundError(f"No files found in {directory} matching {pattern}")

    # --- Build the correctly ordered list according to ModelData.timeStrings
    files = []
    for t in ModelData.timeStrings:
        time_pattern = f"_{t}.h5"
        matched = [f for f in files_all if f.endswith(time_pattern)]
        if matched:
            files.append(matched[0])
        else:
            print(f"Missing file for time {t}")

    # --- Open and concatenate along time
    def limit_parcels(ds): return ds.isel(phony_dim_0=slice(start_job, end_job))
    chunk_spec = {'phony_dim_0': -1}  #new
    ds = xr.open_mfdataset(
        files,
        engine="h5netcdf",
        phony_dims="sort",
        combine="nested",
        concat_dim="time",
        preprocess=limit_parcels,
    
        # 1. Stop xarray from generating tasks to check phony_dim_0 alignment across 661 files
        compat="override", #new
        coords="minimal", #new
        join="override", #new
    
        # 2. Chunking
        chunks=chunk_spec, #new
    
        # 3. Parallelize
        parallel=True #new
    )

    # --- Rename the phony dimension to 'p'
    if "phony_dim_0" in ds.dims:
        ds = ds.rename({"phony_dim_0": "p"})

    return ds, files

# #EXAMPLE USAGE
# directory = f"/mnt/lustre/koa/koastore/torri_group/air_directory/Projects/DCI-Project/Code/OUTPUT/Variable_Calculation/LagrangianArrays/{ModelData.res}_{ModelData.t_res}_{ModelData.Nz_str}nz/Lagrangian_Binary_Array/"
# Lagrangian_Binary_Array,files = OpenMultipleSingleTimes_LagrangianArray_JobArray(directory, ModelData, start_job,end_job)

