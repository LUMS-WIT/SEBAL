import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import openpyxl

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

def remove_nan_entries(dates, values):
    """
    Removes entries with NaN values from date and value arrays.

    Parameters
    ----------
    dates : array-like
        Array of dates corresponding to the values.
    values : array-like
        Array of values associated with the dates.

    Returns
    -------
    tuple
        A tuple containing two arrays:
        - The cleaned array of dates with corresponding non-NaN values.
        - The cleaned array of values that are not NaN.
    """
    # Ensure the input arrays are numpy arrays
    dates = np.array(dates)
    values = np.array(values)

    # Create a mask to filter out NaN entries
    valid_indices = ~np.isnan(values)

    # Apply the mask to both the dates and values arrays
    cleaned_dates = dates[valid_indices]
    cleaned_values = values[valid_indices]

    return cleaned_dates.tolist(), cleaned_values.tolist()
