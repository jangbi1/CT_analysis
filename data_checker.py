#%%
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
# if os.path.isdir('/home/yisakk/COPD_ORG/checklist')==False:
#         os.mkdir('/home/yisakk/COPD_ORG/checklist')
# if os.path.isdir('/home/yisakk/COPD_ORG/targets2')==False:
#         os.mkdir('/home/yisakk/COPD_ORG/targets2')
#%%

ct_lst = glob("/home/yisakk/COPD_ORG/CT_1/*")
ct2_lst = glob("/home/yisakk/COPD_ORG/CT_2/*")

ct_lst_total = ct_lst.copy()+ct2_lst.copy()
ct_dict = {string[-8:] : string for string in ct_lst_total}
mk_dict = {0:'targets2/', 1:'checklist/'}

header_dir = '/home/yisakk/COPD_ORG/'
import shutil
from joblib import Parallel, delayed
start = time.time()
count=0
flag=0
ct_len=0
str2='1.0'
#%%
def slice_analysis(dcm_path, patient_num):
    slices = pydicom.filereader.read_file(dcm_path, force=True)
    if str2 in str(slices.get('SeriesDescription', '0') or '0').lower():
        slices.save_as(''.join(['/home/yisakk/COPD_ORG/checklist/', patient_num, '/', str(slices.get('SeriesNumber', '0') or '0'),'-',str(slices.get('InstanceNumber', '0') or '0'), '.dcm']))

header_lst = glob(header_dir+'header/*')[626:]

for header_idx in tqdm(header_lst, desc='Patient_count', position = 0, leave=True): 
    ct_len+=1
    df = pd.read_csv(header_idx, low_memory = False)
    patient_num = header_idx.rstrip('.csv')[-8:]
    str1 = '1mm' # input("\nTarget series is : ")
        
    series_des = df.get('SeriesDescription')
    if series_des is None:
        # wr.writerow([patient_num]+['X']+['Nan'])
        continue
    sd_vc = df.get('SeriesDescription').dropna().value_counts()
    series_des = [element.lower() for element in sd_vc.index]    

    if any(str1 in i for i in series_des) == False:
        if any(str2 in i for i in series_des) == True:
            count = 0
            for i in range(len(sd_vc)):
                if str2 in series_des[i]:
                    count += sd_vc[i]
                    
            folder_count = len(glob(''.join(['/home/yisakk/COPD_ORG/checklist/', patient_num, '/*'])))
            if count == folder_count:
                print(f'We continued the folder-{patient_num} with {folder_count} insides / {count} descriptions')
                continue
            
            else:
                shutil.rmtree(''.join(['/home/yisakk/COPD_ORG/checklist/', patient_num]), ignore_errors=True)
                print(f'We deleted the folder-{patient_num} with {folder_count} insides / {count} descriptions')

                dcm_dir = ct_dict[patient_num]+'/*/*.dcm'
                dic_list = glob(dcm_dir)
                if os.path.isdir(''.join(['/home/yisakk/COPD_ORG/checklist/', patient_num]))==False:
                    os.mkdir(''.join(['/home/yisakk/COPD_ORG/checklist/', patient_num]))
                    _ = Parallel(n_jobs=8)(delayed(slice_analysis)(dcm_path, patient_num) for dcm_path in tqdm(dic_list, desc= f'{patient_num}', position = 1, leave=False))
                    
        # wt.writerow([ct_len]+[patient_num]+[series_des[i] for i in list(locate(series_des, lambda x: '1mm' in x))])
        
        
    flag=0
    
    # if ct_len == 10:
    #     break
end = time.time() - start

times = str(datetime.timedelta(seconds=end))   
short = times.split(".")[0]
print(f"{short} sec")
# check_list.close()
# target_list.close()

#%%
