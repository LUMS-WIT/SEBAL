import sys
sys.path.append('F:\SEBAL\PySEBAL_code')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from osgeo import gdal, ogr
import osgeo.osr as osr
import csv
import os
import re
import numpy as np
from utils import *

row_path = '149039'
save_plot = True

raster_file_path = r'F:\SEBAL\datasets\validation\LBDC_validations\149039\L9_Top_soil_moisture_30m_2023_06_23_174.tif'
# raster_file_path = r'F:\SEBAL\datasets\validation\LBDC_validations\150039\L9_Top_soil_moisture_30m_2023_09_18_261.tif'
shapefile_path = r'F:\SEBAL\datasets\validation\LBDC_validations\shapefiles\149039_out_extent_1.shp'


wit_sms_path = 'F:\SEBAL\datasets\WIT_SM\SMS_final_v2'
raster_folder_path = r'F:/SEBAL/datasets/validation/LBDC_validations/149039/'

temporal_coverage = 0   # days for temporal matching
metadata_file_path = r'F:\SEBAL\datasets\validation\LBDC_validations\metadata_150039.xlsx'
validation_folder = r'F:\SEBAL\datasets\validation\LBDC_validations\validation_points\149039'
images_folder = r'F:\SEBAL\datasets\validation\LBDC_validations\figs\149039'
pattern = "Top_soil_moisture"


# ----------------------------------------------------------------------
# Plotting Logic
# 1. Read wit soil moisture data
# 2. get the subset of overlapping points from wit sms data
# 3. for each lat/lon from subset, get the soil moisture sebal raster data and wit_sms data
# 4. plot/save the two data points
# ----------------------------------------------------------------------

