#------------------------------------------
#------------- Shape Files ----------------
#------------------------------------------

shapefile_swf = 'D:\SEBAL\datasets\shapefiles\SWF\swf.shp'
SHAPEFILE = shapefile_swf

#------------------------------------------
#------------- Landsat 8/9 ----------------
#------------------------------------------

landsat_swf = 'D:\SEBAL\datasets\landsat\swf\\'
LANDSAT_INDIR = landsat_swf

MODIS_INDIR = 'D:\SEBAL\datasets\MODIS\\rabi_2023_24\\'

#------------------------------------------
#------------- Meteo Files ----------------
#------------------------------------------

BULK_DOWNLOAD = True
# METEO_INDIR = 'D:\SEBAL\datasets\meteo\swf\\'
METEO_INDIR_TEMP = 'D:\SEBAL\datasets\meteo\swf_mod\GLDAS_NOAH025_3H_2.1-20240822_074759\\'
METEO_INDIR = 'D:\SEBAL\datasets\meteo\swf_mod\\'
MISSING_DATES = ['20231208', '20231216']

# MOD09GA is associated with the Terra satellite (0530 GMT) ~ landsatoverpass
LANDSAT_OVERPASS = "0600"
BULK_PROCESSING = True

#------------------------------------------
#------------- HiHydroSoil ----------------
#------------------------------------------

SOIL_INDIR = "D:\SEBAL\datasets\soil\HiHydroSoil_250m\Top_Subsoil\\"
SOIL_OUTDIR = "D:\SEBAL\datasets\soil\\"

#------------------------------------------
#------------- Excel Helper ---------------
#------------------------------------------

DOCS_INDIR = "D:\SEBAL\PySEBAL_dev\docs\\"
SEBAL_OUTDIR = "D:\SEBAL\datasets\SEBAL_out\swf\\"
IMAGE_TYPE = 3