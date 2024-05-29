# pip install landsatxplore

from landsatxplore.api import API
import getpass
from landsatxplore.util import landsat_dataset
from landsatxplore.earthexplorer import EarthExplorer
import os

outdir = "F:\SEBAL\datasets\landsat\LBDC_exp\\new\\"

mode = 'manual' 

def get_landsat(outdir, lat=30.134628, lon = 71.786106, 
                start_date = '2020-09-15', end_date = '2021-09-14' , 
                mode = 'auto', scenes_man = ['LC08_L1TP_149039_20200926_20201005_02_T1', 'LC08_L1TP_150039_20200917_20201005_02_T1']):
    
    # Your USGS  credentials
    username = "hamza.rafique@lums.edu.pk"
    # password = getpass.getpass('Earthdata Password:')
    password = "Password952#"
    # token = "0r5zjwErr_qkhMOKzVoGrxm@lwdmPFrR_iYpf5YnpYwPfIK9sGgflwplu!GTfJ7q"
    # Initialize a new API instance
    api = API(username, password)

    # Perform a request
    response = api.request(endpoint="dataset-catalogs")
    print(response)

    # Search for Landsat 8 scenes
    # Landsat 8 Collection 2 Level 1 : landsat_ot_c2_l1
    # Landsat 9 Collection 2 Level 1 : landsat_ot_c2_l1
    # "landsat_ot_c2_l1": ["632211e26883b1f7", "5e81f14ff4f9941c", "5e81f14f92acf9ef"],
    # nawaz agri farm = 30.134628, 71.786106
    # shameer = 30.658148, 73.400117

    scenes = api.search(
        dataset='landsat_ot_c2_l1',
        latitude=lat,
        longitude=lon,
        start_date=start_date,
        end_date= end_date,
        max_cloud_cover=100
    )

    print(f"{len(scenes)} scenes found.")

    print("Product ID", "\t\tAcquisition Date", "\tCloud Cover", "\tOverpass Time")
    
    
    if mode == 'auto':

        for scene in scenes:
            
            prod_id = scene['landsat_product_id']
            acq_date = scene['acquisition_date'].strftime('%Y-%m-%d')
            cloud_cover = scene['land_cloud_cover']
            acq_date_time = scene['start_time'].strftime("%H:%M:%S")

            print(prod_id, '\t', acq_date, '\t', cloud_cover, '\t', acq_date_time)


        # Define the filename for the text file where you want to save the information
        filename = outdir + "scene_information.txt"

        # Open the file in write mode ('w') and ensure it gets closed properly using a context manager (with statement)
        with open(filename, 'a') as file:
            # Write header to the file
            file.write("Product ID\tAcquisition Date\tCloud Cover\tOverpass Time\n")
            
            # Iterate through the scenes and write each scene's information to the file
            for scene in scenes:
                prod_id = scene['landsat_product_id']
                acq_date = scene['acquisition_date'].strftime('%Y-%m-%d')
                cloud_cover = scene['land_cloud_cover']
                acq_time = scene['start_time'].strftime("%H:%M:%S")
                
                # Write the information for the current scene to the file
                file.write(f"{prod_id}\t{acq_date}\t{cloud_cover}\t{acq_time}\n")

        print(f"Scene information saved to {filename}")

        # Initialize the API
        ee = EarthExplorer(username, password)

        for i in range(len(scenes)):
            # Download the scene
            ID = scenes[i]['landsat_product_id']
            print("Downloading :", ID)
            try: 
                ee.download(ID, output_dir=outdir)
                print('{} successful'.format(ID))
                
            # Additional error handling
            except:
                if os.path.isfile('./data/{}.tar'.format(ID)):
                    print('{} error but file exists'.format(ID))
                else:
                    print('{} error'.format(ID))

        ee.logout()


    else:

        scenes = scenes_man
        
        ee = EarthExplorer(username, password)

        for i in range(len(scenes)):
            # Download the scene
            ID = scenes[i]
            print("Downloading :", ID)
            try: 
                ee.download(ID, output_dir=outdir)
                print('{} successful'.format(ID))
                
            # Additional error handling
            except:
                if os.path.isfile('./data/{}.tar'.format(ID)):
                    print('{} error but file exists'.format(ID))
                else:
                    print('{} error'.format(ID))
        exit()
    
    return

nawaz = [30.134628, 71.786106]
shameer = [30.658148, 73.400117]
farms = [nawaz, shameer]

for farm in farms:
    lat , lon = farm
    get_landsat(outdir,lat, lon, mode='manual')

