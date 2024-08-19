from osgeo import gdal
import numpy as np
import os, glob, shutil, sys, requests, datetime
from osgeo_utils.gdal_calc import Calc

from utils import *


shapefile_PAK = 'F:\SEBAL\shapefiles\Pakistan\gadm41_PAK_shp\gadm41_PAK_0.shp'
shapefile_LBDC_149039 = r'D:\\Hamza\\SEBAL\\shapefiles\\LBDC\\149039\\ALPSMLC30_LBDC_149039_sub_v2.shp'
shapefile_LBDC_150039 = r'D:\\Hamza\\SEBAL\\shapefiles\\LBDC\\150039\\ALPSMLC30_LBDC_150039_sub_v3.shp'
shapefile_mmm = 'D:\Hamza\SEBAL\shapefiles\Def_mmm\def_test_extent.shp'

shapefile_swf = 'D:\SEBAL\datasets\shapefiles\SWF\swf.shp'


shapefile = shapefile_swf

'''
print('-----------------------------------------')
print('------- Unziping Landsat8/9 Data --------')
print('-----------------------------------------')

indir_tar = "D:\SEBAL\datasets\landsat\swf\\"
untar_bulk(indir_tar)
'''
'''
print('-----------------------------------------')
print('------ Validating Landsat8/9 Data -------')
print('-----------------------------------------')

indir_landsat = "D:\\Hamza\\SEBAL\\datasets\\landsat\\LBDC_exp\\149039\\"

validate_landsat(indir_landsat, count=24, size= 1010)
'''

'''
#===============================================================================
print('----------------------------------------')
print('------- Downloading GLDAS Meteo --------')
print('----------------------------------------')

# Please Follow the guide before downloading data from NASA Server
# https://disc.gsfc.nasa.gov/information/documents?title=Data%20Access
# step 1 : create an account
# step 2 : authorize  NASA GESDISC DATA ARCHIVE via you raccount
# step 3 : verify  NASA GESDISC DATA ARCHIVE is in Accepted EULA
# step 4: create the pre=requiste file for authentications using following
# https://disc.gsfc.nasa.gov/information/howto?title=How%20to%20Generate%20Earthdata%20Prerequisite%20Files
# Note .netrc , .urs_cookies file in home dir and .dodrc in project dir


meteo_bulk_download = True
outdir_gldas = "D:\\Hamza\\SEBAL\\datasets\\meteo\\def_mmm\\test\\"


if meteo_bulk_download:
    
    print("\nBulk Downloading GLDAS NOAH Meterological data")
    # indir = "F:\SEBAL\datasets\landsat\LBDC_exp\\new\\"
    indir = r"D:\\Hamza\\SEBAL\\datasets\\landsat\\LBDC_exp\\149039\\pending\\"

    # path = indir + "*.tar*"
    # files = glob.glob(path)
    files = os.listdir(indir)

    print('Total Meterological Dates to download :', len(files))

    i = 1
    for tarf in files:

        # Specify the path to the tar archive file you want to untar
        tar_filename_path = tarf
        tar_filename = tar_filename_path.split('\\')[-1]
        date = tar_filename.split("_")[3]

        year = int(date[:4])
        month = int(date[4:6])
        day = int(date[-2:])

        input_date = datetime.date(year, month, day)

        outdir = outdir_gldas + "{}\\".format(date)
        os.makedirs(outdir, exist_ok=True)

        print( f"\n\t\t\t\t------- Downloading GLDAS for date : {date}, Progress : {i} / {len(files)} ------- \n", )
        print(outdir)
        try :
            download_gldas(input_date, outdir)
        except:
            print(f"\nFailed to download {date}")
        i = i + 1

else:

    print("\nDownloading GLDAS NOAH Meterological data for specific date")
    # enter the date for downloading data
    missing_dates = ['20230508', '20230516', '20230524' ]
    
    for date in missing_dates:

        year = int(date[:4])
        month = int(date[4:6])
        day = int(date[-2:])

        input_date = datetime.date(year, month, day)

    
        outdir = outdir_gldas + "{}\\".format(date)

        print(outdir)
        try :
            download_gldas(input_date, outdir)
        except:
            print(f"Failed to download {date}")

    print('\nDownload Completed .........')

print('----------------------------------------')
print('------- Validating GLDAS Meteo ---------')
print('----------------------------------------')

validate_gldas(outdir_gldas, count=8, size= 145)

'''

