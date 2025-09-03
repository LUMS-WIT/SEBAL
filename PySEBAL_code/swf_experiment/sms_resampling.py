from witsms_reader import SoilMoistureData
import matplotlib.pyplot as plt
from util import remove_nan_entries
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import pearsonr
# sms_id = 4


'''
# ----------------------------------------------------------------------------
# ---------------   Saving the files -----------------------------------------
# ----------------------------------------------------------------------------

# Assuming the SoilMoistureData and remove_nan_entries functions are defined as per your environment
wit_sms_path = 'D:\\SEBAL\\datasets\\witsms\\processed\\SWF SMS\\daily'
soil_moisture_data = SoilMoistureData(wit_sms_path)
soil_moisture_data.read_data()
metadata = soil_moisture_data.get_metadata()

## Read csv file for MODIS data
modis_file_path = r'D:\SEBAL\datasets\SEBAL_out\\csv\sebal_modis_unscaled.csv'
df = pd.read_csv(modis_file_path)

# Function to remove NaN or Inf values before correlation
def remove_nan_and_inf(a, b):
    valid_mask = ~np.isnan(a) & ~np.isnan(b) & ~np.isinf(a) & ~np.isinf(b)
    return a[valid_mask], b[valid_mask]

# Function to align dates and fill missing data
def align_and_fill_sensor_data(sensor_data_dict):
    # Step 1: Find the union of all dates across all sensors (consider only dates, not time)
    all_dates = sorted(set(pd.to_datetime(date).date() for data in sensor_data_dict.values() for date in data['dates']))
    
    # Step 2: Reindex each sensor's data to match the union of dates
    aligned_sensor_data = {}
    for gpi, data in sensor_data_dict.items():
        df = pd.DataFrame({'dates': pd.to_datetime(data['dates']).date, 'values': data['values']})
        df.set_index('dates', inplace=True)
        df = df.reindex(all_dates)
        
        # Fill missing values (choose one approach)
        # df['values'] = df['values'].interpolate()  # Interpolate missing values
        # df['values'] = df['values'].fillna(method='ffill')  # Forward fill missing values
        # df['values'] = df['values'].fillna(method='bfill')  # Backward fill missing values
        # df['values'] = df['values'].fillna(0)  # Replace NaNs with 0

        aligned_sensor_data[gpi] = df['values'].to_numpy()  # Convert back to numpy array
    
    return all_dates, aligned_sensor_data


# Prepare a dictionary to store sensor data
sensor_data_dict = {}

# Organize data by sensor
for _metadata in metadata:
    gpi = _metadata['gpi']  # Unique identifier for each sensor
    lat, lon = float(_metadata['latitude']), float(_metadata['longitude'])

    csv_dates, csv_values = soil_moisture_data.get_soil_moisture_by_location(lat, lon)
    csv_dates, csv_values = remove_nan_entries(csv_dates, csv_values)

    if gpi not in sensor_data_dict:
        sensor_data_dict[gpi] = {
            'dates': csv_dates,
            'values': csv_values
        }

# Align and fill sensor data
aligned_dates, aligned_sensor_data = align_and_fill_sensor_data(sensor_data_dict)



# Prepare sensor data for saving
sensor_data_df = pd.DataFrame(aligned_sensor_data, index=aligned_dates)
# sensor_data_df.columns = [f'sensor_{i+1}' for i in range(len(aligned_sensor_data))]
sensor_data_df.columns = list(aligned_sensor_data.keys())

# Combine sensor and MODIS data into a single DataFrame


# Only consider dates (ignore time part)
raster_dates = pd.to_datetime(df['TimeStamp'], format='%d/%m/%Y %H:%M').dt.date
raster_values = df['250m']

# Align MODIS data with sensor dates
modis_df = pd.DataFrame({'dates': raster_dates, 'MODIS': raster_values})
modis_df.set_index('dates', inplace=True)

# modis_df = modis_df.reindex(aligned_dates)
sensor_data_df = sensor_data_df.loc[modis_df.index]

# Combine sensor and MODIS data into a single DataFrame
combined_df = pd.concat([sensor_data_df, modis_df], axis=1)

# Save the combined data to a CSV file
file_path = 'D:\SEBAL\datasets\SEBAL_out\csv\\filtered_sensors_modis_data.csv'
combined_df.to_csv(file_path, float_format='%.5f')
'''

