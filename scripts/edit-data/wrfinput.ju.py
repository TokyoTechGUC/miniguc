# %%

from netCDF4 import Dataset
from glob import glob
import sys, os

is_py = os.path.basename(sys.argv[0]) == 'wrfinput.ju.py'
RUN_ID = int(sys.argv[1]) if is_py and len(sys.argv) > 1 else 45

root_dir = '/home/mok/miniguc/'
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
list_variables(dataset)

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

def modify_random_initial_winds(src: Dataset) -> Dataset:
    dimensions_u = src.variables['U'].shape
    src.variables['U'][:] = (np.random.rand(*dimensions_u) * 0.2) - 0.1

    dimensions_v = src.variables['V'].shape
    src.variables['V'][:] = (np.random.rand(*dimensions_v) * 0.2) - 0.1

    return src

# %%

def modify_remove_sin_cos_alpha(src: Dataset) -> Dataset:
    src.variables['SINALPHA'][:] = 0
    src.variables['COSALPHA'][:] = 0
    src.variables['E'][:] = 0

    return src

# %%

def modify_reduce_vapor(src: Dataset) -> Dataset:
    src.variables['QVAPOR'][:] *= 0.01
    return src

# %%

def modify_urban_params(src: Dataset) -> Dataset:
    attrs = src.__dict__
    mask = src.variables['LU_INDEX'][0][:] == attrs['ISURBAN']
    urban_vars = {
        'BUILD_SURF_RATIO': 0.25,
        'BUILD_HEIGHT': 1,
        'STDH_URB2D': 0.5,
        'LF_URB2D': 0.25,
    }
    for name, value in urban_vars.items():
        if name == 'LF_URB2D':
            continue
        src.variables[name][0][mask] = value

    for i in range(3):
        src.variables['LF_URB2D'][0][i][mask] = urban_vars['LF_URB2D']
    return src

#%%

import os

file_name: str = 'wrfinput_d01'
output_name: str = root_dir + 'modified-files/' + file_name

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

        # out = modify_water_depth(out)
        out = modify_remove_initial_wind(out)
        # out = modify_random_initial_winds(out)
        out = modify_remove_sin_cos_alpha(out)
        # out = modify_reduce_vapor(out)
        out = modify_urban_params(out)

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
