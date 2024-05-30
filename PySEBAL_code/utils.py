from osgeo import gdal, osr
import numpy as np
import os, glob, shutil, sys, requests, tarfile, datetime
from tqdm import tqdm
from osgeo_utils.gdal_calc import Calc
import netCDF4
import openpyxl
'''
----------------------------------------------------------------
---------- Downloading NASA Lansat 8/9 Data --------------------
----------------------------------------------------------------
'''
# ---------- Unzip NASA Lansat 8/9 Data --------------------

def untar_bulk(indir):
    """
    Bulk Unzip .tar files

    Parameters
    ----------
    indir : str
        path to input directory containing .tar files
    """
    
    path = indir + "*.tar*"
    files = glob.glob(path)
    
    for tarf in files:

        # Specify the path to the tar archive file you want to untar
        tar_filename_path = tarf
        tar_filename = tar_filename_path.split('\\')[-1]

        # Specify the directory where you want to extract the contents
        extract_dir = indir + tar_filename.replace(".tar","")
        os.makedirs(extract_dir, exist_ok=True)


        # Open the tar archive file for reading
        with tarfile.open(tar_filename_path, 'r') as tf:
            for member in tqdm(tf.getmembers(), desc='Extracting '):
                try:
                    tf.extract(member, extract_dir)
                except tarfile.TarError as e:
                    pass

                
        print(f"Contents of '{tar_filename}' have been extracted to '{extract_dir}'")


def validate_landsat(indir, count = 24, size = 1010):
    """
    counts the number of downloaded landsat files in each directory and 
    checks the size of each directory

    Parameters
    ----------
    indir : str
        path to reference directory
    """
    i = 1

    def get_folder_size(folder_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return total_size

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
                    i = i + 1
                elif file_count == count and folder_size < size:
                    print(f"Folder: {folder_name}, Number of Files: {file_count}, Size (MB): {folder_size:.2f} MB")
                    i = i + 1
                else:
                    print(f"Folder: {folder_name}, SAT")
    else:
        print(f"The specified path '{indir}' is not a directory.")
    
    if i ==1:
        print(" \n----- Landsat Download : All SAT -----")
    return

'''
------------------------------------------------------------------
-------- Downloading GLDAS NOAH 2.5 Meteo Data -------------------
------------------------------------------------------------------
'''

def download_gldas(date, outdir):
    """
    Downloads NASA GES DISC data for a specific date.
    https://hydro1.gesdisc.eosdis.nasa.gov/data/GLDAS/GLDAS_NOAH025_3H.2.1/

    Parameters
    ----------
    date : obj
       datetime object
    outdir : str
        path to dir for saving data
    """

    # step 1 : construct base url from input date
    year = date.year
    doy = date.timetuple().tm_yday
    month = date.month
    day = date.day  
    # hour = date.hour
    temporal_cont = f"A{year}{month:02d}{day:02d}"

    base_url = 'https://hydro1.gesdisc.eosdis.nasa.gov/data/GLDAS/GLDAS_NOAH025_3H.2.1/{year}/{doy:03d}/GLDAS_NOAH025_3H.{temporal_content}.{hour}00.021.nc4'

    # step 2 : based on time stamps, construct all possible url(s)    
    time_stamps = ["00", "03", "06", "09", "12", "15", "18", "21"]
    urllist = []
    for hour in time_stamps:
        url = base_url.format(year = year, doy = doy, temporal_content = temporal_cont, hour = hour)
        urllist.append(url)

    # step 3 : download urls and save them in out dir
    for url in urllist:
        file = url.split('/')[-1]
        filename = outdir + file
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            with open(filename, "wb") as f:
                print("\nDownloading %s" % file)
                
                total_length = response.headers.get('content-length')

                if total_length is None: # no content length header
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        dl += len(data)
                        f.write(data)
                        done = int(100 * dl / total_length)
                        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (100-done)) )    
                        sys.stdout.flush()
        else:
            print(f"Failed to download {file}. Status code: {response.status_code}, reason: {response.reason}.")
    
    return

