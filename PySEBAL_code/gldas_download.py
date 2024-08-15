import datetime
import os
from config import BULK_DOWNLOAD, METEO_INDIR, MISSING_DATES, LANDSAT_INDIR
from utils import download_gldas, validate_gldas

def GLDAS():
    
    print('----------------------------------------')
    print('------- Downloading GLDAS Meteo --------')
    print('----------------------------------------')
    
    if not os.path.exists(METEO_INDIR):
        os.makedirs(METEO_INDIR)
        print(f"Directory created: {METEO_INDIR}")

    if BULK_DOWNLOAD:
        print("\nBulk Downloading GLDAS NOAH Meterological data")
        files = os.listdir(LANDSAT_INDIR)

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

            outdir = METEO_INDIR + "{}\\".format(date)
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

        for date in MISSING_DATES:

            year = int(date[:4])
            month = int(date[4:6])
            day = int(date[-2:])

            input_date = datetime.date(year, month, day)

        
            outdir = METEO_INDIR + "{}\\".format(date)

            print(outdir)
            try :
                download_gldas(input_date, outdir)
            except:
                print(f"Failed to download {date}")

        print('\nDownload Completed .........')

def validate():

    print('----------------------------------------')
    print('------- Validating GLDAS Meteo ---------')
    print('----------------------------------------')

    validate_gldas(METEO_INDIR, count=8, size= 145)


if __name__ == "__main__":
    GLDAS()
    validate()