# Reload the CSV file to ensure all data is correctly loaded
file_path = 'D:\SEBAL\datasets\SEBAL_out\csv\\combined_sensors_modis_data.csv'
data = pd.read_csv(file_path)

# Extract the dates and separate the sensor data and MODIS data
dates = pd.to_datetime(data['dates'], format='%d/%m/%Y')
sensor_columns = [col for col in data.columns if col != 'MODIS' and col != 'dates']
sensor_data = data[sensor_columns].to_numpy()
MODIS = data['MODIS'].to_numpy()


# Calculate the individual correlation for each sensor with MODIS, using the original (non-interpolated) sensor data
original_sensor_data_df = pd.DataFrame(sensor_data, columns=sensor_columns, index=dates)

# Drop any rows that have NaN values for MODIS or any sensor to ensure clean correlation computation
cleaned_df = original_sensor_data_df.join(pd.DataFrame(MODIS, columns=['MODIS'], index=dates)).dropna()

# Compute correlation for each sensor column with MODIS
individual_correlations_original = {col: pearsonr(cleaned_df[col], cleaned_df['MODIS'])[0] 
                                    for col in sensor_columns}

print('Original Correlation', individual_correlations_original)

# Redefine the necessary functions and variables
def remove_nan_and_inf(a, b):
    valid_mask = ~np.isnan(a) & ~np.isnan(b) & ~np.isinf(a) & ~np.isinf(b)
    return a[valid_mask], b[valid_mask]

def composite_series(weights, sensor_data):
    return np.sum([weights[i] * sensor_data[:, i] for i in range(sensor_data.shape[1])], axis=0)

def negative_correlation(weights, MODIS, sensor_data):
    Z = composite_series(weights, sensor_data)
    MODIS_clean, Z_clean = remove_nan_and_inf(MODIS, Z)
    return -pearsonr(MODIS_clean, Z_clean)[0]

# Initial guess for the weights (equal weighting)
initial_weights = np.ones(sensor_data.shape[1]) / sensor_data.shape[1]

# Constraints: weights sum to 1
constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

# Bounds: weights must be non-negative
bounds = [(0, 1) for _ in range(sensor_data.shape[1])]

# Perform the optimization to maximize the correlation
result = minimize(negative_correlation, initial_weights, args=(MODIS, sensor_data),
                  constraints=constraints, bounds=bounds, method='SLSQP')

# Extract the optimized weights and the correlation value
optimized_weights = result.x
optimized_correlation = -result.fun

print('Optimized wieghts',optimized_weights)
print('Final Corelation',optimized_correlation)


# Calculate the weighted average of the sensors based on the optimized weights
weighted_average_sensors = composite_series(optimized_weights, np.nan_to_num(sensor_data))
weighted_average_sensors = np.where(weighted_average_sensors < 0.06, np.nan, weighted_average_sensors)
original_sensor_data_df['w_average'] = weighted_average_sensors
original_sensor_data_df['MODIS'] = MODIS

# Save the DataFrame with the new column to a CSV file
output_file_path = 'D:\SEBAL\datasets\SEBAL_out\csv\combined_averaged_sensors_modis_data.csv'
# original_sensor_data_df.to_csv(output_file_path, float_format='%.5f')

# Plot the MODIS data and the weighted average of sensor data
plt.figure(figsize=(14, 6))
plt.plot(dates, MODIS, label='MODIS', color='blue', marker='o', linestyle='None')
plt.plot(dates, weighted_average_sensors, label='Weighted Average of Sensors', color='red', marker='x', linestyle='None')
plt.title('Comparison of MODIS Data and Weighted Average of Sensor Data')
plt.xlabel('Date')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()






