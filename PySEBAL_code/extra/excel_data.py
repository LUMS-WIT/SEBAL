import os
import openpyxl

# Function to get the absolute paths and names of all (sub)folders in a folder
def get_folders_in_folder(folder_path):
    folder_paths = []
    folder_names = []
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            folder_path = os.path.join(root, dir)
            folder_paths.append(os.path.abspath(folder_path))
            folder_names.append(dir)
    return folder_paths, folder_names

# Function to extract date from folder name
def extract_date_from_folder_name(folder_name):
    parts = folder_name.split('_')
    if len(parts) >= 4:
        return parts[3]
    return None

# Function to write folder paths and names to an Excel sheet
def write_to_excel(folder_paths, folder_names, base_output_path, base_meteo_path, excel_file_path):
    workbook = openpyxl.Workbook()
    
    # Creating General_Input sheet
    general_input_sheet = workbook.active
    general_input_sheet.title = 'General_Input'

    # Writing headers for General_Input sheet
    general_input_sheet.cell(row=1, column=1, value='InputMap')
    general_input_sheet.cell(row=1, column=2, value='OutputMap')

    # Creating Landsat_Input sheet
    landsat_input_sheet = workbook.create_sheet(title='Landsat_Input')

    # Writing headers for Landsat_Input sheet
    landsat_input_sheet.cell(row=1, column=1, value='Name Landsat Image')

    # Creating Meteo_Input sheet
    meteo_input_sheet = workbook.create_sheet(title='Meteo_Input')

    # Writing headers for Meteo_Input sheet
    headers = ['Temp_inst', 'Temp_24', 'RH_inst', 'RH_24', 'Wind_inst', 'Wind_24', 'Rs_in_inst_cloud_free', 'Rs_24']
    for col, header in enumerate(headers, start=1):
        meteo_input_sheet.cell(row=1, column=col, value=header)

    # Writing folder paths and names
    for index, (folder_path, folder_name) in enumerate(zip(folder_paths, folder_names), start=2):
        output_path = os.path.join(base_output_path, folder_name)
        
        # Writing to General_Input sheet
        general_input_sheet.cell(row=index, column=1, value=folder_path)
        general_input_sheet.cell(row=index, column=2, value=output_path)
        
        # Writing to Landsat_Input sheet
        landsat_input_sheet.cell(row=index, column=1, value=folder_name)
        
        # Writing to Meteo_Input sheet
        date = extract_date_from_folder_name(folder_name)
        if date:
            temp_inst_value = f'{date}_out\GLDAS_NOAH025_3H.A{date}.0600_Tair_crop_deg_inst.tif'
            temp_24_value = f'{date}_out\GLDAS_NOAH025_3H.A{date}.Tair_crop_deg_24.tif'
            rh_inst_value = f'{date}_out\GLDAS_NOAH025_3H.A{date}.0600_Rh_crop_percent_inst.tif'
            rh_24_value = f'{date}_out\GLDAS_NOAH025_3H.A{date}.Rh_crop_percent_24.tif'
            wind_inst_value = f'{date}_out\GLDAS_NOAH025_3H.A{date}.0600_Wind_crop_ms_inst.tif'
            wind_24_value = f'{date}_out\GLDAS_NOAH025_3H.A{date}.Wind_crop_ms_24.tif'
            rs_in_inst_value = f'{date}_out\GLDAS_NOAH025_3H.A{date}.0600_SWdown_crop_Wm_inst.tif'
            rs_24_value = f'{date}_out\GLDAS_NOAH025_3H.A{date}.SWdown_crop_Wm_24.tif'
            
            temp_inst_path = os.path.join(base_meteo_path, temp_inst_value)
            temp_24_path = os.path.join(base_meteo_path, temp_24_value)
            rh_inst_path = os.path.join(base_meteo_path, rh_inst_value)
            rh_24_path = os.path.join(base_meteo_path, rh_24_value)
            wind_inst_path = os.path.join(base_meteo_path, wind_inst_value)
            wind_24_path = os.path.join(base_meteo_path, wind_24_value)
            rs_in_inst_path = os.path.join(base_meteo_path, rs_in_inst_value)
            rs_24_path = os.path.join(base_meteo_path, rs_24_value)

            meteo_input_sheet.cell(row=index, column=1, value=temp_inst_path)
            meteo_input_sheet.cell(row=index, column=2, value=temp_24_path)
            meteo_input_sheet.cell(row=index, column=3, value=rh_inst_path)
            meteo_input_sheet.cell(row=index, column=4, value=rh_24_path)
            meteo_input_sheet.cell(row=index, column=5, value=wind_inst_path)
            meteo_input_sheet.cell(row=index, column=6, value=wind_24_path)
            meteo_input_sheet.cell(row=index, column=7, value=rs_in_inst_path)
            meteo_input_sheet.cell(row=index, column=8, value=rs_24_path)

    workbook.save(excel_file_path)
    print(f"Data has been written to {excel_file_path}")

# Example usage
excel_file_path = 'D:\\Hamza\\SEBAL\\PySEBAL_dev\\docs\\files_info.xlsx'
landsat_folder_path = r"D:\Hamza\SEBAL\datasets\landsat\LBDC_exp\149039"
base_meteo_path = r"D:\Hamza\SEBAL\datasets\meteo\149039"
base_output_path = r"D:\Hamza\SEBAL\datasets\SEBAL_out\LBDC_exp\149039"

folder_paths, folder_names = get_folders_in_folder(landsat_folder_path)
write_to_excel(folder_paths, folder_names, base_output_path, base_meteo_path, excel_file_path)
