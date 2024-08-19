import glob, os, datetime, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from raster_resampling import resampling, reproject
from util import remove_nan_entries
from sebal_reader import SebalSoilMoistureData
from witsms_reader import SoilMoistureData
from validations.scaling import scaling


'''
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------
# ---------------   Multi resolution with sms data overlay  -----------------------------------------
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

scaling_ = False
pattern = 'Top_soil_moisture'
# pattern = 'Root_zone_moisture'
sms_id = 0
spatial_ress = [30, 60, 90]

# Initialize the figure outside the loop
plt.figure(figsize=(10, 5))

for spatial_res in spatial_ress:
    input_path = r'D:\SEBAL\datasets\SEBAL_out\swf\\'
    output_path = f'D:\SEBAL\datasets\SEBAL_out\swf_sm_{spatial_res}m\{pattern}\\'

    poly_11_0 =	31.078510, 74.165753
    poly_11_1 = 31.078504, 74.167007
    poly_11_2 =	31.079568, 74.166973
    poly_11_3 = 31.079576, 74.165727
    poly_11_4 = 31.078981, 74.166425
    poly_12_0 =	31.074229, 74.177412
    poly_12_4 =	31.074693, 74.177997

    wheat_sms = {
        'poly_11_0': poly_11_0,
        'poly_11_1': poly_11_1,
        'poly_11_2': poly_11_2,
        'poly_11_3': poly_11_3,
        'poly_11_4': poly_11_4
    }

    mustard_sms = {
        'poly_12_0': poly_12_0,
        'poly_12_4': poly_12_4
    }

    raster_data = SebalSoilMoistureData(output_path)

    wit_sms_path = 'D:\SEBAL\datasets\witsms\processed\SWF SMS\daily'
    soil_moisture_data = SoilMoistureData(wit_sms_path)
    soil_moisture_data.read_data()
    metadata = soil_moisture_data.get_metadata()

    _metadata = metadata[sms_id]
    lat, lon = float(_metadata['latitude']), float(_metadata['longitude'])

    raster_dates, raster_values = raster_data.get_data(lat, lon)
    csv_dates, csv_values = soil_moisture_data.get_soil_moisture_by_location(lat, lon)

    raster_dates, raster_values = remove_nan_entries(raster_dates, raster_values)
    csv_dates, csv_values = remove_nan_entries(csv_dates, csv_values)

    if scaling_:
        # Data statistical re-scaling
        ref_data = (csv_dates, csv_values)  # Reference data from CSV files
        test_data = (raster_dates, raster_values)  # Test data from raster files
        test_data, _ = scaling(test_data, ref_data)
        csv_dates, csv_values = ref_data
        raster_dates, raster_values = test_data

    # Plot CSV data
    if spatial_res == 30:
        plt.plot(csv_dates, csv_values, marker='o', linestyle='-', color='b', label='WIT-SMS')

    # Plot Raster data for each spatial resolution
    plt.plot(raster_dates, raster_values, marker='x', linestyle='--', label=f'Sebal Soil Moisture {spatial_res}m')

# Common plot settings outside the loop
plt.title(f'Top Soil Moisture Time Series Comparison Latitude: {lat}, Longitude: {lon}')
plt.xlabel('Date')
plt.ylabel('Soil Moisture (m3/m3)')

# Formatting the date on the x-axis
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.gcf().autofmt_xdate()  # Auto formats the x-axis labels to fit them in the plot area

plt.legend()
plt.grid(True)
plt.show()

exit()
'''
'''
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------
# ---------------   Single resolution with sms data overlay  -----------------------------------------
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

scaling_ = False
pattern = 'Top_soil_moisture'
# pattern = 'Root_zone_moisture'
spatial_res = 90
sms_id = 0

# # convert crs
# print('\n------- Converting CRS to WGS84 EPSG 4326 --------')
input_path = r'D:\SEBAL\datasets\SEBAL_out\swf\\'
output_path = f'D:\SEBAL\datasets\SEBAL_out\swf_sm_{spatial_res}m\{pattern}\\'

# if not os.path.isdir(output_path):
#     os.makedirs(output_path)

# resampling(input_path, output_path, target_resolution= spatial_res, pattern=pattern)


poly_11_0 =	31.078510, 74.165753
poly_11_1 = 31.078504, 74.167007
poly_11_2 =	31.079568, 74.166973
poly_11_3 = 31.079576, 74.165727
poly_11_4 = 31.078981, 74.166425
poly_12_0 =	31.074229, 74.177412
poly_12_4 =	31.074693, 74.177997

# wheat_sms = [poly_11_0, poly_11_1, poly_11_2, poly_11_3, poly_11_4]
# mustard_sms = [poly_12_0, poly_12_4]

wheat_sms = {
    'poly_11_0': poly_11_0,
    'poly_11_1': poly_11_1,
    'poly_11_2': poly_11_2,
    'poly_11_3': poly_11_3,
    'poly_11_4': poly_11_4
}

mustard_sms = {
    'poly_12_0': poly_12_0,
    'poly_12_4': poly_12_4
}

raster_data = SebalSoilMoistureData(output_path)

wit_sms_path = 'D:\SEBAL\datasets\witsms\processed\SWF SMS\daily'
soil_moisture_data = SoilMoistureData(wit_sms_path)
soil_moisture_data.read_data()
metadata = soil_moisture_data.get_metadata()

# Initialize the figures
plt.figure(figsize=(10, 5))

# lat, lon = poly_11_1
_metadata = metadata[sms_id]
lat, lon = float(_metadata['latitude']), float(_metadata['longitude'])

raster_dates, raster_values = raster_data.get_data(lat, lon)
csv_dates, csv_values = soil_moisture_data.get_soil_moisture_by_location(lat, lon)

raster_dates, raster_values = remove_nan_entries(raster_dates, raster_values)
csv_dates, csv_values = remove_nan_entries(csv_dates, csv_values)

if scaling_:
    # Data statistical re-scaling
    ref_data = (csv_dates, csv_values)  # Reference data from CSV files
    test_data = (raster_dates, raster_values)  # Test data from raster files
    test_data, _ = scaling(test_data, ref_data)
    csv_dates, csv_values = ref_data
    raster_dates, raster_values = test_data


# Plot CSV data
plt.plot(csv_dates, csv_values, marker='o', linestyle='-', color='b', label='WIT-SMS')

# Plot Raster data
plt.plot(raster_dates, raster_values, marker='x', linestyle='--', color='r', label=f'Sebal Soil Moisture {spatial_res}m')

plt.title(f'Top Soil Moisture Time Series Comparison Latitude: {lat}, Longitude: {lon}')
plt.xlabel('Date')
plt.ylabel('Soil Moisture (m3/m3)')

# Formatting the date on the x-axis
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.gcf().autofmt_xdate()  # Auto formats the x-axis labels to fit them in the plot area

plt.legend()
plt.grid(True)
plt.show()
exit()
'''


# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------
# ---------------   All sebal/sms plots data for wheat feild  -----------------------------------------
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

pattern = 'Top_soil_moisture'
# pattern = 'Root_zone_moisture'
spatial_res = 30
sms_id = 0
sebal = True

# # convert crs
# print('\n------- Converting CRS to WGS84 EPSG 4326 --------')
input_path = r'D:\SEBAL\datasets\SEBAL_out\swf\\'
output_path = f'D:\SEBAL\datasets\SEBAL_out\swf_sm_{spatial_res}m\{pattern}\\'
raster_data = SebalSoilMoistureData(output_path)

wit_sms_path = 'D:\SEBAL\datasets\witsms\processed\SWF SMS\daily'
soil_moisture_data = SoilMoistureData(wit_sms_path)
soil_moisture_data.read_data()
metadata = soil_moisture_data.get_metadata()

poly_11_0 =	31.078510, 74.165753
poly_11_1 = 31.078504, 74.167007
poly_11_2 =	31.079568, 74.166973
poly_11_3 = 31.079576, 74.165727
poly_11_4 = 31.078981, 74.166425
poly_12_0 =	31.074229, 74.177412
poly_12_4 =	31.074693, 74.177997

wheat_sms = {
    'poly_11_0': poly_11_0,
    'poly_11_1': poly_11_1,
    'poly_11_2': poly_11_2,
    'poly_11_3': poly_11_3,
    'poly_11_4': poly_11_4
}

mustard_sms = {
    'poly_12_0': poly_12_0,
    'poly_12_4': poly_12_4
}

