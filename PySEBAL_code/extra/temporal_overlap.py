import numpy as np
import datetime

def find_valid_overlapping_data(ref_data, test_data):
    """
    Finds overlapping dates considering only year, month, and day in two datasets,
    with an added check for neighboring days in the test data if the exact match
    day does not have a valid value.
    
    Parameters:
    - ref_data: Tuple containing two lists (dates and values) for the reference dataset.
    - test_data: Tuple containing two lists (dates and values) for the test dataset.
    
    Returns:
    - A tuple containing lists of dates, values from the reference dataset, adjusted
      values from the test dataset, and the count of valid overlaps.
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
        # Check exact date match first
        test_value = test_data_dict.get(ref_date)

        # If no valid exact match, check the day before and the day after
        if test_value is None or np.isnan(test_value):
            day_before = (ref_date - datetime.timedelta(days=1))
            day_after = (ref_date + datetime.timedelta(days=1))
            test_value = test_data_dict.get(day_before) or test_data_dict.get(day_after)
        
        # If found a valid value in any of these three days
        if test_value is not None and not np.isnan(test_value):
            overlapping_ref_dates.append(ref_date)
            overlapping_ref_values.append(ref_value)
            overlapping_test_values.append(test_value)

    # Count of valid overlapping data points
    valid_overlap_count = len(overlapping_ref_dates)

    return overlapping_ref_dates, overlapping_ref_values, overlapping_test_values, valid_overlap_count

# Find overlapping data
ref_data = (csv_dates, csv_values)  # Reference data from CSV files
test_data = (raster_dates, raster_values)  # Test data from raster files

# Find overlapping data
common_dates, ref_values, test_values, overlap_count = find_valid_overlapping_data(ref_data, test_data)
print("Overlapping Dates:", common_dates)
print("Reference Values:", ref_values)
print("Test Values:", test_values)
print("Total Valid Overlaps:", overlap_count)