#===============================================================================

def meteo_processing (indir, outdir, shapefile, ncdate = "A20210609"):

    # Landsat 8 / 9 overpass ~ 5:45
    # Modis "Terra" overapss ~ 6:15 / 05:43 (Needs validation)
    # Modis "Aqua" overpass ~ 8:15 and 21:35 (alternating days)

    # overpass date estimation (landsat)
    # https://landsat.usgs.gov/landsat_acq
    # orbital overpass time :
    # https://www.ssec.wisc.edu/datacenter/polar_orbit_tracks/ 
    satoverpass = "0600"
    params = ['Tair', 'Psurf', 'Wind', 'SWdown', 'Rh']
    
    # Create or empty output folder	
    tempdir = outdir + "temp\\"	
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)
    os.makedirs(tempdir)     
    
    print('----------------------------------------')
    print('------ Converting NetCDF to Tif --------')
    print('----------------------------------------')
    
    # step 1 : convert Netcdf to tiff
    # todo : make date automatic
    netCDF_to_tif(indir, tempdir, ncdate)

    print('----------------------------------------')
    print('-------- Extracting the Region ---------')
    print('----------------------------------------')

    # step 2 : crop the region
    crop_region(tempdir, tempdir, shapefile)

    print('--------------------------------------------------')
    print('--- Generating Instantanous and Daily Averages ---')
    print('--------------------------------------------------')
    
    # step 3 : get instantenous and daily averages  
    for param in params:
        print('------------------------------------------')
        print('------- Generating Maps for %s -------' %(param))
        print('------------------------------------------')
        get_meteo(tempdir, outdir, satoverpass, param= param)
        
    # step 4 : clear temp files
    print('----------------------------------------')
    print('-------- Removing Temp Files -----------')
    print('----------------------------------------')
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)        
    print('-------- Done : Good Job -----------')

    return

meteo_bulk_processing = True

startTime_meteo = datetime.datetime.now()
if meteo_bulk_processing:
    print("Bulk Processing Meterological data based on input dir")
    indir_meteo = "D:\SEBAL\datasets\meteo\swf\\"
    # indir_meteo = "D:\\Hamza\\SEBAL\\datasets\\meteo\\def_mmm\\"

    folders = glob.glob(indir_meteo + "*\\", recursive = True)
    total_folders = len(folders)
    i = 1
    for indir in folders:
        
        name = indir.split("\\")[-2] # last one is blank space
        ncdate = "A" +  name

        print( f"\n\t\t\t\t------- Processing GLDAS for date : {name}, Total Processed : {i} / {total_folders} ------- \n", )

        outdir = indir_meteo + name + "_out\\"
        meteo_processing (indir, outdir, shapefile, ncdate=ncdate)
        i = i + 1

else:
    indir_meteo = 'F:\\SEBAL\\datasets\\meteo\\Downloads\\20210609\\'
    outdir_meteo = 'F:\\SEBAL\\datasets\\meteo\\Downloads\\20210609_out\\'
    meteo_processing (indir_meteo, outdir_meteo, shapefile, ncdate="A20210609")

print('\n Meteorological Processing Execution time :', datetime.datetime.now() - startTime_meteo)

#=============================================================================================================================
#------------------------------------------
#------- Filling the excel sheet ----------
#------------------------------------------

'''
# Example usage
excel_file_path = 'D:\\Hamza\\SEBAL\\PySEBAL_dev\\docs\\files_info.xlsx'
landsat_folder_path = r"D:\Hamza\SEBAL\datasets\landsat\def_mmm\test"
base_meteo_path = r"D:\Hamza\SEBAL\datasets\meteo\def_mmm\test"
base_output_path = r"D:\Hamza\SEBAL\datasets\SEBAL_out\def_mmm\test"

folder_paths, folder_names = get_folders_in_folder(landsat_folder_path)
write_to_excel(folder_paths, folder_names, base_output_path, base_meteo_path, excel_file_path)
'''

