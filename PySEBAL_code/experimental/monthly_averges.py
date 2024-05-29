import os
from osgeo import gdal
from osgeo_utils.gdal_calc import Calc
from calendar import monthrange

soil_moisture = "Root_zone_moisture" #Top_soil_moisture Or Root_zone_moisture
# Specify the directory you want to search
directory_to_search = "F:\\SEBAL\\datasets\\SEBAL_out\\def_mmm"
output_directory = "F:\\SEBAL\\datasets\\SEBAL_out\\def_mmm_monthly_averages"


def list_specific_tif_files(directory, file_type):
    tif_files = []
    # Adjust the pattern based on input
    pattern = f"{file_type}_30m_"
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".tif") and pattern in file:
                tif_files.append(os.path.join(root, file))
    return tif_files

# Function to process and save monthly maps
def process_monthly_maps(tif_files, output_directory, file_type):
    print('STEP 1: Averaging and multiplying by number of days per month')
    monthly_data = {}
    for file_path in tif_files:
        file = os.path.basename(file_path)
        file = file.split('\\')[-1]
        parts = file.split('_')
        year, month, date = parts[5], parts[6], parts[7]
        month_key = f"{year}_{month}"
        if month_key not in monthly_data:
            monthly_data[month_key] = []
        monthly_data[month_key].append(file_path)
    
    for month, file_paths in monthly_data.items():
        average_file = os.path.join(output_directory, f'{month}_{file_type}_average.tif')
        # Setup the formula and input files dictionary
        inputs = {f'A{i+1}': file_paths[i] for i in range(len(file_paths))}
        formula = "(" + "+".join(inputs.keys()) + f")/{len(file_paths)}"
        Calc(calc=formula, outfile=average_file, NoDataValue=0, overwrite=True, **inputs)
        # Multiply by days in the month
        year, month = month.split('_')
        days = monthrange(int(year), int(month))[1]
        final_file = os.path.join(output_directory, f'{month}_{file_type}_final.tif')
        Calc(calc=f"A*{days}", outfile=final_file, A=average_file, overwrite=True)


# Specify the type of files to search ("Top_soil_moisture" or "Root_zone_moisture")
file_type = soil_moisture
# Get the list of .tif files based on the type
tif_files = list_specific_tif_files(directory_to_search, file_type)

# # Print the list of .tif files
# for file in tif_files:
#     print(file)

# print(len(tif_files))

# Ensure the output directory exists
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Process monthly maps
process_monthly_maps(tif_files, output_directory, file_type)