class SoilMoistureData:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.data = []
        self.metadata = []
        self.total_files = 0

    def read_data(self):
        files = [f for f in os.listdir(self.folder_path) if f.endswith(".csv") and 'witsms_gpi' in f]
        self.total_files = len(files)
        print(f"Reading {self.total_files} files...")  # Debugging output

        for file in files:
            file_path = os.path.join(self.folder_path, file)
            gpi = re.search('gpi=(\d+)', file).group(1)
            lat = re.search('lat=([-+]?[0-9]*\.?[0-9]+)', file).group(1)
            lon = re.search('lon=([-+]?[0-9]*\.?[0-9]+)', file).group(1)
            timestamps = []
            soil_moistures = []

            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                for col in reader:
                    if col[1]:  # Ensuring the soil moisture value is not empty
                        try:
                            timestamp = datetime.datetime.strptime(col[0], "%Y-%m-%d %H:%M:%S")
                            soil_moisture = float(col[1]) / 100 # coverting to 0-1 scale
                            timestamps.append(timestamp)
                            soil_moistures.append(soil_moisture)
                        except ValueError as e:
                            print(f"Error parsing line in {file}: {e}")  # Error output

            # Ensure data is not empty before appending
            if timestamps:
                self.data.append((timestamps, soil_moistures))  # Storing timestamps and soil moisture values
                start_date = min(timestamps).strftime("%Y-%m-%d")
                end_date = max(timestamps).strftime("%Y-%m-%d")
                count_soil_moisture = len(soil_moistures)
                self.metadata.append({
                    'gpi': gpi,
                    'latitude': lat,
                    'longitude': lon,
                    'start_date': start_date,
                    'end_date': end_date,
                    'count': count_soil_moisture, 
                    'overlaps': 0
                })

    def print_metadata(self):
        headers = ['gpi', 'latitude', 'longitude', 'start_date', 'end_date', 'count', 'overlaps']
        print(",".join(headers))
        for entry in self.metadata:
            row = [entry[header] for header in headers]
            print(",".join(map(str, row)))
    
    def get_metadata(self):
        """
        Returns the metadata as a list of dictionaries.
        Each dictionary contains the metadata of one dataset.
        """
        return self.metadata

    def save_metadata_to_csv(self, filename='metadata.csv'):
        headers = ['gpi', 'latitude', 'longitude', 'start_date', 'end_date', 'count', 'overlaps']
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for entry in self.metadata:
                writer.writerow(entry)
    
    def get_lat_lon_by_gpi(self, gpi):
        for item in self.metadata:
            if item['gpi'] == gpi:
                return (item['latitude'], item['longitude'])
        return None  # Return None if no matching GPI is found

    # def get_soil_moisture_by_location(self, lat=None, lon=None, gpi=None):
    #     if gpi:  # Get data by GPI if provided
    #         for (timestamps, soil_moistures), meta in zip(self.data, self.metadata):
    #             if meta['gpi'] == gpi:
    #                 return list(zip(timestamps, soil_moistures))
    #     elif lat and lon:  # Get data by latitude and longitude
    #         for (timestamps, soil_moistures), meta in zip(self.data, self.metadata):
    #             if meta['latitude'] == str(lat) and meta['longitude'] == str(lon):
    #                 return list(zip(timestamps, soil_moistures))
    #     return None  # Return None if no data is found    

    def get_soil_moisture_by_location(self, lat=None, lon=None, gpi=None):
        if gpi:  # Get data by GPI if provided
            for (timestamps, soil_moistures), meta in zip(self.data, self.metadata):
                if meta['gpi'] == gpi:
                    return timestamps, soil_moistures
        elif lat and lon:  # Get data by latitude and longitude
            for (timestamps, soil_moistures), meta in zip(self.data, self.metadata):
                if meta['latitude'] == str(lat) and meta['longitude'] == str(lon):
                    return timestamps, soil_moistures
        return None, None  # Return None if no data is found

    def plot_data_gpi(self, gpi=None):
        # Plot data only for the specified GPI
        if gpi:
            found = False
            for (timestamps, soil_moistures), meta in zip(self.data, self.metadata):
                if meta['gpi'] == gpi:
                    plt.figure(figsize=(10, 6))
                    plt.plot(timestamps, soil_moistures, label=f"GPI {meta['gpi']} at ({meta['latitude']}, {meta['longitude']})")
                    plt.title(f"Soil Moisture Time Series for GPI {meta['gpi']} - Values: {meta['count']}")
                    plt.xlabel('Date')
                    plt.ylabel('Soil Moisture')
                    plt.legend()
                    plt.show()
                    found = True
                    break  # Stop after plotting the specified GPI
            if not found:
                raise ValueError(f'GPI {gpi} not available in metadata')
        else:
            # If no GPI is specified, plot all data
            for (timestamps, soil_moistures), meta in zip(self.data, self.metadata):
                plt.figure(figsize=(10, 6))
                plt.plot(timestamps, soil_moistures, label=f"GPI {meta['gpi']} at ({meta['latitude']}, {meta['longitude']})")
                plt.title(f"Soil Moisture Time Series for GPI {meta['gpi']} - Values: {meta['count']}")
                plt.xlabel('Date')
                plt.ylabel('Soil Moisture')
                plt.legend()
                plt.show()

# Example usage:
# # Example usage:
soil_moisture_data = SoilMoistureData(wit_sms_path)
soil_moisture_data.read_data()
# soil_moisture_data.print_metadata()  # Print metadata in CSV format
# #soil_moisture_data.save_metadata_to_csv()  # Save metadata to a CSV file


# # Plotting data for a specific GPI
# soil_moisture_data.plot_data('2021069')
metadata = soil_moisture_data.get_metadata()                                            # Plotting step 1

# for data in metadata:
#     lat, lon = soil_moisture_data.get_lat_lon_by_gpi(data['gpi'])  # Replace '123456' with actual GPI
#     print(f"Latitude, Longitude: {float(lat), float(lon)}")


# ---------------------------------------------------------------------------------------------------------


def get_raster_extent(file_path):
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


def get_shapefile_extent(file_path):
    """
    Returns the spatial extent of the given shapefile.
    """
    # Open the shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataset = driver.Open(file_path)
    if not dataset:
        raise ValueError("Could not open the shapefile.")

    # Get the first layer of the shapefile
    layer = dataset.GetLayer(0)
    extent = layer.GetExtent()

    # Extent returned as (x_min, x_max, y_min, y_max)
    return extent

