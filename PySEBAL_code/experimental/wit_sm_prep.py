#!/usr/bin/env python

import os
import pandas as pd
import shutil


years = ['2023', '2022', '2021']
# Define the directory where you want to save the renamed files
new_folder = "F:\SEBAL\datasets\WIT_SM\\SMS\\"
'''
# Ensure the new folder exists or create it if it doesn't
if not os.path.exists(new_folder):
    os.makedirs(new_folder)

metadata = "F:\SEBAL\datasets\WIT_SM\\SMS Data.xlsx"

for year in years:

    # Define the directory where your files are located
    original_folder = f"F:\SEBAL\datasets\WIT_SM\\Nestle SMS Data {year}\\"



    # List all files in the original folder
    files = os.listdir(original_folder)
    files = sorted(files)



    df = pd.ExcelFile(metadata)

    df_sheet = df.sheet_names

    df = pd.read_excel(metadata, sheet_name=year)
    # Assuming 'Index' is the column used for indexing
    index_column = 'Sr No.'
    lon_column = 'Longitude'
    lat_column = 'Latitude'
    # Get the row where the 'Index' column matches the value '5'

    # Iterate through each file in the folder
    i = 1
    for index, file_name in enumerate(files):

        desired_index = int(file_name.split(" ")[0])
        Latitude = df.loc[df[index_column] == desired_index, lat_column].values[0]
        Longitude = df.loc[df[index_column] == desired_index, lon_column].values[0]

        #print(desired_index, Latitude, Longitude)

        
        # Construct the new file name as per your requirement
        desired_index = str(desired_index).zfill(3)
        new_file_name = f"witsms_gpi={year + desired_index}_lat={Latitude}_lon={Longitude}.csv"  # Replace with your naming convention

        # Construct the full file paths for the old and new locations
        old_file_path = os.path.join(original_folder,file_name)
        new_file_path = os.path.join(new_folder, new_file_name)
        

        # Rename and copy the file to the new location

        shutil.copy(old_file_path, new_file_path)

        i +=1
    print('Total number of files :',i)

'''




# List all files in the original folder

indir = r"F:/SEBAL/datasets/WIT_SM/SMS/"
outdir =  r"F:/SEBAL/datasets/WIT_SM/SMS_final_v2/"

files = os.listdir(indir)
files = sorted(files)
k =0
for file in files:

    file_path = os.path.join(indir,file)
    
    
    print(file_path)

    df=pd.read_csv(file_path, skiprows= 4)

    vw=df['VolumetricWaterContent1']
    time_stamp=df['TimeStamp']

    if '20220' in file_path or '20230' in file_path or '20221' in file_path:
        time_stamp = pd.to_datetime(time_stamp, format='mixed')
    
    else:
        time_stamp = pd.to_datetime(time_stamp)
    
    df['TimeStamp'] = time_stamp.dt.strftime('%Y-%m-%d %H:%M:%S')

    filtered_data = vw[(vw >= 0) & (vw <= 50)]
    filtered_indices = filtered_data.index.tolist()

    filtered_datetime_column = df.loc[filtered_indices, 'TimeStamp']

    #filtered_data_final = pd.DataFrame({'': filtered_datetime_column, 'Volumetric Water Content':filtered_data})
    filtered_data_final = pd.concat([filtered_datetime_column,filtered_data], axis=1)
    filtered_data_final.columns = ['TimeStamp', 'soil_moisture']

    filtered_data_final['TimeStamp'] = pd.to_datetime(filtered_data_final['TimeStamp'])

    daily_mean = filtered_data_final.resample('D', on='TimeStamp').mean()


    daily_mean.index += pd.DateOffset(hours=0.5)
    daily_mean.index.name = 'TimeStamp'


    file_path = os.path.join(outdir,file)
    daily_mean.to_csv(file_path, float_format='%.3f')
    k +=1
    
print('Total number of final files :',k)