# SEBAL Implementation and Guide for WIT

## Project Overview

This repository contains the guide and code for (py)SEBAL implementation, validation and results display.

### Goals
The primary goal of this project was initially to execute pysebal. For this purpose additional codes to complete the execution requirements was implemented in python (PySEBAL_code) folder. The code now serve as a testbed for all subsequent research utilizing pySEBAL. The repository will host these research work till such individual works are mature to develop their repositories. Current research implementations include:
- Validation of sebal over Indus Basin / LBDC : awaiting closure
- SWF experiment : under progress

> [!NOTE]
> Please refer to PySEBAL documentation before proceeding further. The documentation is available at this [link](https://pysebal-doc.readthedocs.io/en/version3.7.3/index.html).

## Installation and Setup
To run the models and scripts in this repository, ensure your system meets the following requirements:

### Prerequisites
- Python 3.8 or higher

1. **Clone the Repository**
   ```bash
   git clone https://github.com/LUMS-WIT/SEBAL.git
   cd SEBAL

2. **Install Dependencies using conda**
   ```bash
   # CPU only
   conda env create -f requirements_cpu.yml
   conda activate sebal

3. **Test Run PySEBAL**

   Once all the requirements have been satisfied, we can run PySEBAL code using the test data. The main code file is [Run_py3.py](PySEBAL_dev/SEBAL/Run_py3.py) and test data is located in [test_data](PySEBAL_dev/test_data) folder. If you cloned the repository in *D:* drive then it should be *D:\SEBAL\PySEBAL_dev\test_data*. Now Open *Run_py3.py* in your code editor and ensure following:
   
   ```bash
   ##### USER INPUTS

   ##### For Linux SET THE PATH TO INPUT EXCEL SHEET #####
   #inputExcel = r"/mnt/d/PySEBAL_dev/test_data/InputEXCEL_v3_3_7_LIN.xlsx"
   ##### For Windows SET THE PATH TO INPUT EXCEL SHEET #####
   inputExcel = r"D:\SEBAL\PySEBAL_dev/test_data/InputEXCEL_v3_3_7_WIN.xlsx"
   st = 2 # starting row number
   en = 2 # ending row number
   ```  
   Once done execute the PySEBAL code:
   ```bash
   # Ensure the conda environment i.e. *sebal* is activated
   python Run_py3.py
   ```  

   If successfully executed. There would be an *output* folder inside *D:\SEBAL\PySEBAL_dev\test_data*.

> [!WARNING]
> If PySEBAL_dev is not in *D:* drive, you need to update the paths in excel sheet for the dataset location.

4. **Download Landsat Data**
   - The Landsat 8/9 data can be downloaded freely from [EarthExplorer](https://earthexplorer.usgs.gov/) for which you need to register.
   - Download **Landsat Collection 2 Level-1** data for the given dates and region of interest (ROI).
   - Place the downloaded dataset in *SEBAL\datasets\landsat\\* folder
> [!NOTE]
> Please ensure (visually) that the ROI is not completely covered by clouds. You can set Cloud Cover option to 80% in the search criteria.
> For downloading mulitple images, It is recommended to use Bulk Download option. 

5. **Download DEM**
   - A DEM of ROI is required. There are multiple option to download DEM including
      - SRTM [link](https://earthexplorer.usgs.gov/)
      - Copernicus GLO-30 
      - JAXA-ALOS AW3D30 [link](https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d30/aw3d30_e.htm)
   - Place the downloaded dataset in *SEBAL\datasets\dem\\* folder

6. **Download Soil Dataset**
   - The global maps for soil hydrolic properties at 250 m resolution can be downloaded freely from [HiHydrosoil](https://www.futurewater.eu/projects/hihydrosoil//).
   - The required raster files are following:
      - WCpF2_M_250m_SUBSOIL
      - WCpF2_M_250m_TOPSOIL
      - WCpF4.2_M_250m_SUBSOIL
      - WCpF4.2_M_250m_TOPSOIL
      - WCres_M_250m_SUBSOIL
      - WCres_M_250m_TOPSOIL
      - WCsat_M_250m_SUBSOIL
      - WCsat_M_250m_TOPSOIL
   - Place these rasters in *SEBAL\datasets\soil\\* folder

7. **Shapefile for ROI**
   - Shapefile for ROI needs to be developed in QGIS covering the desired extents.
   - The shapefile needs to be overlapping with DEM, soil data and landsat data. 


## Usage

The following steps would be executed to run pySEBAL model. 

1. **Processing Landsat Data**

   Set the path of landsat folder in [config.py](PySEBAL_code/config.py) python file.
   ```bash
   landsat_swf = 'D:\SEBAL\datasets\landsat\swf\\'
   LANDSAT_INDIR = landsat_swf
   ``` 
   Execute [landsat_processing.py](PySEBAL_code/landsat_processing.py) script.
   ```bash
   python landsat_processing.py
   ```
2. **Downloading Meteorological Data**

   The meteorological data for ROI needs to be available for pySEBAL code. This includes the instantaneous and 24 hours average *Temperature*, *Relative Humidity*, *Windspeed* and *Downwards shortwave radiation*. The same can be downloaded form GLDAS NOAH2.5 3H[NASA Server](https://hydro1.gesdisc.eosdis.nasa.gov/data/GLDAS/GLDAS_NOAH025_3H.2.1/) automatically through python script. Follow [these](https://disc.gsfc.nasa.gov/information/documents?title=Data%20Access) steps before executing the script.

   - create an account using these [steps](https://wiki.earthdata.nasa.gov/display/EL/How+To+Register+For+an+EarthData+Login+Profile)
   - authorize NASA GESDISC DATA ARCHIVE via your account using these [steps](https://disc.gsfc.nasa.gov/earthdata-login)
   - verify  NASA GESDISC DATA ARCHIVE is in Accepted EULA
   - create the pre-requiste file for authentications using these [steps](https://disc.gsfc.nasa.gov/information/howto?title=How%20to%20Generate%20Earthdata%20Prerequisite%20Files)

   Set the values for global variables in *Config.py* python file.
   ```bash
   BULK_DOWNLOAD = True
   METEO_INDIR = 'D:\SEBAL\datasets\meteo\swf\\'
   ```
   Execute [gldas_download.py](PySEBAL_code/gldas_download.py) Script.
   ```bash
   python gldas_download.py
   ```

   Incase of requirement for downloading specific dated meteo data e.g. failed validation. Make following changes in the *config.py* file to include the desired dates. Followed by re-running the script. 
   ```bash
   BULK_DOWNLOAD = False
   METEO_INDIR = 'D:\SEBAL\datasets\meteo\swf\\'
   MISSING_DATES = ['20230508', '20230516', '20230524']
   ```
> [!WARNING]
> You need to place .netrc with above created user login details, .urs_cookies (not compulsory) file in home dir and .dodrc (not compulsory) in project dir.

> [!Note]
> You (might) need to be signed in at Earthdata service at [link](https://urs.earthdata.nasa.gov/) before executing the code below.

3. **Processing of DEM**
   DEM for the ROI would be required in the subsequent steps. It is recommended that the same processing should be carried out in QGIS. In case of manual processing i.e. extracting the ROI's DEM from the downloaded DEM raster, we can use *crop_region_basic*, *crop_region* or *crop_region_subpixel* available in [utils.py](PySEBAL_code/utils.py) python script.

4. **Processsing GLDAS Meteorological Data**

   The purpose of pre-processing is to convert the downloaded meteorological data from GLDAS into desired units and parameters as mentioned in PySEBAL documentation. 

   Set the values for global variables in *Config.py* python file.

   ```bash
   LANDSAT_OVERPASS = "0600"
   BULK_PROCESSING = True
   ```

   Execute [gldas_processing.py](PySEBAL_code/gldas_download.py) Script.
   ```bash
   python gldas_processing.py
   ```

   Incase of requirement for processing specific dated meteo data, set *BULK_PROCESSING* parameter to *False* and enter the desired dates in *MISSING_DATES* parameter from *Config.py* file
> [!NOTE]
> The over pass time for landsat 8/9 over Pakistan is around 0545 hrs (GMT) with corresponding meteo data of time 0600. You can verify the satellite overpass dates from [link](https://landsat.usgs.gov/landsat_acq) and overpass time form [link](https://www.ssec.wisc.edu/datacenter/polar_orbit_tracks/ )

5. **Processsing of HiHydroSoil Data**

   In order to extract the desired parameters from the raster files, first set the values for global variables in *Config.py* python file followed by execution of [soil_processing.py](PySEBAL_code/soil_processing.py) as following:

   ```bash
   SOIL_INDIR = "D:\SEBAL\datasets\soil\HiHydroSoil_250m\Top_Subsoil\\"
   SOIL_OUTDIR = "D:\SEBAL\datasets\soil\\"
   ```

   ```bash
   python soil_processing.py
   ```
> [!NOTE]
> It is recommended that you run the soil processing script for complete region e.g. Pakistan, instead for running it repeatedly for every ROI.

6. **Generating Excel File (Additional)**

   The final step before running the PySEBAL model over ROI is filling all the above generated data details / paths in the *InputExcel* file available in [docs](PySEBAL_dev\docs) folder. The same file can be filled manually. In case exhaustive list of inputs, a helper excel file can be generated to expedite the same.   

   set the values for global variables in *Config.py* python file followed by execution of [excel_processing.py](PySEBAL_code/excel_processing.py) as following:

   ```bash
   DOCS_INDIR = "D:\SEBAL\PySEBAL_dev\docs\\"
   SEBAL_OUTDIR = "D:\SEBAL\datasets\swf\\"
   ```

   ```bash
   python excel_processing.py
   ```
7. **Run PySEBAL**

   Once the *InputExcel* file is filled. We can run PySEBAL code by executing *Run_py3.py* script. We need to specify the path to *InputExcel* , starting and ending rows of excel file *st*,*en* (excluding the header row) in the same manner of done previously.  

   ```bash
   # Ensure the conda environment i.e. *sebal* is activated
   python Run_py3.py
   ```  

## Contributing

todo: Guidelines for how others can contribute to the project

## Citation 

todo: guide to how to cite this work