'''
# ----------------------------------------------------------------------
#  ---------------   End to end optimization  --------------------------
# ----------------------------------------------------------------------
# Function to remove NaN or Inf values before correlation
def remove_nan_and_inf(a, b):
    valid_mask = ~np.isnan(a) & ~np.isnan(b) & ~np.isinf(a) & ~np.isinf(b)
    return a[valid_mask], b[valid_mask]

# Function to align dates and fill missing data
def align_and_fill_sensor_data(sensor_data_dict):
    # Step 1: Find the union of all dates across all sensors
    # all_dates = sorted(set(date for data in sensor_data_dict.values() for date in data['dates']))
    all_dates = sorted(set(pd.to_datetime(date).date() for data in sensor_data_dict.values() for date in data['dates']))
    # Step 2: Reindex each sensor's data to match the union of dates
    aligned_sensor_data = {}
    for gpi, data in sensor_data_dict.items():
        df = pd.DataFrame({'dates': pd.to_datetime(data['dates']).date, 'values': data['values']})
        df.set_index('dates', inplace=True)
        df = df.reindex(all_dates)
        
        # Fill missing values (choose one approach)
        # df['values'] = df['values'].interpolate()  # Interpolate missing values
        # df['values'] = df['values'].fillna(method='ffill')  # Forward fill missing values
        # df['values'] = df['values'].fillna(method='bfill')  # Backward fill missing values
        # df['values'] = df['values'].fillna(0)  # Replace NaNs with 0

        aligned_sensor_data[gpi] = df['values'].to_numpy()  # Convert back to numpy array
    
    return all_dates, aligned_sensor_data

wit_sms_path = 'D:\SEBAL\datasets\witsms\processed\SWF SMS\daily'
soil_moisture_data = SoilMoistureData(wit_sms_path)
soil_moisture_data.read_data()
metadata = soil_moisture_data.get_metadata()

# Prepare a dictionary to store sensor data
sensor_data_dict = {}

# Organize data by sensor
for _metadata in metadata:
    gpi = _metadata['gpi']  # Unique identifier for each sensor
    lat, lon = float(_metadata['latitude']), float(_metadata['longitude'])

    csv_dates, csv_values = soil_moisture_data.get_soil_moisture_by_location(lat, lon)
    csv_dates, csv_values = remove_nan_entries(csv_dates, csv_values)

    if gpi not in sensor_data_dict:
        sensor_data_dict[gpi] = {
            'dates': csv_dates,
            'values': csv_values
        }

# Align and fill sensor data
aligned_dates, aligned_sensor_data = align_and_fill_sensor_data(sensor_data_dict)

# aligned_dates, aligned_sensor_data = remove_nan_entries(aligned_dates, aligned_sensor_data)

# Prepare sensor data for optimization
sensor_data = [aligned_sensor_data[gpi] for gpi in aligned_sensor_data]


## Read csv file for MODIS data
modis_file_path = r'D:\SEBAL\datasets\SEBAL_out\\csv\sebal_modis_unscaled.csv'
df = pd.read_csv(modis_file_path)

# Only consider dates (ignore time part)
raster_dates = pd.to_datetime(df['TimeStamp']).dt.date
raster_values = df['250m']

raster_dates, raster_values = remove_nan_entries(raster_dates, raster_values)

# Optional: Remove NaN entries from MODIS data and align with sensor dates
modis_df = pd.DataFrame({'dates': raster_dates, 'values': raster_values})
modis_df.set_index('dates', inplace=True)
modis_df = modis_df.reindex(aligned_dates)  # Align with sensor data dates

# Handle any NaNs in MODIS data as needed
# modis_df['values'] = modis_df['values'].interpolate()  # Interpolate, or choose another method

MODIS = modis_df['values'].to_numpy()


# Define the functions for optimization (as before)
def composite_series(weights, sensor_data):
    # Calculate the weighted sum of the sensor data across time
    return np.sum([weights[i] * sensor_data[i] for i in range(len(sensor_data))], axis=0)

def negative_correlation(weights, MODIS, sensor_data):
    # Calculate the negative Pearson correlation
    Z = composite_series(weights, sensor_data)
    # Remove NaNs and Infs from MODIS and Z before calculating correlation
    MODIS_clean, Z_clean = remove_nan_and_inf(MODIS, Z)

    return -pearsonr(MODIS_clean, Z_clean)[0]


# Initial guess for the weights (equal weighting)
initial_weights = np.ones(len(sensor_data)) / len(sensor_data)

# Constraints: weights sum to 1
constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

# Bounds: weights must be non-negative
bounds = [(0, 1) for _ in range(len(sensor_data))]

# Optimize weights to maximize correlation
result = minimize(negative_correlation, initial_weights, args=(MODIS, sensor_data),
                  constraints=constraints, bounds=bounds, method='SLSQP')

# Optimized weights
optimized_weights = result.x

# Correlation with optimized weights
optimized_correlation = -result.fun

print("Optimized Weights:", optimized_weights)
print("Optimized Correlation:", optimized_correlation)
'''