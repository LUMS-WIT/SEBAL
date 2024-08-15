from config import LANDSAT_INDIR
from utils import untar_bulk, validate_landsat, remove_tar

def unzip_landsat():
    print('-----------------------------------------')
    print('------- Unziping Landsat8/9 Data --------')
    print('-----------------------------------------')    

    untar_bulk(LANDSAT_INDIR)

def validate():
    print('\n-----------------------------------------')
    print('------ Validating Landsat8/9 Data -------')
    print('-----------------------------------------')

    status = validate_landsat(LANDSAT_INDIR, count=24, size= 1010)
    return status

def removing():
    print('\n-----------------------------------------')
    print('--------- Removing tar Files ------------')
    print('-----------------------------------------')
    remove_tar(LANDSAT_INDIR)

if __name__ == "__main__":
    
    unzip_landsat()
    status = validate()
    if status == 'sat':
        removing()
    else:
        print('\nWARNING!!! Some Files Missing in tar files')