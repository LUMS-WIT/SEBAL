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

#------------------------------------------
#------------- Meteo Files ----------------
#------------------------------------------

BULK_DOWNLOAD = True
METEO_INDIR = 'D:\SEBAL\datasets\meteo\swf\\'
MISSING_DATES = ['20231208', '20231216']

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