def validate_gldas(indir, count = 8, size = 145):
    """
    counts the number of downloaded meteo files in each directory and 
    checks the size of each directory

    Parameters
    ----------
    indir : str
        path to reference directory
    """
    i = 1

    def get_folder_size(folder_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return total_size

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
                    i = i + 1
                elif file_count == count and folder_size < size:
                    print(f"Folder: {folder_name}, Number of Files: {file_count}, Size (MB): {folder_size:.2f} MB")
                    i = i + 1
                else:
                    print(f"Folder: {folder_name}, SAT")
    else:
        print(f"The specified path '{indir}' is not a directory.")
    
    if i ==1:
        print(" \n----- GLDAS Download : All SAT -----")
    return

'''
------------------------------------------------------------------
---------------------- Soil Data Processing ----------------------
------------------------------------------------------------------
'''
def crop_region_basic(filename, outdir, shapefile):
    """
    (soil) Applies a basic cropping function on tiff file using gdal wrap function 
    and shapefile extent.

    Parameters
    ----------
    filename : str
        path to input raster on which cropping is to be applied 
    outdir : str
        path to output dir
    shapefile : str
        path to shapefile required for extent 

    Usage
    -----
    path = './**/*.tif'
    files = glob.glob(path, recursive=True)
    for filename in files:
          crop_region_basic(filename, outdir, shapefile)  
    """
    
    print('Applying Cropping for raster : ', filename)
    
    ds = gdal.Open(filename)

    filename = filename.split("\\")[-1]
    outds = os.path.join(outdir,filename)
    outds = outds.replace('.tif', '_crop.tif')

    gdal.Warp(outds, ds, cutlineDSName = shapefile, 
                   cropToCutline = True, dstNodata = np.nan, 
                   resampleAlg='cubicspline', dstSRS= "EPSG:4326"
                   )
    ds = None

    return

def soil_downscaling(indir, outdir, factor = 0.0001):
    """
    Downsacales soil input by a given factor. Output range 0-1

    Usage
    -----
    indir = "F:\SEBAL\datasets\soil\output_crop\\"
    outdir = "F:\SEBAL\datasets\soil\output_downscale\\"

    soil_downscaling(indir, outdir)

    Parameters
    ----------
    indir : str
        path to input dir
    outdir : str
        path to output dir
    factor : float, optional
        by default 0.0001
    """

    path = indir + "*.tif*"
    files = glob.glob(path)

    for filename in files:

        # no scaling for STC raster
        if filename.find('STC')<0:

            print('Applying Downscaling for raster : ', filename)

            # open raster
            ds = gdal.Open(filename)
            geo = ds.GetGeoTransform()
            proj = ds.GetProjection()

            band = ds.GetRasterBand(1)
            band.GetStatistics(1,True)
            min = band.GetMinimum()

            array = ds.GetRasterBand(1).ReadAsArray()

            # mask nan values
            # perform scaling
            min = min * factor
            array = array * factor
            array = np.where(array < min, np.nan, array)

            # write raster
            # call driver
            driver = gdal.GetDriverByName("GTiff")
            driver.Register()

            outname = outdir + filename.split("\\")[-1]

            outds = driver.Create(outname, xsize = array.shape[1], 
                                ysize = array.shape[0], bands = 1,
                                eType = gdal.GDT_Float32)

            # set geotranform and projection
            outds.SetGeoTransform(geo)
            outds.SetProjection(proj)

            # open create data set
            outband = outds.GetRasterBand(1)
            # write in that dataset
            outband.WriteArray(array)
            # set no data value
            outband.SetNoDataValue(np.nan)


            # flush cache
            outband.FlushCache()
            # Close data set and Band
            outds = None
            outband = None    

        else:
            print("Copying raster : ", filename)
            outname = outdir + filename.split("\\")[-1]  
            shutil.copy2(filename,outname)
    
    return

'''
------------------------------------------------------------------
----------------- Meteorolgical Data Processing ------------------
------------------------------------------------------------------
'''

def netCDF_to_tif(indir, outdir, ncdate):
    """
    Converts GLDAS NOAH2.5 NC4 files to tiff
    
    Usage
    -----
    indir = 'meteo\\'
    outdir = 'meteo_out\\'
    ncdate = "A20210524"
    
    netCDF_to_tif(indir, outdir, ncdate)


    Parameters
    ----------
    indir : str
        path to input dir
    outdir : str
        path to output dir
    ncdate : str
        date in GLDAS format
    """

    acqtime = ["00", "03", "06", "09", "12", "15", "18", "21"]
    inparams = ["Qair_f_inst", "Psurf_f_inst", "Tair_f_inst", "Wind_f_inst", "SWdown_f_tavg"]

    transOptions = gdal.TranslateOptions(outputSRS="EPSG:4326", 
                                format='GTiff',
                                noData= np.nan, 
                                xRes=0.25, yRes=0.25
                                )

    for t in acqtime:
        
        for param in inparams:

            outparam = param.split('_')[0]

            ds = gdal.Translate(outdir+"GLDAS_NOAH025_3H.%s.%s00_%s.tif" % (ncdate, t, outparam), 
                "NETCDF:"+indir+"GLDAS_NOAH025_3H.%s.%s00.021.nc4:%s" % (ncdate, t, param), 
                options = transOptions)
            ds = None
    
    return

def crop_region(indir, outdir, shapefile):
    """
    (meteo) using gdal wrap function and shapefile extent,  crops and resamples tiff files

    Usage
    -----
    indir = 'meteo\\'
    outdir = 'meteo_out\\'
    shapefile = 'path\\to\\shapefile.shp'

    crop_region(indir, outdir, shapefile)

    Parameters
    ----------
    indir : str
        path to input dir
    outdir : str
        path to output dir
    shapefile : str
        path to shapefile
    """
    
    # List all files
    path = indir + '*.tif'
    files = glob.glob(path, recursive=False)

    # set Wrap Options
    wrapOptions = gdal.WarpOptions(cutlineDSName = shapefile, 
                    cropToCutline = True, dstNodata = np.nan,
                    resampleAlg='cubicspline', dstSRS= "EPSG:4326",
                    # xRes = 0.25, yRes = 0.25,
                    #options='overwrite'
                    )

    for filename in files:

        print('Applying Cropping for raster : ', filename)
        
        ds = gdal.Open(filename)

        filename = filename.split("\\")[-1]
        outds = os.path.join(outdir,filename)
        outds = outds.replace('.tif', '_crop.tif')
        
        dsclip = gdal.Warp(outds, ds, options = wrapOptions)

        ds = None
        dsclip = None
    
    return

def get_gldas_struct(filename):
    """
    Generates file structure for GLDAS NOAH2.5 Product (tif)
    reference : https://hydro1.gesdisc.eosdis.nasa.gov/data/GLDAS/GLDAS_NOAH025_3H.2.0/doc/README_GLDAS2.pdf
    
    Usage
    -----
    dict =  get_gldas_struct(GLDAS_NOAH025_3H.A20210524.0000_Qair_crop.tif)

    Parameters
    ----------
    filename : str

    Returns
    -------
    Dict
        _description_
    """
   
    structure_dict = {}

    filename = filename.split("_")

    product = filename[0]
    model_spt_res = filename[1]
    temporal_content = filename[2]
    param = filename[3]

    temp = temporal_content.split('.')
    temporal_res = temp[0]
    date = temp[1]
    time = temp[2]


    structure_dict['product name'] = product
    structure_dict['spatial resolution'] = model_spt_res
    structure_dict['temporal content'] = temporal_content
    structure_dict['parameter'] = param

    structure_dict['temporal resolution'] = temporal_res
    structure_dict['date'] = date
    structure_dict['time'] = time


    return structure_dict

def get_tif_params(ds):
    """
    Extracts the metadata from GLDAS NOAH2.5 Layer

    Usage
    -----
    ds = gdal.Open(file)
    tifmeta = get_tif_params(ds)
         
    Parameters
    ----------
    ds : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """

    
    metadata_dict = {}

    # ToDo need this meta data as global
    # Get file properties
    geo = ds.GetGeoTransform()
    proj = ds.GetProjection()
    metadata = ds.GetMetadata_Dict()
    band = ds.GetRasterBand(1)

    vmax = float(band.GetMetadataItem('vmax'))
    vmin = float(band.GetMetadataItem('vmin'))

    varname = band.GetMetadataItem('NETCDF_VARNAME')
    units = band.GetMetadataItem('units')

    metadata_dict['geotransform'] = geo
    metadata_dict['projection'] = proj
    metadata_dict['vmax'] = vmax
    metadata_dict['vmin'] = vmin

    return metadata_dict

def save_geotiff(inraster, outname, geotaransform, projection, description=None, units = None):
    """
    Saves Geotiff files from rasters generated by gdal_cal function

    Parameters
    ----------
    inraster : _type_
        _description_
    outname : _type_
        _description_
    geotaransform : _type_
        _description_
    projection : _type_
        _description_
    description : _type_, optional
        _description_, by default None
    units : _type_, optional
        _description_, by default None
    """

    array = inraster.GetRasterBand(1).ReadAsArray()

    # call driver
    driver = gdal.GetDriverByName("GTiff")
    driver.Register()

    temp = driver.Create(outname, xsize = array.shape[1], 
                        ysize = array.shape[0], bands = 1,
                        eType = gdal.GDT_Float32)

    
    band = temp.GetRasterBand(1)
    
    # set geotranform and projection
    temp.SetGeoTransform(geotaransform)
    temp.SetProjection(projection)

    if description:
        band.SetDescription(description)
    if units:
        band.SetMetadata({'units': units})

    # write in that dataset
    band.WriteArray(array)
    # set no data value
    band.SetNoDataValue(np.nan)

    # flush cache
    band.FlushCache()

    # Close data set and Band
    inraster = None
    band = None
    temp = None

    return

def daily_averages(indir, outdir, description, units):
    """
    Creates daily averages. Used along with get_meteo() function

    Arguments:
        indir -- _description_
        outdir -- _description_
        description -- _description_
        units -- _description_
    """
    # Create average using files in tempdir
    # get metada : geotranform and projection

    files = glob.glob(indir, recursive=True)
    assert len(files) != 0, "Need more then 1 file to compute averages"
    print('Total files for daily averages :', len(files))
    file_temp = files[0]
    ds_temp = gdal.Open(file_temp)

    # Get file properties
    geo = ds_temp.GetGeoTransform()
    proj = ds_temp.GetProjection()

    # Todo : standarize file paths
    outname = file_temp.split('\\')[-1]  # ['', 'meteo_out', 'GLDAS_NOAH025_3H.A20210524.0300_Tair_crop_deg.tif']
    outname = outname.split('.')    # ['GLDAS_NOAH025_3H', 'A20210524', '0300_Tair_crop_deg', 'tif']
    desc = outname[2].split("_")    # ['0300', 'Tair', 'crop', 'deg']
    desc = "_".join(desc[1:])   # 'Tair_crop_deg'
    outname = outname[0] + '.' + outname[1] + '.' + desc + '_24.tif'

    outname = outdir + outname
 

    # Get daily averages
    param_24 = Calc(A= files, outfile = "temp_24", calc = "numpy.average(A, axis=0)") 

    # save tiff file
    save_geotiff(param_24, outname, geo, proj, description = description, units = units)
    ds_temp = None
    param_24 = None
    os.remove('temp_24')

    return

def meteo_Rh_input(indir, time):
    """
    Gets the corresponding Tair_deg and Psurf_mb files required for
    Relative humidity raster calculations based on input time

    Used along with get_meteo() function

    Parameters
    ----------
    indir : _type_
        _description_
    time : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    # Tair_deg
    Tair_key = '*%s_Tair*.tif' % (time)
    Tair_path = indir + Tair_key 
    Tair_file = glob.glob(Tair_path)[0]
    assert len(Tair_file) != 0, "Corresponding Tair_deg File missing or mulitple"
    # Tair_ds = gdal.Open(Tair_file)

    # PSurf_mb
    Psurf_key = '*%s_Psurf*.tif' % (time)
    Psurf_path = indir + Psurf_key
    Psurf_file = glob.glob(Psurf_path)[0]
    assert len(Psurf_file) != 0, "Corresponding Psurf_mb File missing or mulitple"

    return Tair_file, Psurf_file



def get_meteo(indir, outdir, satoverpass, param, quiet = True):
    """
    Converts the cropped Psurf raster into desired units of mb
    Generates instaneous maps based on satellite overpass time
    Generates daily average maps

    Usage
    -----
    satoverpass = "0300" 
    indir = 'meteo_out\\'
    outdir = 'meteo_out\\'

    params = ['Tair', 'Psurf', 'Wind', 'SWdown', 'Rh']
    for param in params:
        get_meteo(indir, outdir, satoverpass, param= param)

    Parameters
    ----------
    indir : str
        path to input dir
    outdir : str
        path to output dir
    satoverpass : str
        GLDAS data closest time with satellite overpass
    param : str
        'Tair', 'Psurf', 'Wind', 'SWdown', 'Rh'
    """

    tempdir = indir + "temp\\"		
    if not os.path.isdir(tempdir):
        os.makedirs(tempdir)
   
    if param == 'SWdown':
        param_key = '*SWdown_crop*.tif'
        param_desc =  'SWdown_Wm2'
        param_unit = 'Wm'

    elif param == 'Wind':
        param_key = '*Wind_crop*.tif'
        param_desc =  'Wind_ms'
        param_unit = 'ms'

    elif param == 'Tair':
        param_key = '*Tair_crop*.tif'
        param_desc =  'Tair_deg'
        param_unit = 'deg'

    elif param == 'Psurf':
        param_key = '*Psurf_crop*.tif'
        param_desc =  'Psurf_mb'
        param_unit = 'mb'

    # note , Rh HAS to run at the end
    elif param == 'Rh':
        # meteo_Rh_mask(indir)
        param_key = '*Qair_crop*.tif'
        param_desc = "Rh"
        param_unit = 'percent' 
   
    for file in glob.glob(indir + param_key):
    
        if not quiet:
            print('Applying Unit Conversion for raster : ', file)
        
        ds = gdal.Open(file)

        # ToDo need this meta data as global
        # Get file properties
        tifmeta = get_tif_params(ds)        
        geo = tifmeta.get('geotransform')
        proj = tifmeta.get('projection')
        vmin = tifmeta.get('vmin')

        # Get File structure from input name
        name = file.split("\\")[-1]
        gldas = get_gldas_struct(name)
        time = gldas.get('time')
        product = gldas.get('product name')
        spat_res = gldas.get('spatial resolution')
        temporal = gldas.get('temporal content')
            
        masked = Calc(A= ds, outfile='temp0', calc = "numpy.where(A<%d, numpy.nan, A)" % (vmin), quiet= quiet)

        # change units
        if param == 'Psurf':
            param_ =  Calc(A= masked, outfile='temp1', calc = "A/100", quiet= quiet)
        
        elif param == 'Tair':
            param_ =  Calc(A= masked, outfile='temp2', calc = "A-273.15", quiet= quiet)
        
        elif param == 'Rh':
            # using temp dir since it contains generated masked files
            Tair_deg, Psurf_mb = meteo_Rh_input(tempdir, time)
            Qair_file = masked

            # refernce : https://earthscience.stackexchange.com/questions/2360/how-do-i-convert-specific-humidity-to-relative-humidity
            # Using To = 273.15 K
            #(a) Saturation vapor pressure
            # "es_${i} = 6.112 * exp((17.67 * GLDAS_NOAH025_3H_20210524_${i}00_Tair_deg) / (GLDAS_NOAH025_3H_20210524_${i}00_Tair_deg + 243.5))"
            es = Calc(A = Tair_deg, outfile='temp3', calc= " 6.112 * numpy.exp( ( 17.67 * A) / (A + 243.5) ) ", quiet= quiet ) # Correction 6.112

            #(b) vapour pressure
            # "e_${i} = (GLDAS_NOAH025_3H_20210524_${i}00_Qair * GLDAS_NOAH025_3H_20210524_${i}00_Psurf_mb) / (0.378 * GLDAS_NOAH025_3H_20210524_${i}00_Qair + 0.622)"
            e = Calc(A = Qair_file, B = Psurf_mb, outfile='temp4', calc= "(A * B) / (0.378 * A + 0.622)", quiet= quiet ) 

            #(c) Relative humidity
            # Rh1 = (e_${i} / es_${i}) * 100"
            Rh1 = Calc( A = e, B = es, outfile= 'temp5', calc= "(A / B) * 100", quiet= quiet)

            #(d) remove Outliers
            #  Rh = float(if(GLDAS_NOAH025_3H_20210524_${i}00_Rh1 > 100, 100, if(GLDAS_NOAH025_3H_20210524_${i}00_Rh1 < 0, 0, GLDAS_NOAH025_3H_20210524_${i}00_Rh1)))"
            Rh = Calc( A= Rh1, outfile= 'temp6', calc= "numpy.where(A>100, 100, numpy.where(A<0, 0, A))", quiet= quiet )

            param_ = Rh
            Qair_file = None

        else:
            param_ = masked
        
        # Todo : save all files simialr to Rh naming convention 
        # extract and save inst measurement
        if satoverpass in file:
            
            print('--- Creating daily Instantaneous maps -----')

            # save inst files in indir --> copy them into temp dir
            # save o/w files in temp dir
            param_inst = param_
            
            if param == 'Rh':
                # creating a new name Rh
                outname = "_".join([product, spat_res, temporal, param_desc, 'crop', param_unit] )
                outname = outdir + outname + '_inst.tif'                
            else:
                # footer = '_' + param_unit + '_inst.tif'
                # outname = file.replace('.tif', footer)
                param_desc = param_desc.split('_')[0]
                outname = "_".join([product, spat_res, temporal, param_desc, 'crop', param_unit] )
                outname = outdir + outname + '_inst.tif' 

            save_geotiff(param_inst, outname, geo, proj, description = param_desc, units = param_unit)

            # copy file to temp folder
            tempname = outname.split("\\")[-1]
            tempname = tempdir + tempname
            shutil.copy(outname,tempname) # src, dest
        
        else:
            # copy o/w files in temp dir
            if param == 'Rh':

                outname = "_".join([product, spat_res, temporal, param_desc, 'crop', param_unit] )
                tempname = outname + '.tif'
            
            else:
                # ToDo ?
                footer = '_' + param_unit + '.tif'  
                outname = file.replace('.tif', footer)
                tempname = outname.split("\\")[-1]
            
            tempname = tempdir + tempname
            save_geotiff(param_, tempname, geo, proj, description = param_desc, units = param_unit)

    print('--- Creating daily averages -----')
    
    # Create average using files availble in tempdir
    # save them in outdir
    # get metada : geotranform and projection
    
    if param == 'Rh':
        # since the name has been changed therefore, using new param key
        param_key = '*Rh*.tif'

    Tout = tempdir + param_key
    daily_averages(Tout, outdir, description = param_desc+'_24', units = param_unit)

    param_ = masked = param_inst = None
    del param_, masked, param_inst

    Rh = Rh1 = e = es = ds = None
    del Rh, Rh1, e, es, ds

    temp = ['temp0', 'temp1', 'temp2', 'temp3' , 'temp4' , 'temp5' , 'temp6']
    for delfile in temp:
        if os.path.exists(delfile):
            os.remove(delfile)

'''
---------------------------------------------------
---------- Filling of Excel File ------------------
---------------------------------------------------
'''
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

'''
----------------------------------------------------------------
---------- Validation against QA4SM standards ------------------
----------------------------------------------------------------
'''

def read_crs(in_path):
    """
    Reads input tiff file and prints its crs and geotransform

    Parameters
    ----------
    in_path : str
        input tiff file path
    """
    # Open the source dataset
    src_ds = gdal.Open(in_path)

    if src_ds is None:
        print(f"Failed to open {in_path}")
    else:
        # Get the source CRS
        src_crs = src_ds.GetProjectionRef()
        src_srs = osr.SpatialReference()
        src_srs.ImportFromWkt(src_crs)

        print("Source CRS:")
        print(src_srs.ExportToPrettyWkt())

        # Get the source geotransform
        geotransform = src_ds.GetGeoTransform()

        print("Source Geotransform:")
        print(geotransform)

    # Close the source dataset
    src_ds = None

    return


def convert_crs(infile, outdir, crs = 4326, filename = None):
    """
    Converts datasource crs to desired crs

    Parameters
    ----------
    infile : str
        path to input tiff files
    outdir : str
        path to output dir
    crs : int, optional
        4326 (crs in degrees) / 32643 (crs in decimal/meters) 
    """
    # Define the target CRS (WGS84)
    target_crs = osr.SpatialReference()
    target_crs.ImportFromEPSG(crs)  # EPSG 4326 is WGS84

    # Open the source dataset
    src_ds = gdal.Open(infile)

    if src_ds is None:
        print(f"Failed to open {infile}")
        

    # Create a new dataset in WGS84 with the same dimensions
    if filename:
        file_name = filename
    else:
        file_name = infile.split('\\')[-1]
    
    print(file_name)
    target_ds = gdal.Warp(
        f"{outdir}\{file_name}",
        src_ds,
        dstSRS=target_crs.ExportToWkt(),
        format="GTiff",
    )

    # Close the datasets
    src_ds = None
    target_ds = None
    
    return

def write_netCDF(indir, outdir, version = 1):
    """
    Converts the time series rasters output from Pysebal (crs : WGS84 EPSG 4326)
    into netCDF4 format in compliance with CF-1.6 for QA4SM api validations
    https://qa4sm.eu/ui/user-data-guidelines
    
    Parameters
    ----------
    indir : str
        path to input dir where all tiff are present
    outdir : str
        path to output dir to save .nc file
    version : int, optional
        version number, by default 1
    """

    path = indir + "*.tif*"
    files = glob.glob(path)

    def extract_date_sebalOut(file_path):
        # L8_Top_soil_moisture_30m_2022_11_26_330.tif
        # Split the file name by underscores and extract the date part
        parts = file_path.split('_')
        doy = parts[-1].split(".")[0]
        day = parts[-2]
        month = parts[-3]
        year = parts[-4]
        #date_str = parts[-1].split('.')[0]  # Remove the ".tif" extension
        date = datetime.datetime(int(year), int(month), int(day))
        
        return date

    # Sort the file paths by date
    sorted_file_paths = sorted(files, key=extract_date_sebalOut)

    # Define dimensions and coordinates
    # ds = gdal.Open('sebal_sm\L8_Top_soil_moisture_30m_2022_11_26_330.tif')
    ds = gdal.Open(sorted_file_paths[0])
    a = ds.ReadAsArray()
    ny, nx = np.shape(a)
    b = ds.GetGeoTransform() #bbox, interval
    # GeoTransform : (70.99986111111112, 0.0003031501201746644, 0.0, 31.01068962796874, 0.0, -0.0003031501201746644)
    print('GeoTransform :', b)  
    x = np.arange(nx) * b[1] + b[0]
    y = np.arange(ny) * b[5] + b[3]


    # Create NetCDF file
    outfile = outdir + 'soil_moisture_v' + str(version) + '.nc'
    nco = netCDF4.Dataset(outfile, 'w')

    # Create dimensions, variables and attributes
    nco.createDimension('lon', nx)
    nco.createDimension('lat', ny)
    nco.createDimension('time', None)
    xo = nco.createVariable('lon', np.float64, ('lon',))
    xo.units = 'degrees_east'
    xo.standard_name = 'longitude'
    yo = nco.createVariable('lat', np.float64, ('lat',))
    yo.units = 'degrees_north'
    yo.standard_name = 'latitude'
    timeo = nco.createVariable('time', np.int64, ('time'))
    timeo.units = 'Days since 2000-01-01T00:00:00'
    timeo.calendar = 'standard'
    timeo.standard_name = 'time'
    smo = nco.createVariable('sm', np.float64, ('time','lat', 'lon'), zlib=True, 
                            fill_value=-9999)
    smo.units = 'cm^3/cm^3'
    smo.long_name = 'soil_moisture'
    smo.valid_range = [0, 0.99]
    smo.standard_name = 'sm'

    nco.Conventions='CF-1.6'

    # Write x, y and time values
    xo[:] = x
    yo[:] = y

    i = 0
    for file_path in sorted_file_paths:
        print(file_path)
        date = extract_date_sebalOut(file_path)
        print(date)
        dtime = netCDF4.date2num(date, timeo.units, timeo.calendar)
        timeo[i] = dtime

        sm_tif = gdal.Open(file_path)
        sm_data = sm_tif.ReadAsArray()
        # assign data to variable
        smo[i,:, :] = sm_data
        i += 1

    nco.close()

    return

def read_netCDF(infile):
    """
    A reference module to read netCDF file made using write_netCDF function

    Parameters
    ----------
    infile : str
        path to netCDF file
    """

    f = netCDF4.Dataset(infile)
    print('NetCDF file details =\n', f)
    print('----------------------------------------------------------')

    print('Avaible variables  = ', f.variables.keys())


    lat = f.variables['lat']
    lon = f.variables['lon']
    time1 = f.variables['time']
    sm = f.variables['sm']


    print('Latitude values = \n',lat[:10])
    print('Longitude values = \n', lon[:10])


    timedim = sm.dimensions[0]
    print('name of time dimesion = %s' %timedim)
    times = f.variables[timedim]
    print( 'units = %s, values = %s' % (times.units, times[:]))

    dates = netCDF4.num2date(times[:], times.units)
    print('Available dates = ', [date.strftime('%Y-%m-%d %H:%M:%S') for date in dates[:10]]) 

    print('----------------------------------------------------------')
    print('SM Details = \n')
    print(sm)

    #print(sm[5][685][1916])
    f.close()
    
    return