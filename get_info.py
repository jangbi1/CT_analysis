
# print('hello, world')

# import torch

# print(torch.__version__)

# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# print(device)

# print(torch.cuda.get_device_name(0))
#%%
import io
import os
import pydicom
from io import StringIO
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut
from tqdm import tqdm
def set_outside_scanner_to_air(hu_pixelarrays):
    """
    Pixel Padding Value Attribute(0028,0120) -> air
    """
    hu_pixelarrays[hu_pixelarrays < -1024] = -1024
    
    return hu_pixelarrays


def sample_stack(stack, rows=6, cols=6, start_with=0, show_every=2, vmin=-1000, vmax=1000):
    fig,ax = plt.subplots(rows,cols,figsize=[18,20])
    for i in range(rows*cols):
        ind = start_with + i*show_every
        ax[int(i/cols),int(i % cols)].set_title(f'slice {ind}')
        ax[int(i/cols),int(i % cols)].imshow(stack[ind],cmap=plt.cm.bone)
        ax[int(i/cols),int(i % cols)].axis('off')
    plt.show()
    
#%%


path = "/home/yisakk/COPD_ORG/CT_1/40444002/*/*.dcm"
dcm_list = glob(path)
file_name = dcm_list[10]

slices = [pydicom.read_file(dcm_path, force=True) for dcm_path in dcm_list]
slices_copy = slices.copy()
sample = sorted(slices_copy, key = lambda x: (float(x.SeriesNumber), float(x.InstanceNumber)))

counts = 0
for i in sample:
    print("Series number is ", i.SeriesNumber, ", and Instance number is ", i.SeriesDescription, '/', i.SOPInstanceUID)
    counts+=1
    
    # if counts == 50:
    #     break
#%%

ct_img_ls = []
voi_img_ls = []

for i in sample:
    tmp = apply_modality_lut(i.pixel_array, i)
    # tmp = set_outside_scanner_to_air(tmp)
    ct_img_ls.append(tmp)
    voi_img_ls.append(apply_voi_lut(tmp, i))

    
ct_stack = np.stack(ct_img_ls, axis=0)
voi_stack = np.stack(voi_img_ls, axis=0)

print(ct_stack.shape)
#%%
sample_stack(voi_stack)



















# %% List Dict Generation
import pandas as pd
from glob import glob 
from more_itertools import locate
import csv
from tqdm import tqdm
import pydicom
import time
import datetime
# %% High directory
if os.path.isdir('/home/yisakk/COPD_ORG/checklist')==False:
        os.mkdir('/home/yisakk/COPD_ORG/checklist')
if os.path.isdir('/home/yisakk/COPD_ORG/targets')==False:
        os.mkdir('/home/yisakk/COPD_ORG/targets')


ct_lst = glob("/home/yisakk/COPD_ORG/CT_1/*")
ct2_lst = glob("/home/yisakk/COPD_ORG/CT_2/*")

ct_lst_total = ct_lst.copy()+ct2_lst.copy()
ct_dict = {string[-8:] : string for string in ct_lst_total}
mk_dict = {0:'targets/', 1:'checklist/'}

header_dir = '/home/yisakk/COPD_ORG/'
header_lst = glob(header_dir+'header/*')
# %% Dicom saver
start = time.time()
count=0
flag=0
ct_sum=0
# check_list = open('/home/yisakk/COPD_ORG/checklist/checklist.csv', 'a', encoding='utf-8', newline='')
# wr = csv.writer(check_list)
# target_list = open('/home/yisakk/COPD_ORG/targets/checklist.csv', 'a', encoding='utf-8', newline='')
# wt = csv.writer(target_list)

header_lst = '/home/yisakk/COPD_ORG/header/40444002.csv'

