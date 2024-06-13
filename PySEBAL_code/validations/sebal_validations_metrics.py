import sys
import metrics
import openpyxl
import numpy as np
import os, re, fnmatch
import matplotlib.pyplot as plt
import pandas as pd

# Define the path to your Excel file
path_row = '150039'
temporal_win = '0'
combine_validations = True
rescaled = True
plotting = True

if rescaled:
    master_folder = fr'F:\SEBAL\datasets\validation\LBDC_validations\validation_points_rescaled' 
    data_folder = fr'F:\SEBAL\datasets\validation\LBDC_validations\validation_points_rescaled\{path_row}_{temporal_win}'
    output_file = fr'F:\SEBAL\datasets\validation\LBDC_validations\results\validations_{path_row}_tw_{temporal_win}_rescaled.xlsx'
    combine_output_file = fr'F:\SEBAL\datasets\validation\LBDC_validations\results\validations_tw_{temporal_win}_rescaled.xlsx'

    plot_file_output = fr'F:\SEBAL\datasets\validation\LBDC_validations\results\{path_row}_tw_{temporal_win}_rescaled.png'
    combine_plot_file_output = fr'F:\SEBAL\datasets\validation\LBDC_validations\results\tw_{temporal_win}_rescaled.png'
else:
    master_folder = fr'F:\SEBAL\datasets\validation\LBDC_validations\validation_points' 
    data_folder = fr'F:\SEBAL\datasets\validation\LBDC_validations\validation_points\{path_row}_{temporal_win}'
    output_file = fr'F:\SEBAL\datasets\validation\LBDC_validations\results\validations_{path_row}_tw_{temporal_win}.xlsx'
    combine_output_file = fr'F:\SEBAL\datasets\validation\LBDC_validations\results\validations_tw_{temporal_win}.xlsx'

    plot_file_output = fr'F:\SEBAL\datasets\validation\LBDC_validations\results\{path_row}_tw_{temporal_win}.png'
    combine_plot_file_output = fr'F:\SEBAL\datasets\validation\LBDC_validations\results\tw_{temporal_win}.png'

metadata_file = fr'F:\SEBAL\datasets\validation\LBDC_validations\metadata_{path_row}_tw_{temporal_win}.xlsx'
xlsx_file_path = r'F:\SEBAL\datasets\validation\LBDC_validations\validation_points\149039_1\sebal_149039_witgpi_2021073_lat_30.898787_lon_73.4677055.xlsx'

def extract_sm_data(xlsx_file_path,ref=1, test=2):
    # Load the workbook and select the active sheet
    workbook = openpyxl.load_workbook(filename=xlsx_file_path)
    sheet = workbook.active  # or workbook['SheetName'] if you know the sheet name

    # Initialize lists to store 'ref_sm' and 'test_sm' values
    test_sm_list = []   # x
    ref_sm_list = []    # y

    # Assuming the first row contains headers and data starts from the Reference row
    for row in sheet.iter_rows(min_row=2, values_only=True):
        # Append the values from 'ref_sm' and 'test_sm' columns to their respective lists
        ref_sm_list.append(row[1])
        test_sm_list.append(row[2])

    # Convert lists to numpy arrays before returning
    ref_sm_array = np.array(ref_sm_list)
    test_sm_array = np.array(test_sm_list)

    return ref_sm_array, test_sm_array


# wit_sm, sebal_sm = extract_sm_data(xlsx_file_path)

# print(wit_sm, sebal_sm)


# # x, y
# mse, mse_corr, mse_bias, mse_var = metrics.mse(sebal_sm, wit_sm)
# p_rho = metrics.pearson_r(sebal_sm, wit_sm)
# s_rho = metrics.spearman_r(sebal_sm, wit_sm)
# ubrmsd = metrics.ubrmsd(sebal_sm, wit_sm)

# print('mse:', mse)
# print('pearson:', p_rho)
# print('spearmans rho:', s_rho)
# print('UbRMSD:', ubrmsd)

