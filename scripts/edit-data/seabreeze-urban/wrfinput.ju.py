# %%

from netCDF4 import Dataset
from glob import glob
import sys, os

is_py = os.path.basename(sys.argv[0]) == 'wrfinput.ju.py'
RUN_ID = int(sys.argv[1]) if is_py and len(sys.argv) > 1 else 5

root_dir = '/home/guc/'
data_dir = f'runs/{RUN_ID:03}*/'
root_data_dir = glob(root_dir + data_dir)[0]

all_files = glob(root_data_dir + 'wrfinput*')

# %%

def list_landuse(dataset: Dataset) -> None:
    attrs = dataset.__dict__
    print(f'Land use category (MMINLU), check with WRF/LANDUSE.TBL: {attrs['MMINLU']}')
    print(f'Land use category number (NUM_LAND_CAT): {attrs['NUM_LAND_CAT']}')
    print(f'Water type index (ISWATER): {attrs['ISWATER']}')
    print(f'Urban type index (ISWATER): {attrs['ISURBAN']}')

# show_lu()
# list_landuse()

# %%

import matplotlib.pyplot as plt
import math

def list_variables(dataset: Dataset) -> None:
    '''
    List all variables in the nc dataset for adjustment
    dataset:    netcdf dataset
    '''
    print('\n'.join(map(lambda x: f'{x.name}: {dataset[x.name].__dict__.get('description')} {x.dimensions}', dataset.variables.values())))

dataset = Dataset(all_files[0], format="NETCDF4")
# list_variables(dataset)

# %%

def plot_all_vars(dataset: Dataset) -> None:
    cols_num, len_vars = 10, len(dataset.variables)
    _, axes = plt.subplots(math.ceil(len_vars / cols_num), cols_num, figsize=(12, 26))
    idx: int = 0
    for var in dataset.variables.values():
        i, j = idx // cols_num, idx % cols_num
        axes[i][j].tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
        axes[i][j].set_title(var.name, x=0.5, y=0.35, fontweight="500", fontsize=6)
        if j != 0: axes[i][j].set_yticklabels([])
        if i != 0: axes[i][j].set_xticklabels([])
        if len(var.shape) == 3: axes[i][j].contourf(var[0], cmap='Spectral')
        elif len(var.shape) == 4: axes[i][j].contourf(var[0][0], cmap='Spectral')
        else: continue
        idx += 1

if not is_py:
    plot_all_vars(dataset)

# %%
import numpy as np

def modify_convert_uniform(src: Dataset, var_names: list[str]) -> Dataset:
    '''
    Convert all variables in the src file to uniform average
    src         source dataset
    var_names   list of variable names to average
    '''

    for var_name in var_names:
        print(f'Averaging {var_name}...', end='\r')
        modified_var, var_shape = src.variables[var_name][:], src.variables[var_name].shape
        if len(var_shape) == 3:
            for timestep in range(var_shape[0]):
                average_value = np.mean(src.variables[var_name][timestep])
                modified_var[timestep][:] = average_value
        elif len(var_shape) == 4:
            for timestep in range(var_shape[0]):
                for height in range(var_shape[1]):
                    average_value = np.mean(src.variables[var_name][timestep][height])
                    modified_var[timestep][height][:] = average_value

        src.variables[var_name][:] = modified_var

    return src

# %%
WATER_CUTOFF_IDX = 50

def modify_landuse(src: Dataset) -> Dataset:
    '''
    Modify the land use category
    src     source dataset
    '''
    water_cutoff_idx = WATER_CUTOFF_IDX

    attrs = src.__dict__
    land_use_cat = {
        'urban': attrs['ISURBAN'],          # Urban and Built-up Land
        'water': attrs['ISWATER'],          # Water Bodies
        'grassland': 10,                    # Grassland
    }

    # Modify the land use index. To check the variables,
    # see LANDUSE.TBL and num_land_cat in namelist.input
    # Currently using USGS (num_land_cat = 24)
    modified_lu = src.variables['LU_INDEX'][:]
    modified_lu[0][:, :water_cutoff_idx] = land_use_cat['water']
    modified_lu[0][:, water_cutoff_idx:] = land_use_cat['grassland']
    # modified_lu[0][40:60, 60:80] = land_use_cat['urban']
    src.variables['LU_INDEX'][:] = modified_lu

    # Modify land mask, 1 for land, 0 for water
    modified_landmask = src.variables['LANDMASK'][:]
    modified_landmask[0][:, :water_cutoff_idx] = 0 # Water
    modified_landmask[0][:, water_cutoff_idx:] = 1 # Land
    src.variables['LANDMASK'][:] = modified_landmask
    src.variables['XLAND'][:] = 2 - modified_landmask # Why are they making 2 vars with same function

    # Modify land use fraction
    # https://forum.mmm.ucar.edu/threads/difference-between-landusef-and-frc_urb2d.10455/
    # Basically you need to modify the fraction of land to the corresponding
    # array index
    modified_landusef = src.variables['LANDUSEF'][:]
    modified_landusef[:] = 0 # Reset everything, probably easier
    modified_landusef[0][land_use_cat['water']][:, :water_cutoff_idx] = 1.0
    modified_landusef[0][land_use_cat['grassland']][:, water_cutoff_idx:] = 1.0
    src.variables['LANDUSEF'][:] = modified_landusef

    return src

