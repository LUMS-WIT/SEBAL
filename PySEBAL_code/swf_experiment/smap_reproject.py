from raster_resampling import reproject
import os, glob

spatial_res = '3km'
pattern = f'Soil_Moisture_Retrieval_Data_{spatial_res}_soil_moisture_{spatial_res}_'
# pattern = 'Root_zone_moisture'

# # convert crs
# print('\n------- Converting CRS to WGS84 EPSG 4326 --------')
input_path = r'D:\SEBAL\datasets\SMAP\\'
output_path = f'D:\SEBAL\datasets\SMAP\\swf_sm_{spatial_res}\\'

if not os.path.isdir(output_path):
    os.makedirs(output_path)

path = input_path + "**/*.tif"
#Use glob to find all TIFF files in subdirectories
files = glob.glob(path, recursive=True)
for filename in files:
    if filename.endswith(".tif") and pattern in filename:             
        reproject(filename, output_path)