#=============================================================================================================================

'''
# convert crs
print('\n------- Converting CRS to WGS84 EPSG 4326 --------')
input_path = r'F:/SEBAL/datasets/SEBAL_out/LBDC/150039/'
output_path = r'F:/SEBAL/datasets/validation/LBDC_validations/150039/'

path = input_path + "**/*.tif"
#Use glob to find all TIFF files in subdirectories
files = glob.glob(path, recursive=True)

if not os.path.isdir(output_path):
    os.makedirs(output_path)

# Filter the list to include only files with "Top_soil_moisture" in their name
for filename in files:
    if filename.endswith(".tif") and pattern in filename:        
        convert_crs(filename, output_path, crs = 4326)

'''

'''
# validations

print('----------------------------------------------')
print('------- Initiating Validation (QA4SM) --------')
print('----------------------------------------------')

# convert crs
print('\n------- Converting CRS to WGS84 EPSG 4326 --------')

indir = "D:\\Hamza\\SEBAL\\datasets\\SEBAL_out\\LBDC_exp\\150039\\"
outdir = "D:\\Hamza\\SEBAL\\datasets\\validations\\150039\\"

path = indir + "**/*.tif"
# Use glob to find all TIFF files in subdirectories
files = glob.glob(path, recursive=True)

tempdir = outdir + 'temp\\'
if not os.path.isdir(tempdir):
    os.makedirs(tempdir)	
# Filter the list to include only files with "Top_soil_moisture" in their name
filtered_files = [file for file in files if "Top_soil_moisture" in file]
for file in filtered_files:
    convert_crs(file, tempdir, crs = 4326)

print('\n------- Writing time series pySebal soil moisture outputs to netCDF format --------')

write_netCDF(tempdir, outdir, version = 1)

print('\n------- Removing temporary files --------')
if os.path.exists(tempdir) and os.path.isdir(tempdir):
    # Remove the directory and all its contents
    shutil.rmtree(tempdir)

print('\n------- Operation complete --------')
'''
'''
#===============================================================================
print('---------------------------------------------')
print('------- HiHydro Soil Data Processing --------')
print('---------------------------------------------')
# soil processing (HiHydro)

def soil_processing (indir, outdir, shapefile):


    # Create or empty output folder	
    tempdir = outdir + "temp\\"	
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)
    os.makedirs(tempdir)

    print('----------------------------------------')
    print('-------- Extracting the Region ---------')
    print('----------------------------------------')

    # step 1 : Perform Region Cropping
    # read from indir and save in tempdir
    path = indir + './**/*.tif'
    files = glob.glob(path, recursive=True)
    for filename in files:
          crop_region_basic(filename, tempdir, shapefile)

    print('----------------------------------------')
    print('-------- Downscaling Soil Data ---------')
    print('----------------------------------------')

    # step 2 : Perform Downscaling
    # read from tempdir and save in indir
    soil_downscaling(tempdir, outdir, factor = 0.0001)

    
    print('----------------------------------------')
    print('-------- Removing Temp Files -----------')
    print('----------------------------------------')
    
    # step 3 : Delete tempdir
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)
    
    print('-------- Done : Good Job -----------')

    return

indir_soil = "D:\Hamza\SEBAL\datasets\soil\HiHydroSoil_250m\Top_Subsoil\\"
outdir_soil = "D:\Hamza\SEBAL\datasets\soil\def_mmm\\"
soil_processing(indir_soil, outdir_soil, shapefile )
'''
#===============================================================================
'''
print('-------------------------------')
print('------- DEM Processing --------')
print('-------------------------------')

infile = 'F:\SEBAL\datasets\dem\ALPSMLC30_PAK.tif'
outdir = 'F:\SEBAL\datasets\dem\\'
shapefile_LBDC = 'F:\SEBAL\shapefiles\LBDC\LBDC_dissolved.shp'


crop_region_basic(infile, outdir, shapefile_LBDC)
# crop_region_basic(infile, outdir, shapefile)
'''