def combine_val_files(root_dir, specific_folder_name):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if fnmatch.fnmatch(os.path.basename(dirpath), specific_folder_name):
            for file in filenames:
                if file.endswith('.xlsx') and 'witgpi' in file:
                    file_paths.append(os.path.join(dirpath, file))
    return file_paths

def validations(folder_path):
    # Initialize lists to compile data from all files
    wit_sm_ = []
    sebal_sm_ = []


    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".xlsx") and 'witgpi' in f]
    total_files = len(files)
    print(f"Reading {total_files} files...")  # Debugging output

    observations = 0
    for file in files:
        wit_sm, sebal_sm = extract_sm_data(file)
                # x and y must have length at least 2.
        if len(wit_sm) > 1:
            observations += len(wit_sm)
            wit_sm_.extend(wit_sm)
            sebal_sm_.extend(sebal_sm)

    bias = metrics.bias(sebal_sm_, wit_sm_)
    mse, mse_corr, mse_bias, mse_var = metrics.mse(sebal_sm_, wit_sm_)
    ubrmsd = metrics.ubrmsd(sebal_sm_, wit_sm_)
    p_rho = metrics.pearson_r(sebal_sm_, wit_sm_)
    s_rho = metrics.spearman_r(sebal_sm_, wit_sm_)

    metrics_dict = {
        'bias': bias,
        'mse': mse,
        'ubrmsd': ubrmsd,
        'p_rho': p_rho,
        's_rho': s_rho
    }

    return metrics_dict, observations

def validations_gpi(folder_path):
    
    # Initialize a dictionary to store lists of results for each metric
    metrics_dict = {
        'gpi': [],
        'bias': [],
        'mse': [],
        'ubrmsd': [],
        'p_rho': [],
        's_rho': []
    }

    if combine_validations:
        specific_folder_name = f'*_{temporal_win}'
        files = combine_val_files(master_folder, specific_folder_name)
        total_files = len(files)
        print(f"Reading {total_files} files...")  # Debugging outpt
    
    else:    
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".xlsx") and 'witgpi' in f]
        total_files = len(files)
        print(f"Reading {total_files} files...")  # Debugging output

    # defining pattern for extracting gpi
    pattern = r'witgpi_([^_]+)_'

    observations = 0
    for file in files:
        wit_sm, sebal_sm = extract_sm_data(file)

        gpi = re.search(pattern, file).group(1)
        # x and y must have length at least 2. otherwise p_rho wont work
        if len(wit_sm) > 1:
            observations += len(wit_sm)

            bias = metrics.bias(sebal_sm, wit_sm)
            mse, mse_corr, mse_bias, mse_var = metrics.mse(sebal_sm, wit_sm)
            ubrmsd = metrics.ubrmsd(sebal_sm, wit_sm)
            p_rho = metrics.pearson_r(sebal_sm, wit_sm)
            s_rho = metrics.spearman_r(sebal_sm, wit_sm)

            metrics_dict['gpi'].append(gpi)
            metrics_dict['bias'].append(bias)
            metrics_dict['mse'].append(mse)
            metrics_dict['ubrmsd'].append(ubrmsd)
            metrics_dict['p_rho'].append(p_rho)
            metrics_dict['s_rho'].append(s_rho)

    
    return metrics_dict, observations

def compute_statistics(data_dict):
    stats_results = {}
    for key, values in data_dict.items():
        if key == 'gpi':
            continue
        stats_results[key] = {}
        if key in ['p_rho', 's_rho']:
            stats_results[key]['mean'] = metrics.mean_r(values)
            stats_results[key]['median'] = np.nanmedian(values)
            stats_results[key]['IQR'] = metrics.calculate_iqr(values)
        else:
            stats_results[key]['mean'] = np.nanmean(values)
            stats_results[key]['median'] = np.nanmedian(values)
            stats_results[key]['IQR'] = metrics.calculate_iqr(values)
    return stats_results


