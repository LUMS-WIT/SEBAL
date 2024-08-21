from osgeo import gdal, osr
import os, glob
import shutil

from osgeo import gdal, osr

def reproject(infile, outdir, target_crs=4326, filename=None):
    """
    Reprojects a raster to a specified CRS without resampling (i.e., keeping the original resolution).

    Parameters
    ----------
    infile : str
        Path to the input TIFF file.
    outdir : str
        Path to the output directory.
    target_crs : int, optional
        EPSG code of the desired CRS (default is 4326).
    filename : str, optional
        Optional output filename.
    """
    # Define the target CRS
    target_crs_ref = osr.SpatialReference()
    target_crs_ref.ImportFromEPSG(target_crs)  # Default is EPSG:4326 (WGS84)

    # Open the source dataset
    src_ds = gdal.Open(infile)
    if src_ds is None:
        raise ValueError(f"Failed to open {infile}")

    # Determine output filename
    if filename:
        file_name = filename
    else:
        file_name = infile.split('\\')[-1]

    # Reproject without resampling (keep original resolution)
    target_ds = gdal.Warp(
        f"{outdir}\\{file_name}",
        src_ds,
        dstSRS=target_crs_ref.ExportToWkt(),
        format="GTiff"
    )
    
    if target_ds is None:
        raise RuntimeError(f"Failed to create output dataset {file_name}")

    # Close datasets
    src_ds = None
    target_ds = None
    print(f"Successfully reprojected {file_name} to CRS {target_crs}")

    return


def reproject_to_utm(infile, outdir, filename=None):
    """
    Reprojects the input raster to the appropriate UTM zone.

    Parameters
    ----------
    infile : str
        Path to the input raster file.
    outdir : str
        Path to save the reprojected raster file.
    filename : str, optional
        Optional output filename.

    Returns
    -------
    str
        Path to the reprojected raster file.
    """
    # Open the source dataset
    src_ds = gdal.Open(infile)
    if src_ds is None:
        raise ValueError(f"Failed to open {infile}")

    # Get the geographic CRS of the input raster
    src_srs = osr.SpatialReference()
    src_srs.ImportFromWkt(src_ds.GetProjection())

    # Determine the UTM zone from the raster's longitude
    geotransform = src_ds.GetGeoTransform()
    lon = geotransform[0]  # top-left corner longitude
    lat = geotransform[3]  # top-left corner latitude

    # Calculate UTM zone (valid zones are 1 to 60)
    utm_zone = int((lon + 180) / 6) + 1
    is_northern = lat >= 0

    # Validate UTM zone
    if utm_zone < 1 or utm_zone > 60:
        raise ValueError(f"Invalid UTM zone calculated: {utm_zone}")

    # Define the UTM CRS
    tgt_srs = osr.SpatialReference()
    tgt_srs.SetUTM(utm_zone, is_northern)
    tgt_srs.SetWellKnownGeogCS("WGS84")

    # Determine output filename
    if filename:
        file_name = filename
    else:
        file_name = infile.split('\\')[-1]

    # Reproject to UTM
    target_ds = gdal.Warp(
        f"{outdir}\\{file_name}",
        src_ds,
        dstSRS=tgt_srs.ExportToWkt(),
        format="GTiff"
    )
    
    if target_ds is None:
        raise RuntimeError(f"Failed to create output dataset {file_name}")

    # Close datasets
    src_ds = None
    target_ds = None
    print(f"Successfully reprojected {file_name} to UTM zone {utm_zone}")

    return f"{outdir}\\{file_name}"

def resample(infile, outdir, target_resolution=60, filename=None):
    """
    Resamples the input raster to a new spatial resolution.

    Parameters
    ----------
    infile : str
        Path to the input raster file.
    outdir : str
        Path to save the resampled raster file.
    target_resolution : float, optional
        The desired resolution (e.g., 60 for 60m x 60m).
    filename : str, optional
        Optional output filename.
    """
    # Open the source dataset
    src_ds = gdal.Open(infile)
    if src_ds is None:
        raise ValueError(f"Failed to open {infile}")

    # Get the geotransform of the source dataset
    geotransform = src_ds.GetGeoTransform()
    x_res = geotransform[1]
    y_res = geotransform[5]
    print(f"Original resolution: x_res={x_res}, y_res={y_res}")

    # Calculate the new pixel size (target resolution)
    new_x_res = target_resolution
    new_y_res = -target_resolution  # Negative for north-up images

    # Determine output filename
    if filename:
        file_name = filename
    else:
        file_name = infile.split('\\')[-1]
        file_name = file_name.replace("30m", f"{target_resolution}m")

    # Perform resampling
    target_ds = gdal.Warp(
        f"{outdir}\\{file_name}",
        src_ds,
        xRes=new_x_res, 
        yRes=new_y_res, 
        resampleAlg='cubicspline',
        format="GTiff"
    )
    
    if target_ds is None:
        raise RuntimeError(f"Failed to create output dataset {file_name}")

    # Close datasets
    src_ds = None
    target_ds = None
    print(f"Successfully resampled {file_name} to {target_resolution}m resolution")

    return f"{outdir}\\{file_name}"

def resampling(indir, outdir, target_resolution=60, pattern= 'Top_soil_moisture'):

    path = indir + "**/*.tif"
    #Use glob to find all TIFF files in subdirectories
    files = glob.glob(path, recursive=True)

    if target_resolution != 30:

        tempdir = outdir + "temp"	    
        if not os.path.isdir(tempdir):
            os.makedirs(tempdir)

        # Filter the list to include only files with "Top_soil_moisture" in their name
        for filename in files:
            if filename.endswith(".tif") and pattern in filename:         
                resample(filename, tempdir, target_resolution, filename=None)
            
        path = tempdir + "**/*.tif"
        #Use glob to find all TIFF files in subdirectories
        files = glob.glob(path, recursive=True)

        for filename in files:
            if filename.endswith(".tif") and pattern in filename:
                reproject(filename, outdir) 
    
        print('-------- Removing Temp Files -----------') 
        shutil.rmtree(tempdir)    
    else:
        # Filter the list to include only files with "Top_soil_moisture" in their name
        for filename in files:
            if filename.endswith(".tif") and pattern in filename:             
                reproject(filename, outdir)
