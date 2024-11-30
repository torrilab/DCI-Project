## Cold pool tracking (step1-4) by Mingyue Tang
## step 2 for tracking cold pools
## already calculate density potential temperature and flagged all the cores as 1 (others are 0)
# 4-D BFS 
import torch

def distance4D(data, pivot):   # 4-D with 2 periodic boudaries  #*** need to fix for open boudnary conditions in x 
    L = 100      # Lx = Ly 
    diffs = torch.zeros_like(data)
    for j in [0,1,3]:  #non-periodic in t,z,x
        diffs[:,j] = torch.abs(data[:,j] - pivot[j])
    for j in [2]:  #periodic in y 
        vmin = torch.min(data[:,j], pivot[j])
        vmax = torch.max(data[:,j], pivot[j])
        diffs[:,j] = torch.min(vmax-vmin, L+vmin-vmax)
    return diffs[:,0:4]


def check(data, threshold):
    is_correct = True
    for i in range(int(torch.max(data[:,4]))):
        group = data[torch.where(data[:,4]==i)]
        for j in range(len(group)):
            dis = distance4D(group, group[j])
            dis = torch.sum(dis, 1)
            num_correct_rows = torch.sum(torch.le(dis, threshold)*1.0)
            is_this_correct = torch.ge(num_correct_rows,1)
            is_correct = is_this_correct and is_correct
    return is_correct

###### data = cores_tzyx_gn (t, z, y, x, groupnumber) , 5D ###################
path = '/mnt/lustre/koa/koastore/torri_group/air_directory/cold pool tracking/'
data = torch.load(path+'step1-findflag_cores_tzyx_tensor-240620.pt')
data = data.cuda()    #uses GPUS*

#### BFS by matrix   04/10/2022 ##############################################################
threshold = 1   
acc_group_number = 0

for prnt,i in enumerate(range(len(data))):
    if prnt%1e4==0: print(f'current step: {prnt}/{len(data)}')
    pivot = data[i]
    diffs = distance4D(data, pivot)
    is_valid = torch.le( torch.sum( torch.gt(diffs[:,0:4], 0) *1.0, 1 ) , 1) * 1.0 # only one dim has dis = 1
    diffs = diffs[:,0:4] - (threshold+1)
    diffs = torch.max(diffs, 1)[0]    
    diffs = torch.lt(diffs, 0) * 1.0
    is_valid = diffs * is_valid
    collision_group_numbers = data[:,4][torch.where(data[:,4]*is_valid!=0)]
    if len(collision_group_numbers) > 0: 
        group_numbers = data[:,4]
        group_numbers_repeat = group_numbers.repeat(len(collision_group_numbers),1).t()
        group_numbers_divide = group_numbers_repeat / collision_group_numbers
        group_numbers_eq1 = torch.eq(group_numbers_divide, 1)
        group_numbers_sum = torch.sum(group_numbers_eq1*1.0, dim=-1)
        valid_group_number_indices = torch.where(group_numbers_sum==1)
        is_valid[valid_group_number_indices] = 1

        cur_group_number = torch.min(collision_group_numbers)
    else:
        cur_group_number = torch.max(data[:,4]) + 1
    data[:,4] = cur_group_number * is_valid + data[:,4] * (1-is_valid)

data = data.cpu()  #uses GPUS*
######## save data as tensor ########################################
torch.save(data, path+'step2-color_cores_tzyx_gn_tensor-220711.pt')