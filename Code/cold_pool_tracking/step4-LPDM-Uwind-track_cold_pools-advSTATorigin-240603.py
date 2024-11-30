## Cold pool tracking (step1-4) by Mingyue Tang
## step 4 for tracking cold pools (LPDM & SAM 3-D colored)
## already color, find, flag all the cores; color their group numbers

import netCDF4 as nc
import torch
from tqdm import tqdm
import gc 
import glob

str_in   = './data/step3-color-cores-groupnumber-BFS-SizeThre250-220718.nc'       
str_SAM_3D_path = './data/step0-DPT-QP-resave-220710/it*nc'     #*****
str_N_id = './data/step3-color_cores_tzyx_gn_tensor-SizeThre250-220718.pt'   

str_lpdm = './output/DYNAMO_event1_1080p_384x384x128_250m_10s_LPDM_sub1.xyz'  #******** parcel data xyz
str_OUT_STAT = './output/DYNAMO_event1_1080p_384x384x128_250m_10s_LPDM.nc' #****** #horizontal average o\vertical profile of background wind

###########  Sensitive thresholds ##########################################
Nt       = 2880   #* number of timesteps
Nz_sc    = 10     #selected layers bottom 10 layers *maybe 7 or 8 ask torri   #600 to 700 meters
Nz_lpdm  = 128    #*all layers of lagrangian particle model len(data['xh/xf'])

##### Read xyz file : parameters #######################################################
num_colum = 1080     
nx = 384 ; Nx = nx # = Nx   #***
ny = 384 ; Ny = ny # = Ny   #***
nz = Nz_lpdm   #128
N_par  = num_colum * nx * ny
nt = Nt + 1  #dnt=1, 6 hours
Nr = 2 * Nx

fid = open(str_lpdm,"rb")  

#### Read the max of core id N_id ########################################################
data_tensor = torch.load(str_N_id)
N_id = int(max(data_tensor[:,4])) 
del data_tensor 
gc.collect()

#### Read DPT path list ##################################################################
str_SAM_3D_path_list = glob.glob(str_SAM_3D_path)
str_SAM_3D_path_list.sort()

##### Allocating memory for the program #######################################
id_n  = np.zeros((N_par), int)
cc_n  = np.zeros((N_par), int) 
tt_n  = np.zeros((N_par), int) 
x0_n  = np.zeros((N_par), float)   
y0_n  = np.zeros((N_par), float)  
z0_n  = np.zeros((N_par), int)     

