# %% List Dict Generation
import pandas as pd
from glob import glob 
from more_itertools import locate
import csv
from tqdm import tqdm
import pydicom
import time
import datetime

import io
import os
import matplotlib.pyplot as plt
import numpy as np
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut
# %% High directory
if os.path.isdir('/home/yisakk/COPD_ORG/checklist')==False:
        os.mkdir('/home/yisakk/COPD_ORG/checklist')
if os.path.isdir('/home/yisakk/COPD_ORG/targets2')==False:
        os.mkdir('/home/yisakk/COPD_ORG/targets2')
#%%

ct_lst = glob("/home/yisakk/COPD_ORG/CT_1/*")
ct2_lst = glob("/home/yisakk/COPD_ORG/CT_2/*")

ct_lst_total = ct_lst.copy()+ct2_lst.copy()
ct_dict = {string[-8:] : string for string in ct_lst_total}
mk_dict = {0:'targets2/', 1:'checklist/'}

header_dir = '/home/yisakk/COPD_ORG/'
header_lst = glob(header_dir+'header/*')
# %% Dicom saver
start = time.time()
count=0
flag=0
ct_len=0

# check_list = open('/home/yisakk/COPD_ORG/checklist/checklist_1.csv', 'a', encoding='utf-8', newline='')
# wr = csv.writer(check_list)
target_list = open('/home/yisakk/COPD_ORG/targets/checklist_2.csv', 'a', encoding='utf-8', newline='')
wt = csv.writer(target_list)

header_lst = glob(header_dir+'header/*')
# header_lst = header_lst.copy()

for header_idx in tqdm(header_lst, desc='Patient_count', position = 0, leave=True): 
    ct_len+=1
    df = pd.read_csv(header_idx, low_memory = False)
    patient_num = header_idx.rstrip('.csv')[-8:]
    str1 = '1mm' # input("\nTarget series is : ")
    if os.path.isdir(''.join([header_dir, mk_dict[0], patient_num]))==True:
        # print('already exists in checklist')
        continue
    if os.path.isdir(''.join([header_dir, mk_dict[1], patient_num]))==True:
        # print('already exists in targets')
        continue
        
    series_des = df.get('SeriesDescription')
    if series_des is None:
        # wr.writerow([patient_num]+['X']+['Nan'])
        continue
    series_des =  series_des.dropna().unique().tolist()
     
    series_des = [element.lower() for element in series_des]
    if any(str1 in i for i in series_des) == False:  
        if any('1.0' in i for i in series_des) == True:
            flag = 1
            str1 = '1.0'
            series_idx = list(locate(series_des, lambda x: str1 in x))
            wr.writerow([ct_len]+[patient_num]+['O']+[series_des[i] for i in series_idx])
            if os.path.isdir(''.join([header_dir, mk_dict[flag], patient_num]))==False:
                os.mkdir(''.join([header_dir, mk_dict[flag], patient_num]))   
            
        else:
            wr.writerow([ct_len]+[patient_num]+['X']+series_des)
            continue
        
    else:
        dcm_dir = ct_dict[patient_num]+'/*/*.dcm'
        dic_list = glob(dcm_dir)
        slices = [pydicom.read_file(dcm_path, force=True) for dcm_path in dic_list]
        sample = sorted(slices.copy(), key = lambda x: (int(x.get('SeriesNumber', '0') or 0), int(x.get('InstanceNumber', '0') or 0)))
        if os.path.isdir(''.join([header_dir, mk_dict[flag], patient_num]))==False:
            os.mkdir(''.join([header_dir, mk_dict[flag], patient_num]))
        for i in tqdm(sample, desc='Save_dicom', position=1, leave=False):
            if str1 in str(i.get('SeriesDescription', '0') or '0').lower():
                i.save_as(''.join([header_dir, mk_dict[flag], patient_num, '/', str(i.get('SeriesNumber', '0') or '0'),'-',str(i.get('InstanceNumber', '0') or '0'), '.dcm']))
                
        wt.writerow([ct_len]+[patient_num]+[series_des[i] for i in list(locate(series_des, lambda x: '1mm' in x))])
        
        
    flag=0
    
    # if count == 1721:
    # break
end = time.time() - start

times = str(datetime.timedelta(seconds=end))   
short = times.split(".")[0]
print(f"{short} sec")
# check_list.close()
target_list.close()

#%%

df = pd.read_csv('/home/yisakk/COPD_ORG/header/35809063.csv', low_memory = False)
if df.SeriesDescription.value_counts() != len(os.listdir('/home/yisakk/COPD_ORG/targets/35809063')):
    
#%%