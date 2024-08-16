import os, shutil, glob

from utils import crop_region_basic, soil_downscaling
from config import SOIL_INDIR, SOIL_OUTDIR, SHAPEFILE

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

if __name__ == "__main__":
    
    print('---------------------------------------------')
    print('------- HiHydro Soil Data Processing --------')
    print('---------------------------------------------')
    soil_processing(SOIL_INDIR, SOIL_OUTDIR, SHAPEFILE)