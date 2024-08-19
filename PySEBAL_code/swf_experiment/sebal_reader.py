import glob, os, datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from osgeo import gdal
import osgeo.osr as osr
import numpy as np

class SebalSoilMoistureData:
    """
    Class for reading and processing raster data from a specified folder.
    Attributes:
        folder_path (str): Path to the folder containing raster files.
    """

    def __init__(self, folder_path, pattern = 'Top_soil_moisture'):
        """
        Initializes the SebalData object.
        Args:
            folder_path (str): Path to the folder containing raster files.

        Raises:
            ValueError: If the folder path is invalid or does not exist.
        """

        if not os.path.exists(folder_path):
            raise ValueError(f"Invalid folder path: {folder_path}")
        self.folder_path = folder_path
        
        self.pattern = pattern
        files = [f for f in os.listdir(self.folder_path) if f.endswith(".tif") and self.pattern in f]
        # taking a raster file for extent coverage check
        if len(files)>0:
            file = files[0]
            self.raster_file_path = os.path.join(self.folder_path, file)
        else:
            raise ValueError(f"Folder contains no raster files")   
        
        self.raster_dates = None 
        self.raster_values= None

    def get_raster_extent(self, file_path):
        """
        Returns the spatial extent of the given raster file.
        """
        dataset = gdal.Open(file_path)
        if not dataset:
            raise ValueError("Could not open the raster file.")

        # Get raster geometry info
        transform = dataset.GetGeoTransform()
        x_min = transform[0]
        y_max = transform[3]
        x_max = x_min + transform[1] * dataset.RasterXSize
        y_min = y_max + transform[5] * dataset.RasterYSize

        return (x_min, x_max, y_min, y_max)
    
    def is_within_extent(self, lat, lon, extent):
        """
        Check if the given latitude and longitude are within the raster extent.
        """
        x_min, x_max, y_min, y_max = extent
        return x_min <= lon <= x_max and y_min <= lat <= y_max
    
    def read_raster_value(self, file_path=None, lat=None, lon=None):
        """
        Reads the value at a specific latitude and longitude from a single raster file
        matching the given pattern within the folder.

        Args:
            lat (float): Latitude coordinate.
            lon (float): Longitude coordinate.
            pattern (str, optional): Pattern to match filenames (default: "Top_soil_moisture").

        Returns:
            float: Raster value at the specified coordinates, or np.nan if missing or out of bounds
        """
            # Open the TIF file
        dataset = gdal.Open(file_path)
        if not dataset:
            raise ValueError("File could not be opened.")
        
        # Fetch the geographic coordinate system and projection from the dataset
        old_cs = osr.SpatialReference()
        old_cs.ImportFromWkt(dataset.GetProjectionRef())
        
        # Create a new geographic coordinate system (WGS84)
        wgs84 = osr.SpatialReference()
        wgs84.ImportFromEPSG(4326)
        
        # Create a coordinate transformation from WGS84 to the dataset's projection
        transform = osr.CoordinateTransformation(wgs84, old_cs)
        
        # Transform the lat, lon coordinates to the dataset's projection
        x, y, z = transform.TransformPoint(lon, lat)
        
        # Get the affine transformation coefficients
        gt = dataset.GetGeoTransform()
        
        # Convert from geographic coordinates to raster pixel coordinates
        pixel_x = int((x - gt[0]) / gt[1])
        pixel_y = int((y - gt[3]) / gt[5])

        # Check if the pixel coordinates are within the raster bounds
        if (pixel_x < 0 or pixel_x >= dataset.RasterXSize or
            pixel_y < 0 or pixel_y >= dataset.RasterYSize):
            print(f"Requested pixel is out of bounds: ({pixel_x}, {pixel_y})")

        # Read the data value at the raster pixel coordinates
        band = dataset.GetRasterBand(1)
        value = band.ReadAsArray(pixel_x, pixel_y, 1, 1)
        
        # Close the dataset
        dataset = None
        
        # Handle missing data
        if value is None or np.isnan(value).all():
            return np.nan
        else:
            return value[0, 0]

    def read_data(self, lat=None, lon=None):
        """
        Reads values from all raster files matching the given pattern
        within the folder, at the specified latitude and longitude.

        Args:
            lat (float): Latitude coordinate.
            lon (float): Longitude coordinate.

        Returns:
            tuple(list, list) 
                - List of datetime objects (dates)
                - List of corresponding raster values (sorted by date)
        """
        values = []
        dates = []

        # Walk through the directory, including subdirectories
        for root, dirs, files in os.walk(self.folder_path):    
            # Iterate through all files in the folder
            for filename in files:
                if filename.endswith(".tif") and self.pattern in filename:
                    # Construct the full file path
                    file_path = os.path.join(root, filename)
                    # Extract date from filename
                    parts = filename.split('_')
                    date_str = f"{parts[-4]}_{parts[-3]}_{parts[-2]}"  # Assumes date is in the format {year}_{month}_{day}
                    date = datetime.datetime.strptime(date_str, '%Y_%m_%d')
                    # Read the raster value
                    value = self.read_raster_value(file_path, lat, lon)
                    values.append(value)
                    dates.append(date)
        
        # Combine dates and values into a list of tuples and sort by date
        _values = list(zip(dates, values))
        _values.sort(key=lambda x: x[0])  # Sorting by dates
        
        # Unpack dates and values from the sorted list
        raster_dates, raster_values = zip(*_values)

        return raster_dates, raster_values
    
    def get_data(self, lat, lon):
        """
        return the date and value data for the user
        """
        # TODO: needs to optimize, opening and closing raster twice
        extent = self.get_raster_extent(self.raster_file_path)
        if self.is_within_extent(lat, lon, extent):
            raster_dates, raster_values = self.read_data(lat, lon)       
            return raster_dates, raster_values
        else:
            return None, None
           
    def plot_data(self):
        
        if self.raster_dates:
            # Plotting the results of raster
            plt.figure(figsize=(10, 5))
            #plt.plot(dates, values, 'o')
            plt.plot(self.raster_dates, self.raster_values, marker='x', linestyle='--', color='r', label='Sebal Soil Moisture')
            plt.title(f'{self.pattern} Over Time')
            plt.xlabel('Date')
            plt.ylabel('Soil Moisture Value (m3/m3)')

            # Configure date format on x-axis
            # Set the x-ticks to match the dates of the data points
            plt.gca().set_xticks(self.raster_dates)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.gcf().autofmt_xdate(rotation=90)  # Auto formats the x-axis labels to fit them in the plot area
            plt.gca().tick_params(axis='x', labelsize=8)  # Setting the font size to 8

            plt.legend()
            plt.tight_layout()
            plt.show()
        else:
            print('Please run read_data method first')


