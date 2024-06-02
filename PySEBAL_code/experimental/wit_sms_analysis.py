import sys
sys.path.append('F:\SEBAL\PySEBAL_code')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
import os
import re
import numpy as np
from utils import *

pattern = "Top_soil_moisture"

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
                    'count': count_soil_moisture,
                    'start_date': start_date,
                    'end_date': end_date
                })

    def print_metadata(self):
        headers = ['gpi', 'latitude', 'longitude', 'count', 'start_date', 'end_date']
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
        headers = ['gpi', 'latitude', 'longitude', 'count', 'start_date', 'end_date']
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

    def plot_data(self, gpi=None):
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
soil_moisture_data = SoilMoistureData('F:\SEBAL\datasets\WIT_SM\SMS_final_v2')
soil_moisture_data.read_data()
# soil_moisture_data.print_metadata()  # Print metadata in CSV format
# #soil_moisture_data.save_metadata_to_csv()  # Save metadata to a CSV file


# # Plotting data for a specific GPI
# soil_moisture_data.plot_data('2021069')
metadata = soil_moisture_data.get_metadata()

# for data in metadata:
#     lat, lon = soil_moisture_data.get_lat_lon_by_gpi(data['gpi'])  # Replace '123456' with actual GPI
#     print(f"Latitude, Longitude: {float(lat), float(lon)}")

lat, lon = 30.676265,73.151078

csv_dates, csv_values = soil_moisture_data.get_soil_moisture_by_location(float(lat), float(lon))  # Replace '123456' with actual GPI
# ------------------------------------------------------------------------------------


from osgeo import gdal

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

raster_file_path = r'F:\SEBAL\datasets\SEBAL_out\LBDC\149039\temp\L9_Top_soil_moisture_30m_2023_06_23_174.tif'
data_within_extent = find_data_within_extent(metadata, raster_file_path)

print(f"Data within raster extent: {len(data_within_extent)}")
for data in data_within_extent:
    print(data)


# -----------------------------------------------------------------------------------
from osgeo import gdal
import osgeo.osr as osr

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
        exit()

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

# Example usage
file_path = r'F:/SEBAL/datasets/SEBAL_out/LBDC/149039/temp/L8_Top_soil_moisture_30m_2020_09_10_254.tif'
folder_path = r'F:/SEBAL/datasets/SEBAL_out/LBDC/149039/temp/'
# latitude = 31.014104
# longitude = 73.486085

latitude = float(lat)
longitude = float(lon)

# value = read_raster_value(file_path, latitude, longitude)
# print("Value at location:", value)


dates, values = read_raster_folder(folder_path, latitude, longitude)

print(dates, values)
print('Total Count :', len(values))

nan_count = np.sum(np.isnan(values))
print('Data with NaN values:', nan_count)
# Plotting the results
plt.figure(figsize=(10, 5))
#plt.plot(dates, values, 'o')
plt.plot(dates, values, marker='o', linestyle='dashed')
plt.title(f'{pattern} Over Time')
plt.xlabel('Date')
plt.ylabel('Soil Moisture Value (m3/m3)')

# Configure date format on x-axis
# Set the x-ticks to match the dates of the data points
plt.gca().set_xticks(dates)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gcf().autofmt_xdate(rotation=90)  # Auto formats the x-axis labels to fit them in the plot area
plt.gca().tick_params(axis='x', labelsize=8)  # Setting the font size to 8

plt.legend()
plt.tight_layout()
#plt.show()


raster_dates, raster_values = dates, values

# Plotting the results
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

# -----------------------------------


# convert crs
# print('\n------- Converting CRS to WGS84 EPSG 4326 --------')
# # path = folder_path + "*/*.tif"
# # # Use glob to find all TIFF files in subdirectories
# # files = glob.glob(folder_path, recursive=True)

# tempdir = folder_path + 'temp/'
# if not os.path.isdir(tempdir):
#     os.makedirs(tempdir)	
# # Filter the list to include only files with "Top_soil_moisture" in their name
#     # Walk through the directory, including subdirectories
# for root, dirs, files in os.walk(folder_path):    
#     # Iterate through all files in the folder
#     for filename in files:
#         if filename.endswith(".tif") and pattern in filename:
#             # Construct the full file path
#             file_path = os.path.join(root, filename)
#     convert_crs(file_path, tempdir, crs = 4326)