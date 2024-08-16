import os, glob
import shutil
import datetime

from utils import netCDF_to_tif, crop_region, crop_region_subpixel, get_meteo
from config import LANDSAT_OVERPASS, SHAPEFILE, METEO_INDIR, BULK_PROCESSING, MISSING_DATES

def meteo_processing (indir, outdir, shapefile, ncdate = "A20210609"):

    # Landsat 8 / 9 overpass ~ 5:45
    # Modis "Terra" overapss ~ 6:15 / 05:43 (Needs validation)
    # Modis "Aqua" overpass ~ 8:15 and 21:35 (alternating days)

    satoverpass = LANDSAT_OVERPASS
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
    try:
        # TODO: Outphase crop_region with subpixel to use gdal.translate for region cropping 
        crop_region(tempdir, tempdir, shapefile)
    except:
        print('Shapefile is sub-pixel. Modifying to include atleast one pixel')
        crop_region_subpixel(tempdir, tempdir, shapefile)

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

if __name__ == "__main__":

    startTime_meteo = datetime.datetime.now()
    indir_meteo = METEO_INDIR
    
    if BULK_PROCESSING:
        print("Bulk Processing Meterological data based on input dir")
        
        folders = glob.glob(indir_meteo + "*\\", recursive = True)
        total_folders = len(folders)
        i = 1
        for indir in folders:
            
            name = indir.split("\\")[-2] # last one is blank space
            ncdate = "A" +  name

            print( f"\n\t\t\t\t------- Processing GLDAS for date : {name}, Total Processed : {i} / {total_folders} ------- \n", )

            outdir = indir_meteo + name + "_out\\"
            meteo_processing (indir, outdir, SHAPEFILE, ncdate=ncdate)
            i = i + 1

    else:
        for date in MISSING_DATES:
            ncdate = "A" +  date
            indir = METEO_INDIR  + "{}\\".format(date)
            outdir = METEO_INDIR + "{}_out\\".format(date)

            meteo_processing (indir, outdir, SHAPEFILE, ncdate=ncdate)


        # indir_meteo = 'F:\\SEBAL\\datasets\\meteo\\Downloads\\20210609\\'
        # outdir_meteo = 'F:\\SEBAL\\datasets\\meteo\\Downloads\\20210609_out\\'
        # meteo_processing (indir_meteo, outdir_meteo, SHAPEFILE, ncdate="A20210609")

    print('\n Meteorological Processing Execution time :', datetime.datetime.now() - startTime_meteo)

