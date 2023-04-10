
# print('hello, world')

# import torch

# print(torch.__version__)

# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# print(device)

# print(torch.cuda.get_device_name(0))

from __future__ import print_function
import zipfile
import io
# import StringIO
import logging
import os
import sys
import argparse
import pydicom
from io import StringIO
import shutil
from tqdm import tqdm
import time
if os.path.isdir('/home/jangbi/targets')==True:
    shutil.rmtree('/home/jangbi/targets')

# def show_serial_num(file_list=None, series_num=None):
#     logger = logging.getLogger("show_serial_num")
#     dict = {}
#     if file_list is None:
#         file_list = []
#     for file_name, file_object in file_list:
#         try:
#             logger.info('reading: %s', file_name)
#             f = pydicom.read_file(fp=file_object)
#             logger.info("finished reading")
#             patient_id = f.get("PatientID", "No ID")

#             print(file_name, "has patient id of", patient_id)
            
            
#         except Exception:
#             print(file_name, "had no patient id for some reason")

        
def show_serial_num(file_list=None):
    print('\n')
    logger = logging.getLogger("show_patient_IDs")
    dict = {}
    if file_list is None:
        file_list = []
    for file_name, file_object in file_list:
        try:
            f = pydicom.read_file(fp=file_object)      
            if f.SeriesDescription != '':
                dict[f.SeriesNumber] = [f.SeriesDescription, f.pixel_array.shape]
            
        except Exception:
            print(file_name, "had no serial num for some reason")
    for key, value in dict.items():
        print(key, "is Series Number of ", value[0], ", and size is ", value[1])


def get_dicom_info(file_list=None, series_num=None):
    if os.path.isdir('/home/jangbi/targets')==False:
        os.mkdir('/home/jangbi/targets')
    if file_list is None:
        file_list = []   

    for file_name, file_object in tqdm(file_list, desc = 'Save Dicom'):
        g = pydicom.read_file(fp=file_object) 
        sN = g.get("SeriesNumber", "No SN")
        if int(sN) == int(series_num):
            dir = '/home/jangbi/targets/'+file_name
            g.save_as(dir)
        
        
def unzip(zip_archive):
    """
    zip_archive is a zipfile object (from
        zip_archive = zipfile.ZipFile(filename, 'r') for example)
    Returns a dictionary of file names and file like objects (StringIO's)
    The filter in the if statement skips directories and dot files
    """
    file_list = []
    for file_name in tqdm(zip_archive.namelist(), desc = 'Unzip', leave=False):
        if (not os.path.basename(file_name).startswith('.') and
                not file_name.endswith('/')):
            file_object = zip_archive.open(file_name, 'r')
            file_like_object = io.BytesIO(file_object.read())
            file_object.close()
            file_like_object.seek(0)
            name = os.path.basename(file_name)
            file_list.append((name, file_like_object))
                    
    return file_list


def parse_args():
    """Argument parser for load series"""
    parser = argparse.ArgumentParser(
        description='Read a zip/tar/gz of dicom files')
    parser.add_argument('-i',
                        dest='input_file',
                        type=str,
                        help='zip')
    
    _args = parser.parse_args()
    
    return _args

# def parse_args2():
#     """Argument parser for load series"""
#     parser = argparse.ArgumentParser(
#         description='Read a serail_number and check to save')
    
#     parser.add_argument('-s',
#                         dest='series_num',
#                         type=str)
#     _args = parser.parse_args()

#     return _args

def main():
    args = parse_args()
    global series_num
    try:
        if zipfile.is_zipfile(args.input_file):
            zip_archive = zipfile.ZipFile(args.input_file, 'r')
            file_list = unzip(zip_archive)
            show_serial_num(file_list)
            
            series_num = input("\nTarget serial number is : ")
            file_list2 = unzip(zip_archive)

            # print(type(series_num))
            get_dicom_info(file_list2, series_num)
        # elif tarfile.is_tarfile(args.input_file):
        #     tar_archive = TarFile.open(name=args.input_file, mode='r')
        #     file_list = untar(tar_archive)
        #     show_serial_num(file_list)
        #     series_num = input("Target serial number is : ")
        #     get_dicom_info(file_list, series_num)
        else:
            print("Unknown format")
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    main()