def is_within_extent(lat, lon, extent):
    """
    Check if the given latitude and longitude are within the raster extent.
    """
    x_min, x_max, y_min, y_max = extent
    return x_min <= lon <= x_max and y_min <= lat <= y_max

def find_data_within_extent(metadata, raster_file_path):
    """
    Filters metadata to find entries within the extent of the specified raster file.
    """
    extent = get_raster_extent(raster_file_path)
    # extent = get_shapefile_extent(shapefile_path)
    within_extent = []
    for entry in metadata:
        lat = float(entry['latitude'])
        lon = float(entry['longitude'])
        if is_within_extent(lat, lon, extent):
            within_extent.append(entry)
    
    return within_extent

# Example usage:
# metadata = [
#     {'gpi': '2021001', 'latitude': '30.3283', 'longitude': '73.1475', 'count': 50, 'start_date': '2021-12-23', 'end_date': '2022-02-15'},
#     {'gpi': '2021002', 'latitude': '30.3286755', 'longitude': '73.1471864', 'count': 50, 'start_date': '2021-12-23', 'end_date': '2022-02-15'}
#     # Add more metadata entries as needed
# ]

data_within_extent = find_data_within_extent(metadata, raster_file_path)              # Plotting step 2

print(f"Data within raster extent: {len(data_within_extent)}")
for data in data_within_extent:
    print(data)


# ---------------------------------------------------------------------------------------------------------

class SebalSoilMoistureData:
    """
    Class for reading and processing raster data from a specified folder.
    Attributes:
        folder_path (str): Path to the folder containing raster files.
    """

    def __init__(self, folder_path):
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
        self.raster_dates = None 
        self.raster_values= None
        self.pattern = 'Top_soil_moisture'
        
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
        self.raster_dates, self.raster_values = zip(*_values)
    
    def get_data(self):
        """
        return the date and value data for the user
        """
        if self.raster_dates:
            if self.raster_values:

                return self.raster_dates, self.raster_values
        else:
            print('Please run read_data method first')
            

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

def read_raster_value(file_path, lat, lon):
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

def read_raster_folder(folder_path, lat, lon, pattern = "Top_soil_moisture"):
    values = []
    dates = []

    # Walk through the directory, including subdirectories
    for root, dirs, files in os.walk(folder_path):    
        # Iterate through all files in the folder
        for filename in files:
            if filename.endswith(".tif") and pattern in filename:
                # Construct the full file path
                file_path = os.path.join(root, filename)
                # Extract date from filename
                parts = filename.split('_')
                date_str = f"{parts[-4]}_{parts[-3]}_{parts[-2]}"  # Assumes date is in the format {year}_{month}_{day}
                date = datetime.datetime.strptime(date_str, '%Y_%m_%d')
                # Read the raster value
                value = read_raster_value(file_path, lat, lon)
                values.append(value)
                dates.append(date)
    
    # Combine dates and values into a list of tuples and sort by date
    raster_values = list(zip(dates, values))
    raster_values.sort(key=lambda x: x[0])  # Sorting by dates
    
    # Unpack dates and values from the sorted list
    sorted_dates, sorted_values = zip(*raster_values)
    return sorted_dates, sorted_values



'''
# Example usage
#lat, lon = 30.676265,73.151078
lat, lon = float(data_within_extent[-1]['latitude']), float(data_within_extent[-1]['longitude'])              # Plotting step 3.a

csv_dates, csv_values = soil_moisture_data.get_soil_moisture_by_location(lat, lon)  # Replace '123456' with actual GPI

# latitude = 30.3283
# longitude = 73.1475
# value = read_raster_value(raster_file_path, latitude, longitude)
# print("Value at location:", value)

raster_dates, raster_values = read_raster_folder(raster_folder_path, lat, lon)                          # plotting step 3.b

#print(raster_dates, raster_values)
print('Total Count of sebal values:', len(raster_values))

nan_count = np.sum(np.isnan(raster_values))
print('Sebal Data with NaN values:', nan_count)
'''
# ---------------------------------------------------------------------------------------------------------

