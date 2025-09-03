import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors as cl
import pandas as pd

file_path = 'D:\SEBAL\datasets/validation\LBDC_validations/results/validations_149039_tw_0_rescaled.xlsx'
file_path1 = 'D:\SEBAL\datasets/validation\LBDC_validations/results/validations_150039_tw_0_rescaled.xlsx'


extent = [69.2, 75.0, 27.6, 34.0]  # Set the map extent to Punjab, Pakistan
param = 'overlaps'

# Function to define custom color maps
def get_status_colors():
    cmap = plt.get_cmap('Set3', 14)  # Adjusting for 14 different statuses
    colors = [cmap(i) for i in range(cmap.N)]
    colors.insert(0, (0, 0.66666667, 0.89019608, 1.0))  # Special color for a specific status
    colors.insert(0, (0.45882353, 0.08235294, 0.11764706, 1.0))  # Another special color
    return cl.ListedColormap(colors)

# Define color maps as per your mapping
_cclasses =  {
    'div_better': plt.get_cmap(
        'RdYlBu'
    ),  # diverging: 1 good, 0 special, -1 bad (pearson's R, spearman's rho')
    'div_worse': plt.get_cmap(
        'RdYlBu_r'
    ),  # diverging: 1 bad, 0 special, -1 good (difference of bias)
    'div_neutr':
    plt.get_cmap('RdYlGn'),  # diverging: zero good, +/- neutral: (bias)
    'seq_worse': plt.get_cmap(
        'YlGn_r'
    ),  # sequential: increasing value bad (p_R, p_rho, rmsd, ubRMSD, RSS)
    'seq_better': plt.get_cmap(
        'YlGn'),  # sequential: increasing value good (n_obs, STDerr)
    'qua_neutr':
    get_status_colors(),  # qualitative category with 2 forced colors
}

_colormaps = {
    'R': _cclasses['div_better'],
    'p_R': _cclasses['seq_worse'],
    'rho': _cclasses['div_better'],
    #'p_rho': _cclasses['seq_worse'],
    'p_rho': _cclasses['div_neutr'],
    's_rho': _cclasses['div_neutr'],
    'rmsd': _cclasses['seq_worse'],
    'bias': _cclasses['div_neutr'],
    # 'n_obs': _cclasses['seq_better'],
    'overlaps': _cclasses['seq_better'],
    'ubrmsd': _cclasses['seq_worse'],
    'mse': _cclasses['seq_worse'],
    'mse_corr': _cclasses['seq_worse'],
    'mse_bias': _cclasses['seq_worse'],
    'mse_var': _cclasses['seq_worse'],
    'RSS': _cclasses['seq_worse'],
    'tau': _cclasses['div_better'],
    'p_tau': _cclasses['seq_worse'],
    'snr': _cclasses['div_better'],
    'err_std': _cclasses['seq_worse'],
    'beta': _cclasses['div_neutr'],
    'status': _cclasses['qua_neutr'],
}


# 59 in 150039
# 34 in 149039
# total : 93
df1 = pd.read_excel(file_path)
df2 = pd.read_excel(file_path1)


# Filter rows where metric data is available
metrics_columns = ['overlaps','bias', 'mse', 'ubrmsd', 'p_rho', 's_rho']
df1_filtered = df1.dropna(subset=metrics_columns)
df2_filtered = df2.dropna(subset=metrics_columns)


df_final = pd.concat([df1_filtered, df2_filtered], ignore_index=True)
# Select required columns
df_final = df_final[['latitude', 'longitude'] + metrics_columns]

# Assuming df_final is loaded with your data
lats = df_final['latitude'].tolist()
lons = df_final['longitude'].tolist()
# values = df_final['bias'].tolist()  # Make sure 'bias' is present in df_final

print(f'Total Number of sites observed : {len(lons)}')

# Create a map with PlateCarree projection
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_extent(extent, crs=ccrs.PlateCarree())  # Set map extent to focus on Punjab, Pakistan

states_provinces = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='50m',
    facecolor='none')

# Add map features
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.STATES, linestyle=':')
ax.add_feature(cfeature.RIVERS)
# ax.add_feature(cfeature.LAND)
ax.add_feature(states_provinces, edgecolor='gray')

# Add gridlines
gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': 12, 'color': 'gray'}
gl.ylabel_style = {'size': 12, 'color': 'gray'}

# Plot the scatter points using the custom colormap for 'bias'
sc = ax.scatter(lons, lats, c=df_final[param].tolist(), cmap=_colormaps[param], marker='o', edgecolor='k', s=60, transform=ccrs.PlateCarree())

# Add a color bar
cbar = plt.colorbar(sc, ax=ax, orientation='vertical')
cbar.set_label(param)

# Add a title
plt.title(f'Scatter Plot of {param} on Map with Gridlines')

# Show the plot
plt.show()