def plot_box_and_whiskers(metrics_dict, filename, save= False):
    # Creating the plot
    fig, ax = plt.subplots()
    # Prepare data for plotting
    # Prepare data for plotting, excluding NaN values
    data_to_plot = [
        [value for value in metrics_dict[key] if not np.isnan(value)] 
        for key in metrics_dict if key != 'gpi'
    ]
    # Create box plot
    bp = ax.boxplot(data_to_plot, showfliers=False) #, notch=True, patch_artist=True)

    # Annotating the median
    for i, line in enumerate(bp['medians']):
        x, y = line.get_xydata()[1]  # top of median line
        ax.annotate(f'{y:.3f}', xy=(x, y), xytext=(x, y+0.5), 
                    textcoords='offset points', ha='center', va='bottom')

    # # Annotating the mean
    # for i, data in enumerate(data_to_plot):
    #     mean_value = np.mean(data)  # Calculate mean
    #     ax.annotate(f'{mean_value:.3f}', xy=(i+1, mean_value), xytext=(0, 10),
    #                 textcoords='offset points', ha='center', va='bottom')
                
    ax.set_title('Box and Whisker Plot for Metrics')
    ax.set_ylabel('Metric Values')
    ax.set_xlabel('Metrics')
    ax.set_xticklabels([key for key in metrics_dict.keys() if key != 'gpi'])

    # Add horizontal grid lines
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    plt.show()

    # Save the plot if requested
    if save:
        fig.savefig(filename)
        print(f'Plot saved as {filename}')

if combine_validations:
    input_folder = master_folder
else:
    input_folder = data_folder

metrics_dict, num_of_obs = validations_gpi(input_folder)
stats_results = compute_statistics(metrics_dict)
print('------------- results for gpi based metrics ----------------')
print('Number of Observatoions N:', num_of_obs)
print(stats_results)
# plot_box_and_whiskers(metrics_dict)


df = pd.read_excel(metadata_file)
df['gpi'] = df['gpi'].astype(str)
metrics_df = pd.DataFrame(metrics_dict)

# Merge the Excel DataFrame with the metrics DataFrame on the 'gpi' column
merged_df = pd.merge(df, metrics_df, on='gpi', how='left')

# Create a DataFrame for the summary statistics
summary_data = {
    'Metric': ['bias', 'mse', 'ubrmsd', 'p_rho', 's_rho'],
    'mean': [stats_results['bias']['mean'], stats_results['mse']['mean'], stats_results['ubrmsd']['mean'], stats_results['p_rho']['mean'], stats_results['s_rho']['mean']],
    'median': [stats_results['bias']['median'], stats_results['mse']['median'], stats_results['ubrmsd']['median'], stats_results['p_rho']['median'], stats_results['s_rho']['median']],
    'IQR': [stats_results['bias']['IQR'], stats_results['mse']['IQR'], stats_results['ubrmsd']['IQR'], stats_results['p_rho']['IQR'], stats_results['s_rho']['IQR']]
}
summary_df = pd.DataFrame(summary_data)

# Add observations as the first row in the summary DataFrame
observations_df = pd.DataFrame({'Metric': ['Observations'], 'mean': [num_of_obs], 'median': [''], 'IQR': ['']})
summary_df = pd.concat([observations_df, summary_df], ignore_index=True)

if combine_validations:
    # Save the merged DataFrame to the first sheet and the summary DataFrame to the second sheet
    with pd.ExcelWriter(combine_output_file, engine='xlsxwriter') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

    print("Validations saved to", combine_output_file)
    plot_file_name = combine_plot_file_output
else:
    # Save the merged DataFrame to the first sheet and the summary DataFrame to the second sheet
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        merged_df.to_excel(writer, sheet_name='MetaData', index=False)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

    print("Validations saved to", output_file)
    plot_file_name = plot_file_output
# print('------------- results for combined metrics ----------------')
# metrics_dict_, num_of_obs_ = validations(data_folder)
# print('Number of Observatoions N:', num_of_obs_)
# print(metrics_dict_)


plot_box_and_whiskers(metrics_dict, filename= plot_file_name, save=plotting)