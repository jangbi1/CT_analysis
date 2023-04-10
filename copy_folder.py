from joblib import Parallel, delayed
from tqdm import tqdm
import os
import shutil
source_folder = '/home/yisakk/COPD_ORG/targets2/'
target_folder = '/home/yisakk/COPD_ORG/targets/'
cores = 10

def copy_folder(folder_name):
    # targets2 폴더 내의 폴더를 대상 폴더로 복사합니다.
    source_path = os.path.join(source_folder, folder_name)
    target_path = os.path.join(target_folder, folder_name)
    
    # targets 폴더에 해당 폴더가 이미 있는 경우, 폴더 내의 모든 파일을 삭제합니다.
    if os.path.exists(target_path):
        for file_name in os.listdir(target_path):
            file_path = os.path.join(target_path, file_name)
            os.remove(file_path)
    # targets 폴더에 해당 폴더가 없는 경우, 새로운 폴더를 만듭니다.
    else:
        os.mkdir(target_path)
    
    # targets2 폴더 내의 모든 파일을 대상 폴더로 복사합니다.
    for file_name in os.listdir(source_path):
        source_file_path = os.path.join(source_path, file_name)
        target_file_path = os.path.join(target_path, file_name)
        shutil.copyfile(source_file_path, target_file_path)

folder_names = os.listdir(source_folder)

# 병렬 처리를 위해 joblib를 사용합니다.
Parallel(n_jobs=cores)(delayed(copy_folder)(folder_name) for folder_name in tqdm(folder_names))