for it in tqdm(range(0, Nt, 1)):

    idc   = np.zeros((Nz_sc,Ny,Nx), int)   
    idp   = np.zeros((Nz_sc,Ny,Nx), int)   
    age   = np.zeros((Nz_sc,Ny,Nx), int)
    rad   = np.zeros((Nz_sc,Ny,Nx), int)
    thra  = np.zeros((Nz_sc,Ny,Nx),)

    npdf  = np.zeros((N_id+1,Nz_sc,Ny,Nx), int)  
    apdf  = np.zeros((Nt+1,Nz_sc,Ny,Nx), int)
    rpdf  = np.zeros((Nr+1,Nz_sc,Ny,Nx), int)

    ### Read colored cores nc file at every time step 06/26/2022 ###############
    gn_return   = xr.open_dataset(str_in)['gn_return'][it,:,:,:] 
    idc_cc = gn_return.values

    ### Read DPT : Buoyancy at every time step 06/26/2022 ######################
    thr_a_it = xr.open_dataset(str_SAM_3D_path_list[it])['DPTAnomaly'].values 

    ### Read LPDM xyz file  ####################################################
    off_set = 0
    tmp = np.fromfile(fid, np.int32, count= 1, offset = off_set )
    xyz_n = np.fromfile(fid, np.int32, count= N_par,  offset = off_set)
    tmp = np.fromfile(fid, np.int32, count= 1, offset = off_set) 

    x_n = np.floor(xyz_n/1e6)
    y_n = np.floor(xyz_n/1e3) - x_n*1e3   
    z_n = xyz_n - x_n*1e6 - y_n*1e3       

    x_n = np.where(x_n > nx, nx-1, x_n-1).astype(int) 
    y_n = np.where(y_n > ny, ny-1, y_n-1).astype(int) 
    z_n = np.where(z_n > nz, nz-1, z_n-1).astype(int) 

    I_pos = z_n * Nx * Ny  +  y_n * Nx  +  x_n

    #######  1. Find cores  : colored as cores ###################################
    id_core_3D = idc_cc 
    id_core = np.reshape(id_core_3D, (-1)) 
    I_core = np.where(id_core > 0)[0]
    core_n = np.isin(I_pos, I_core)*1

    ####### 2.  Find cold pools : B < 0 ##########################################
    thr_a = thr_a_it.reshape(-1)
    I_pool = np.where(thr_a < 0)[0]
    pool_n = np.isin(I_pos, I_pool)*1

    ###### 3.  Update tt clock (reset after the first loop) ###################################
    id_0 = np.where( ((core_n==1) | (pool_n==1)) & (tt_n > 0) & (z_n < Nz_sc)) [0]
    tt_n[id_0] = tt_n[id_0] + 1

    ####### 4.  Identify all the particles (firstly) going through a core ##################
    id_1 = np.where((core_n == 1) & (id_n == 0) & (z_n < Nz_sc) )[0] 
    id_n[id_1] = id_core[I_pos[id_1]]
    cc_n[id_1] = 1
    tt_n[id_1] = 1
    x0_n[id_1] = x_n[id_1]
    y0_n[id_1] = y_n[id_1]
    
    ########### 5.  Collect particles' IDs and calculate radius #########################################
    id_2 = np.where((pool_n == 1) & (id_n > 0) & (cc_n == 1) & (z_n < Nz_sc) )[0]
    for m in range(len(id_2)):
        n = id_2[m]

        i = int(x_n[n])
        j = int(y_n[n])
        k = int(z_n[n])
        c = id_n[n]   
        a = tt_n[n]

        del_x = i - x0_n[n] 
        del_y = j - y0_n[n]  
  
        del_x = min(abs(del_x), Nx-abs(del_x)) #*** comment out since open in x
        del_y = min(abs(del_y), Ny-abs(del_y))

        r = np.floor(np.sqrt( del_x**2 + del_y**2 )).astype(int) + 1

        npdf[c,k,j,i] = npdf[c,k,j,i] + 1 
        apdf[a,k,j,i] = apdf[a,k,j,i] + 1
        rpdf[r,k,j,i] = rpdf[r,k,j,i] + 1


    #### 4.2  if enter, save x, y, z; then calculated sum of traveling distance 08/01/2022 ########### 
    ip_enter = np.where( cc_n == 1 )[0] 
    u_z = xr.open_dataset(str_OUT_STAT)['U'].values [it,:Nz_sc] 
    v_z = xr.open_dataset(str_OUT_STAT)['V'].values [it,:Nz_sc]

    for ip in ip_enter:       
        del_t = 1*60  
        x_center = int(np.ceil(x0_n[ip]))
        y_center = int(np.ceil(y0_n[ip]))

        u_ip = u_z [z0_n[ip]] 
        x0_n[ip] = x0_n[ip] + u_ip * del_t /250.  
        v_ip = v_z [z0_n[ip]]
        y0_n[ip] = y0_n[ip] + v_ip * del_t /250. 
             
        # if  x0_n[ip] >= (Nx-1): #*** comment out since open in x
        #     x0_n[ip] = x0_n[ip] - Nx
        if  y0_n[ip] >= (Ny-1):
            y0_n[ip] = y0_n[ip] - Ny
        # if  x0_n[ip] < 0: #*** comment out since open in x
        #     x0_n[ip] = x0_n[ip] + (Nx-1) 
        if  y0_n[ip] < 0:
            y0_n[ip] = y0_n[ip] + (Ny-1)

    del id_0, id_1, u_z, v_z, id_2,
    gc.collect()


    ############# 6.1 Give IDs to cold pool grid points ################################
    val_id = np.nanmax(npdf[0:N_id,:,:,:], axis=0) 
    pos_id = np.argmax(npdf[0:N_id,:,:,:], axis=0) 
    id_get = np.where( val_id  > 0)  
    idc[id_get] = pos_id[id_get]
    
    ############# 6.2 Give age to cold pool grid points ################################
    val_id = np.nanmax(apdf[0:Nt,:,:,:], axis=0)
    pos_id = np.argmax(apdf[0:Nt,:,:,:], axis=0)
    id_get = np.where( val_id > 0 )
    age[id_get] = pos_id[id_get]

    ############# 6.3 Give radius to cold pool grid points ################################
    val_id = np.nanmax(rpdf[:,:,:,:], axis=0) 
    pos_id = np.argmax(rpdf[:,:,:,:], axis=0)
    id_get = np.where( val_id > 0 )
    rad[id_get] = pos_id[id_get]

    del val_id, pos_id, id_get, apdf, rpdf, 
    gc.collect()

    ############## 7. Entrain particle  #####################################################
    id_3 = np.where((pool_n == 1) & (id_n == 0) & (cc_n == 0) & (z_n < Nz_sc) )[0]
    idc_1D = np.reshape(idc, (-1)) 
    id_n[id_3] = idc_1D[ I_pos[id_3]]

    ############### 8. Reset particles out of cold pools ####################################
    id_4 = np.where((id_n > 0) & ((pool_n == 0) | (z_n >= Nz_sc)) )[0] # B > 0
    id_n[id_4] = 0
    cc_n[id_4] = 0
    tt_n[id_4] = 0
    x0_n[id_4] = 0
    y0_n[id_4] = 0
    z0_n[id_4] = 0

    ################ 9. Prepare tensors for display (adding missing pieces) ##################
    id_5 = np.where((pool_n == 1) & (id_n > 0) & (cc_n == 0) & (z_n < Nz_sc) )[0]
    for m in range(len(id_5)):
        n = id_5[m]

        i = int(x_n[n])
        j = int(y_n[n])
        k = int(z_n[n])
        c = id_n[n]   
        npdf[c,k,j,i] = npdf[c,k,j,i] + 1 

    ################ 10. Give IDs to cold pool grid points #########################################
    val_id = np.nanmax(npdf[0:Nt,:,:,:], axis=0)
    pos_id = np.argmax(npdf[0:Nt,:,:,:], axis=0)
    id_get = np.where( val_id > 0 )
    idp[id_get] = pos_id[id_get]

    ################# 11. Save age, rad, idc, idp ###############################################
    ds = xr.Dataset(
        data_vars = dict(
            age   = (['z','y','x'], age),   
            rad   = (['z','y','x'], rad),   
            idc   = (['z','y','x'], idc),   
            idp   = (['z','y','x'], idp),   
        ),
        coords = dict(
            x = gn_return.x,
            y = gn_return.y,
            z = gn_return.z[:Nz_sc],
        ),
        attrs=dict(description="cold pools features: age, radius, IDs to cold pool points: idc and idp (without/with reset). "),
    )


    ds.to_netcdf('./data/step4-E1-advX0STAT-j-CP-age_rad_idc_idp-220906/it_'+str(it).zfill(4)+'-adv-CP-age_rad_idc_idp.nc')

    del age, rad, idc, idp, npdf, ds   #age, radius, cold pool id 1/0, downdraft id integers, npdf/ds medium steps dont matter
    gc.collect()


    