# %%

def modify_height(src: Dataset) -> Dataset:
    '''
    Modify terrain height of input file
    src     source dataset
    '''
    water_cutoff_idx = WATER_CUTOFF_IDX

    modified_height = src.variables['HGT'][:]
    modified_height[0][:, :water_cutoff_idx] = 0 # Water
    modified_height[0][:, water_cutoff_idx:] = 50 # Land
    # modified_height[0][40:60, 60:80] = 100
    src.variables['HGT'][:] = modified_height

    return src

# %%

def modify_water_depth(src: Dataset) -> Dataset:
    modified_water_depth = src.variables['WATER_DEPTH'][:]
    modified_water_depth[0][:, :] = -10.0
    src.variables['WATER_DEPTH'][:] = modified_water_depth

    return src

# %%

def modify_remove_initial_wind(src: Dataset) -> Dataset:
    src.variables['U'][:] = np.zeros(src.variables['U'].shape)
    src.variables['U10'][:] = np.zeros(src.variables['U10'].shape)

    src.variables['V'][:] = np.zeros(src.variables['V'].shape)
    src.variables['V10'][:] = np.zeros(src.variables['V10'].shape)

    src.variables['W'][:] = np.zeros(src.variables['W'].shape)

    return src

# %%
import os

file_name: str = 'wrfinput_d01'
output_name: str = root_dir + 'modified-files/wrfinput/no-coriolis/' + file_name

if len(glob(output_name)) > 0:
    os.remove(output_name)

with Dataset(all_files[0], 'r', format='NETCDF4') as src:
    with Dataset(output_name, 'w', format='NETCDF4') as out:
        # Get the attributes of the original file
        attributes = src.__dict__

        # Add extra field to attrs, e.g. notes
        attributes['TITLE'] += ' (MODIFIED)'
        attributes['NOTE'] = 'Idealized land-water split by Mok'

        # Set it into the output
        out.setncatts(attributes)

        # Copy dimensions
        for name, dimension in src.dimensions.items():
            dimension_size = (
                len(dimension) if not dimension.isunlimited() else None
            ) # The value should be None for unlimited dimension

            # Create the dimension with its size, make sure to modify it
            # if you changed the variable dimension
            out.createDimension(name, dimension_size)

        # Modify the variable, see function on the cell above

        for name, variable in src.variables.items():
            out.createVariable(
                name,
                variable.datatype,
                variable.dimensions,
                zlib = True,            # Lossless compression (optional)
                complevel = 5,          # Lossless compression (optional)
                shuffle = True          # Lossless compression (optional)
            )

            # Set output variable attributes
            out[name].setncatts(src[name].__dict__)
            out[name][:] = src[name][:]

        out = modify_water_depth(out)
        out = modify_remove_initial_wind(out)

        var_names = [ 'T', 'THM', 'MU', 'P', 'AL', 'P_HYD', 'Q2', 'T2', 'TH2',
            'PSFC', 'QVAPOR', 'TSLB', 'TMN', 'TSK', 'SST', 'VAR',
            'CON', 'VAR_SSO', 'OA1', 'OA2', 'OA3', 'OA4',
            'OL1', 'OL2', 'OL3', 'OL4',
        ]
        out = modify_convert_uniform(out, var_names)

    print('Done! Congrats 🎉')

# %%
import subprocess

if is_py:
    subprocess.call(['mv', output_name, all_files[0]])
else:
    # Test reading output file
    out_dataset = Dataset(output_name)
    plot_all_vars(out_dataset)