for header_idx in tqdm(header_lst, desc='Patient_count {}'.format(count+1), position = 0, leave=True): 
    ct_len = 0
    df = pd.read_csv(header_idx, low_memory = False)
    patient_num = header_idx.rstrip('.csv')[-8:]
    str1 = '1mm' # input("\nTarget series is : ")
    
    series_des = df.get('SeriesDescription', '0').dropna().unique().tolist()
    series_des = [element.lower() for element in series_des]
    if any(str1 in i for i in series_des) == False:
                
        if any('1.0' in i for i in series_des) == True:
                    
            os.mkdir(''.join(['/home/yisakk/COPD_ORG/checklist/',patient_num]))
            flag = 1
            str1 = '1.0'
            series_idx = list(locate(series_des, lambda x: str1 in x))
            # wr.writerow([[patient_num]+['O']+[series_des[i] for i in series_idx]])
            
        else:
            # wr.writerow([patient_num]+['X']+series_des)
            continue
        
    else:
        dcm_dir = ct_dict[patient_num]+'/*/*.dcm'
        dic_list = glob(dcm_dir)
        slices = [pydicom.read_file(dcm_path, force=True) for dcm_path in dic_list]
        sample = sorted(slices.copy(), key = lambda x: (x.get('SeriesNumber', '0'), (x.get('InstanceNumber', '0'))))
        
        if os.path.isdir(''.join([header_dir, mk_dict[flag], patient_num]))==False:
            os.mkdir(''.join([header_dir, mk_dict[flag], patient_num]))
        for i in tqdm(sample, desc='Save_dicom', position=1, leave=False):
            if str1 in i.get('SeriesDescription', '0').lower():
                # i.save_as(''.join([header_dir, mk_dict[flag], patient_num, '/', str(i.get('SeriesNumber', '0')),'-',str(i.get('InstanceNumber', '0')), '.dcm']))
                ct_len += 1
        
        # wt.writerow([patient_num]+[ct_len]+[series_des[i] for i in list(locate(series_des, lambda x: '1mm' in x))])
        ct_sum += ct_len
        
    flag=0
    count+=1
    # if count == 9:
    #     break
end = time.time() - start

times = str(datetime.timedelta(seconds=end)) 
short = times.split(".")[0]
print(f"{short} sec")
# check_list.close()
# target_list.close()
print('Total saves: {}'.format(ct_sum))
# %%
#%% 2300개 csv 확인 및 새로 생성


count = np.ones([1, 2301])


f = open('/home/yisakk/COPD_ORG/targets/checklist.csv', 'r', encoding='utf-8')
rdr = csv.reader(f)
lines = []
for line in rdr:
    idx = int(np.where(np.array(header_lst)=='/home/yisakk/COPD_ORG/header/'+line[0]+'.csv')[0])
    line.insert(0, idx)
    lines.append(line)
    count[0,idx] = count[0,idx] - 1

f = open('/home/yisakk/COPD_ORG/checklist_X.csv','w',newline='') #원본을 훼손할 위험이 있으니 다른 파일에 저장하는 것을 추천합니다.
wr = csv.writer(f) 
wr.writerows(lines_2)
f.close()  
#%%  
f = open('/home/yisakk/COPD_ORG/checklist/checklist.csv', 'r', encoding='utf-8')
rdr = csv.reader(f)
lines_2 = []
for line in rdr:
    if '[' in line[0]: 
        line[0] = line[0].replace('[', '')
        line[0] = line[0].replace(']', '')
        line[0] = line[0].replace("'", '')
        line[0] = line[0].replace(" ", '')
        tmp = line[0].split(",")
        idx = int(np.where(np.array(header_lst)=='/home/yisakk/COPD_ORG/header/'+tmp[0]+'.csv')[0])
        tmp.insert(0, idx)
        lines_2.append(tmp)
        # count[0,idx] = count[0,idx] - 1

    else:
        idx = int(np.where(np.array(header_lst)=='/home/yisakk/COPD_ORG/header/'+line[0]+'.csv')[0])
        line.insert(0, idx)
        lines_2.append(line)
        # count[0,idx] = count[0,idx] - 1  
#%%
f = open('/home/yisakk/COPD_ORG/checklist_X.csv','w',newline='') #원본을 훼손할 위험이 있으니 다른 파일에 저장하는 것을 추천합니다.
wr = csv.writer(f)
wr.writerows(lines_2)
 
f.close()
#%%
count = 0
for header_idx in tqdm(header_lst, desc='Patient_count', position = 0, leave=True): 
    df = pd.read_csv(header_idx, low_memory = False)
    patient_num = header_idx.rstrip('.csv')[-8:]
    count += 1
    if any(patient_num in d for d in c):
        
        continue
    
    else:
        print(patient_num)
        print(count)
        break
        
    
    for dir in b:
        dir_dict = {dir[-8:] : os.path.getctime(dir)}
    
    
sorted(dir_dict.items(), key = lambda item: item[1], reverse=True)
print(dir_dict)
datetime.datetime.fromtimestamp(os.path.getctime(b[1])).strftime('%Y-%m-%d %H:%M:%S')