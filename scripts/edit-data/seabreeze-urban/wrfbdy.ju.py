

# %%

from netCDF4 import Dataset
from glob import glob
import numpy as np
import sys, os

is_py = os.path.basename(sys.argv[0]) == 'wrfbdy.ju.py'
RUN_ID = int(sys.argv[1]) if is_py and len(sys.argv) > 1 else 5

root_dir = '/home/guc/'
data_dir = f'runs/{RUN_ID:03}*/'
root_data_dir = glob(root_dir + data_dir)[0]

all_files = glob(root_data_dir + 'wrfbdy*')

# %%
import matplotlib.pyplot as plt

def list_variables(dataset: Dataset) -> None:
    '''
    List all variables in the nc dataset for adjustment
    dataset:    netcdf dataset
    '''
    print('\n'.join(map(lambda x: f'{x.name}: {dataset[x.name].__dict__.get('description')} {x.dimensions} {x.shape}', dataset.variables.values())))

# Check the values in the selected wrfbdy file
dataset = Dataset(all_files[0])

# You can look at the attributes of the file in dictionary
# format this way. Call dataset.ncattrs if you want all attribute
# print(dataset.__dict__) 

# A function to list all the variables in this file
# list_variables(dataset)

# print(dataset.variables['U_BXS'][0][0])
# print(dataset.variables['U_BXS'].dimensions)
# plt.imshow(dataset.variables['U_BXS'][0][0], cmap='rainbow')

# %%
import math

def plot_all_vars(dataset: Dataset) -> None:
    cols_num, len_vars = 10, len(dataset.variables)
    _, axes = plt.subplots(math.ceil(len_vars / cols_num), cols_num, figsize=(12, 18))
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

def modify_average_z_layers(src: Dataset, var_names: list[str]) -> Dataset:
    '''
    A function to average all variables in each Z-layer
    src:    A read file pointer to source/input file
    '''
    for var_name in var_names:
        print(f'Processing variable {var_name}...', end='\r')
        # Ideally we want to use recursive, but now the size is fixed
        # so it's fine

        # I can't assign the value directly to out for some reason
        # so I make a temporary variable
        modified_out = src.variables[var_name][:]
        var_shape = src.variables[var_name].shape
        for time_idx in range(var_shape[0]):
            for bdy_width_idx in range(var_shape[1]):
                for bottom_top_idx in range(var_shape[2]):
                    mean_val_in_z_level = np.mean(src.variables[name][time_idx][bdy_width_idx][bottom_top_idx])
                    modified_out[time_idx][bdy_width_idx][bottom_top_idx][:] = mean_val_in_z_level
        src.variables[var_name][:] = modified_out

    return src

# %%

def modify_remove_wind(src: Dataset) -> Dataset:
    '''
    A function to remove boundary condition wind
    src:    A read file pointer to source/input file
    '''
    for var_name in src.variables.keys():
        if (var_name.split('_')[0] in ['U', 'V', 'W']):
            src.variables[var_name][:] = 0.0
    return src

# %%
import os
file_name: str = 'wrfbdy_d01'
output_name: str = root_dir + 'modified-files/wrfbdy/no-coriolis/' + file_name

if len(glob(output_name)) > 0:
    os.remove(output_name)

# Three things need to be set: attributes, dimensions, and variables
# What we want to modify here is the variables
with Dataset(all_files[0], 'r', format='NETCDF4') as src:
    with Dataset(output_name, 'w', format='NETCDF4') as out:
        # Get the attributes of the original file
        attributes = src.__dict__

        # Add extra field to attrs, e.g. notes
        attributes['TITLE'] += ' (MODIFIED)'
        attributes['NOTE'] = 'Average Top-bottom direction by Mok'

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

        # Modify the variable, see function on the cell above
        var_names = []
        for var_name in src.variables.keys():
            initial = var_name.split('_')[0]
            if initial in ['PH', 'T', 'QVAPOR']:
                var_names.append(var_name)
        # out = modify_average_z_layers(out, var_names)
        out = modify_remove_wind(out)

    print('Done! Congrats 🎉')

# %%
import subprocess

# Test reading output file
if is_py:
    subprocess.call(['mv', output_name, all_files[0]])
else:
    out_dataset = Dataset(output_name)
    plot_all_vars(out_dataset)
