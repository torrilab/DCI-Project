## Cold pool tracking (step1-4) by Mingyue Tang
## step 3 for tracking cold pools
# change save tensor to nc file, ignore too small clusters.

import torch
from tqdm import tqdm
import gc

###### Read tensor data from step2 ###############################################################
data = torch.load('./data/step2-color_cores_tzyx_gn_tensor-220711.pt')

##### Creat a new tensor to concat with rewrited group ################################
new_data = torch.zeros(0, 5)

####### Add size threshold and rename the groupnumber (ignore too small cores) 06/23/2022 #########
size_threshold = 250  #number of gridboxes for BFS      
gn = 1

for ig in tqdm(range(1, int(max(data[:,4])), 1)):  
    group_i = torch.where(data[:,4]==ig)
    group = data[group_i]
    len_ig = len(group_i[0])
    if len_ig < size_threshold:
        group[:,4] = 0 
    else:
        group[:,4] = gn  
        gn = gn + 1
    new_data = torch.cat([new_data, group], dim=0) 

######## save data as tensor ######################################################
torch.save(new_data, './data/step3-color_cores_tzyx_gn_tensor-SizeThre250-220718.pt')

del data, group,
gc.collect()

######### save colored cores as nc #########################################
DPT_path = './data/step1-FindFlag_Cores-220710.nc'
nc_array = xr.open_dataset(DPT_path)['flag_return'] 

x = nc_array.x
y = nc_array.y
z = nc_array.z
time = nc_array.time

del nc_array,
gc.collect()

gn_return  = np.zeros(( len(time), len(z), len(y), len(x) ), int)

for i in tqdm(range(len(new_data[:,0]))):
    gn_return[ int(new_data[i,0]), int(new_data[i,1]), int(new_data[i,2]), int(new_data[i,3]) ] = new_data[i,4]

ds = xr.Dataset(
    data_vars = dict(
        gn_return   = (['time','z','y','x'], gn_return),   # group number
    ),
    coords = dict(
        x = x,
        y = y,
        z = z,
        time = time,
    ),
    attrs=dict(description="color cold cores, return flagging coonvective points and 4-D BFS group numbers, with size threshold >= 250"),
)


ds.to_netcdf('./data/step3-color-cores-groupnumber-BFS-SizeThre250-220718.nc')