def temporal_matching(ref_data, test_data, search_range=0):
    """
    Finds overlapping dates by checking a range of days around each reference date to find
    the closest matching test date with a valid (non-NaN) value.
    Note that valid overlap count cannot exceed than the number of points in reference data

    Parameters:
    - ref_data: Tuple containing two lists (dates and values) for the reference dataset.
    - test_data: Tuple containing two lists (dates and values) for the test dataset.
    - search_until_range: Number of days to check around each reference date.

    Returns:
    - overlapping_ref_dates: List of reference dates that have overlaps.
    - overlapping_ref_values: List of values from the reference dataset for the overlapping dates.
    - overlapping_test_values: List of closest values from the test dataset corresponding to the reference dates.
    - valid_overlap_count: Count of valid overlapping points.
    """
    ref_dates, ref_values = ref_data
    test_dates, test_values = test_data

    # Convert datetime.datetime to datetime.date to ignore time of day
    ref_data_dict = {date.date(): value for date, value in zip(ref_dates, ref_values)}
    test_data_dict = {date.date(): value for date, value in zip(test_dates, test_values)}

    overlapping_ref_dates = []
    overlapping_ref_values = []
    overlapping_test_values = []

    for ref_date, ref_value in ref_data_dict.items():
        closest_value = None
        closest_distance = search_range + 1  # Initialize to more than the search range

        # Check dates within the range around the reference date
        for offset in range(-search_range, search_range + 1):
            test_date = ref_date + datetime.timedelta(days=offset)
            if test_date in test_data_dict and not np.isnan(test_data_dict[test_date]):
                distance = abs(offset)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_value = test_data_dict[test_date]

        # If a valid closest value is found within the range
        if closest_value is not None:
            overlapping_ref_dates.append(ref_date)
            overlapping_ref_values.append(ref_value)
            overlapping_test_values.append(closest_value)

    valid_overlap_count = len(overlapping_ref_dates)

    return overlapping_ref_dates, overlapping_ref_values, overlapping_test_values, valid_overlap_count


def save_to_plot(csv_dates, csv_values, raster_dates, raster_values, lat, lon, filename ):
    plt.figure(figsize=(12, 6))

    # Plot CSV data
    plt.plot(csv_dates, csv_values, marker='o', linestyle='-', color='b', label='WIT-SMS')

    # Plot Raster data
    plt.plot(raster_dates, raster_values, marker='x', linestyle='--', color='r', label='Sebal Soil Moisture')

    plt.title(f'Top Soil Moisture Time Series Comparison Latitude: {lat}, Longitude: {lon}')
    plt.xlabel('Date')
    plt.ylabel('Soil Moisture (m3/m3)')

    # Formatting the date on the x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()  # Auto formats the x-axis labels to fit them in the plot area

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(filename, dpi=300)  # Save the figure to file
    print(f"Plot saved as {filename}")

