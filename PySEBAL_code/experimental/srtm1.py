# conda install -c conda-forge elevation
# conda install -c conda-forge make
# conda install -c conda-forge curl
# conda install -c conda-forge gdal

# Todo : checking bounds of landsat using gdal
# Landsat details

MAP_PROJECTION = "UTM"
DATUM = "WGS84"

CORNER_UL_LAT_PRODUCT = 31.34089
CORNER_UL_LON_PRODUCT = 70.83034
CORNER_UR_LAT_PRODUCT = 31.39724    # right top
CORNER_UR_LON_PRODUCT = 73.28450    # right top
CORNER_LL_LAT_PRODUCT = 29.19960    # left bottom
CORNER_LL_LON_PRODUCT = 70.92003    # left bottom
CORNER_LR_LAT_PRODUCT = 29.25134
CORNER_LR_LON_PRODUCT = 73.32151

'''
elevation.clip(bounds=(12.35, 41.8, 12.65, 42), output='Rome-DEM.tif')

The --bounds option accepts latitude and longitude coordinates 
(more precisely in geodetic coordinates in the WGS84 reference system EPSG:4326 ) 
given as left bottom right top 

 

attempt 1 : Failed 
too large an extent given 12 tiles

datasource.py line 169
def seed(cache_dir=CACHE_DIR, product=DEFAULT_PRODUCT, bounds=None, max_download_tiles=9, **kwargs):

'''

import elevation

outdir = "F:\SEBAL\datasets\dem\LBDC\\"
# elevation.clip(bounds=(
#                         CORNER_LL_LAT_PRODUCT, CORNER_LL_LON_PRODUCT, \
#                         CORNER_UR_LAT_PRODUCT, CORNER_UR_LON_PRODUCT), \
#                         output=outdir + 'LBDC-DEM.tif')

# got custom cordinates from QGIS
# elevation.clip(bounds=(
#                         30.62107, 73.311834, \
#                         30.92171, 73.79356), \
#                         output='LBDC-DEM.tif')
elevation.clip(bounds=(12.35, 41.8, 12.65, 42), output='Rome-DEM.tif')
elevation.clean()









