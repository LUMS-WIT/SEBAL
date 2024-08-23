import os
import re
import shutil

from config import METEO_INDIR_TEMP, METEO_INDIR

# LOGIC
# 1. read all the files in the folder and extract dates
# 2. make folder for each date in desired directory
# 3. move same dates files to corresponding dates
# 4. verfiy and remove the initial folder

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

def validate(indir, count = 8, size = 145):

    print('----------------------------------------')
    print('------- Validating GLDAS Meteo ---------')
    print('----------------------------------------')

        # Check if the specified path is a directory
    if os.path.isdir(indir):
        for folder_name in os.listdir(indir):
            folder_path = os.path.join(indir, folder_name)

            # Check if the item in the directory is a sub-directory
            if os.path.isdir(folder_path):
                # List all files in the sub-directory and count them
                files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                file_count = len(files)
                folder_size = get_folder_size(folder_path) / (1024 * 1024)

                if file_count < count:
                    print(f"Folder: {folder_name}, Number of Files: {file_count}")
                elif file_count == count and folder_size < size:
                    print(f"Folder: {folder_name}, Number of Files: {file_count}, Size (MB): {folder_size:.2f} MB")
                else:
                    print(f"Folder: {folder_name}, SAT")

def organize_files_by_date(source_folder, destination_base_folder):

    print('----------------------------------------')
    print('------- Organizing GLDAS Meteo ---------')
    print('----------------------------------------')

    # Regular expression to extract the date from the file name
    date_pattern = re.compile(r'\.A(\d{8})\.')
    
    # Dictionary to hold files categorized by date
    files_by_date = {}

    # Step 1: Read all files in the folder and extract dates
    for file_name in os.listdir(source_folder):
        match = date_pattern.search(file_name)
        if match:
            date = match.group(1)  # Extracted date (e.g., "20231208")
            if date not in files_by_date:
                files_by_date[date] = []
            files_by_date[date].append(file_name)

    # Step 2: Make folder for each date in the desired directory
    for date, files in files_by_date.items():
        date_folder_path = os.path.join(destination_base_folder, date)
        os.makedirs(date_folder_path, exist_ok=True)
        
        # Step 3: Move same date files to the corresponding date folder
        for file_name in files:
            source_file_path = os.path.join(source_folder, file_name)
            destination_file_path = os.path.join(date_folder_path, file_name)
            shutil.move(source_file_path, destination_file_path)
            print(f"Moved {file_name} to {date_folder_path}")

    # Step 4: Verify if the source folder is empty
    remaining_files = os.listdir(source_folder)
    if not remaining_files:
        print(f"All files have been moved. Deleting empty source folder: {source_folder}")
        os.rmdir(source_folder)
    else:
        print(f"The source folder is not empty. Remaining files:")
        for file in remaining_files:
            print(file)


if __name__ == "__main__":
    
    organize_files_by_date(METEO_INDIR_TEMP, METEO_INDIR)
    validate(METEO_INDIR)