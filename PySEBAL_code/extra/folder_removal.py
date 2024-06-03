import os
import shutil

def list_and_delete_folders(directory, regx= '_out'):
    # List to keep track of folders ending with '_out'
    out_folders = []

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name.endswith(regx):
                full_path = os.path.join(root, dir_name)
                out_folders.append(full_path)

    # Print all folders ending with '_out'
    print(f"Folders ending with {regx}:")
    for folder in out_folders:
        print(folder)

    # Delete the folders and their contents
    for folder in out_folders:
        shutil.rmtree(folder)
        print(f"Deleted folder and contents: {folder}")

# Example usage
directory_to_search = 'D:\\149039\\'
list_and_delete_folders(directory_to_search, '_vegetation')