def save_to_excel(data, filename, headers):
    """
    Saves given data to an Excel file with specified headers.
    
    Parameters:
    - data: List of tuples/lists containing the data to save.
    - filename: String for the filename to save the Excel document.
    - headers: List of strings for column headers in the Excel file.
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    
    # Add headers to the first row
    sheet.append(headers)
    
    # Add data rows
    for row in data:
        sheet.append(row)
    
    # Save the workbook
    workbook.save(filename)
    print(f"Data saved to {filename}")

validation_metadata = []
print(f'Performing temporal matching with temporal window of {temporal_coverage} days')
for _metadata in data_within_extent:
    lat, lon = float(_metadata['latitude']), float(_metadata['longitude'])


    csv_dates, csv_values = soil_moisture_data.get_soil_moisture_by_location(lat, lon)
    raster_dates, raster_values = read_raster_folder(raster_folder_path, lat, lon)

    # Find overlapping data
    ref_data = (csv_dates, csv_values)  # Reference data from CSV files
    test_data = (raster_dates, raster_values)  # Test data from raster files

    # Find overlapping data
    common_dates, ref_values, test_values, overlap_count = temporal_matching(ref_data, test_data, temporal_coverage)
    # print("Overlapping Dates:", common_dates)
    # print("Reference Values:", ref_values)
    # print("Test Values:", test_values)
    # print("Total Valid Overlaps:", overlap_count)

    _metadata['overlaps'] = overlap_count

    # Only add to the new list if overlaps are non-zero
    if overlap_count > 0:
        validation_metadata.append(_metadata)

        # Prepare data to save in Excel
        data_to_save = list(zip(common_dates, ref_values, test_values))
        headers = ['Timestamp', 'wit_sm', 'sebal_sm']
        filename = f'\sebal_{row_path}_witgpi_{_metadata["gpi"]}_lat_{lat}_lon_{lon}.xlsx'

        filename = validation_folder + filename

        # Save data to Excel file
        #save_to_excel(data_to_save, filename, headers)

        filename_img = f'\sebal_{row_path}_witgpi_{_metadata["gpi"]}_lat_{lat}_lon_{lon}.png'
        filename_img = images_folder + filename_img
        save_to_plot(csv_dates, csv_values, raster_dates, raster_values, lat, lon, filename_img)

print('Total number of overlapping in-situ sensors', len(validation_metadata))

def save_metadata(metadata, filename):
    """
    Saves the given metadata list of dictionaries to an Excel file.
    
    Parameters:
    - metadata: List of dictionaries with metadata information.
    - filename: The name of the Excel file to save.
    """
    # Create a workbook and grab the active worksheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    
    # Define the header
    headers = ['gpi', 'latitude', 'longitude', 'start_date', 'end_date', 'count', 'overlaps']
    sheet.append(headers)
    
    # Add data from metadata to the sheet
    for data in metadata:
        row = [data.get(header, None) for header in headers]
        sheet.append(row)
    
    # Save the workbook to a file
    workbook.save(filename)
    print(f"Data saved to {filename}")

# Example usage
# save_metadata(validation_metadata, metadata_file_path)

exit()

# ---------------------------------------------------------------------------------------------------------
# Plotting the results of raster
plt.figure(figsize=(10, 5))
#plt.plot(dates, values, 'o')
plt.plot(raster_dates, raster_values, marker='x', linestyle='--', color='r', label='Sebal Soil Moisture')
plt.title(f'{pattern} Over Time')
plt.xlabel('Date')
plt.ylabel('Soil Moisture Value (m3/m3)')

# Configure date format on x-axis
# Set the x-ticks to match the dates of the data points
plt.gca().set_xticks(raster_dates)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gcf().autofmt_xdate(rotation=90)  # Auto formats the x-axis labels to fit them in the plot area
plt.gca().tick_params(axis='x', labelsize=8)  # Setting the font size to 8

plt.legend()
plt.tight_layout()
#plt.show()


# ---------------------------------------------------------------------------------------------------------     #plotting step 4

# Plotting the results of Sebal and wit_sms
plt.figure(figsize=(12, 6))

# Plot CSV data
plt.plot(csv_dates, csv_values, marker='o', linestyle='-', color='b', label='WIT-SMS')

# Plot Raster data
plt.plot(raster_dates, raster_values, marker='x', linestyle='--', color='r', label='Sebal Soil Moisture')

plt.title(f'Top Soil Moisture Time Series Comparison Latitude: {lat}, Longtitude: {lon}')
plt.xlabel('Date')
plt.ylabel('Soil Moisture (m3/m3)')

# Formatting the date on the x-axis
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.gcf().autofmt_xdate()  # Auto formats the x-axis labels to fit them in the plot area

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ---------------------------------------------------------------------------------------------------------

'''
# convert crs
print('\n------- Converting CRS to WGS84 EPSG 4326 --------')
input_path = r'F:/SEBAL/datasets/SEBAL_out/LBDC/150039/'
output_path = r'F:/SEBAL/datasets/validation/LBDC_validations/150039/'

path = input_path + "**/*.tif"
#Use glob to find all TIFF files in subdirectories
files = glob.glob(path, recursive=True)

if not os.path.isdir(output_path):
    os.makedirs(output_path)

# Filter the list to include only files with "Top_soil_moisture" in their name
for filename in files:
    if filename.endswith(".tif") and pattern in filename:        
        convert_crs(filename, output_path, crs = 4326)

'''