if sebal:
    #Plotting wheat soil moisture data
    for var_name, sms in wheat_sms.items():
        lat, lon = sms
        
        raster_dates, raster_values = raster_data.get_data(lat, lon)
        raster_dates, raster_values = remove_nan_entries(raster_dates, raster_values)
        plt.plot(raster_dates, raster_values, marker='x', linestyle='--', label=var_name)

    # Plotting mustard soil moisture data
    # for var_name, sms in mustard_sms.items():
    #     lat, lon = sms
    #     raster_dates, raster_values = raster_data.get_data(lat, lon)
    #     raster_dates, raster_values = remove_nan_entries(raster_dates, raster_values)
    #     plt.plot(raster_dates, raster_values, marker='o', linestyle='-', label=var_name)
else:
    # Plotting of sms data
    soil_moisture_data = SoilMoistureData(wit_sms_path)
    soil_moisture_data.read_data()
    metadata = soil_moisture_data.get_metadata()

    for _metadata in metadata:

        lat, lon = float(_metadata['latitude']), float(_metadata['longitude'])
        csv_dates, csv_values = soil_moisture_data.get_soil_moisture_by_location(lat, lon)
        csv_dates, csv_values = remove_nan_entries(csv_dates, csv_values)
        plt.plot(csv_dates, csv_values, marker='x', linestyle='-', label=_metadata['gpi'])

# Configure the plot
plt.xlabel('Date')
plt.ylabel('Soil Moisture Value (m3/m3)')

# Configure date format on x-axis
if sebal:
    plt.gca().set_xticks(raster_dates)
else:
    plt.gca().set_xticks(csv_dates)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gcf().autofmt_xdate(rotation=90)  # Auto formats the x-axis labels to fit them in the plot area
plt.gca().tick_params(axis='x', labelsize=8)  # Setting the font size to 8

# Add a legend and finalize the plot
plt.legend()
plt.tight_layout()

# Show the plot
plt.show()
  

'''
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------
# ---------------   Single sebal/sms plots data for wheat feild  -----------------------------------------
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

pattern = 'Top_soil_moisture'
# pattern = 'Root_zone_moisture'
spatial_res = 30
sms_id = 4
scaling_ = False
# # convert crs
# print('\n------- Converting CRS to WGS84 EPSG 4326 --------')
input_path = r'D:\SEBAL\datasets\SEBAL_out\swf\\'
output_path = f'D:\SEBAL\datasets\SEBAL_out\swf_sm_{spatial_res}m\{pattern}\\'
raster_data = SebalSoilMoistureData(output_path)

poly_11_0 =	31.078510, 74.165753
poly_11_1 = 31.078504, 74.167007
poly_11_2 =	31.079568, 74.166973
poly_11_3 = 31.079576, 74.165727
poly_11_4 = 31.078981, 74.166425
poly_12_0 =	31.074229, 74.177412
poly_12_4 =	31.074693, 74.177997


# lat, lon = poly_11_1

wit_sms_path = 'D:\SEBAL\datasets\witsms\processed\SWF SMS\daily'
soil_moisture_data = SoilMoistureData(wit_sms_path)
soil_moisture_data.read_data()
metadata = soil_moisture_data.get_metadata()

_metadata = metadata[sms_id]
lat, lon = float(_metadata['latitude']), float(_metadata['longitude'])

raster_dates, raster_values = raster_data.get_data(lat, lon)
csv_dates, csv_values = soil_moisture_data.get_soil_moisture_by_location(lat, lon)

raster_dates, raster_values = remove_nan_entries(raster_dates, raster_values)

csv_dates, csv_values = remove_nan_entries(csv_dates, csv_values)
raster_dates, raster_values = remove_nan_entries(raster_dates, raster_values)

if scaling_:
    # Data statistical re-scaling
    ref_data = (csv_dates, csv_values)  # Reference data from CSV files
    test_data = (raster_dates, raster_values)  # Test data from raster files
    test_data, _ = scaling(test_data, ref_data)
    csv_dates, csv_values = ref_data
    raster_dates, raster_values = test_data

# Plotting the results of raster
plt.figure(figsize=(10, 5))
#plt.plot(dates, values, 'o')
# Plot CSV data
plt.plot(csv_dates, csv_values, marker='o', linestyle='-', color='purple', label='WIT-SMS')

plt.plot(raster_dates, raster_values, marker='x', linestyle='--', color='r', label=pattern)
# plt.title(f'{pattern} Over Time')
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
plt.show()
'''
