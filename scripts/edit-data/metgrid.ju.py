# %%
from netCDF4 import Dataset
from glob import glob
import sys, os

is_py = os.path.basename(sys.argv[0]) == 'metgrid.ju.py'

root_dir = '/home/guc/'
all_files = glob(root_dir + 'Build_WRF/WPS/met_em*')
# all_files = glob(root_dir + 'runs/016*/met_em*')

# %%

dataset = Dataset(all_files[1])
# print('\n'.join(map(lambda x: f'{x.name}: {dataset[x.name].__dict__.get('description')} {x.dimensions}', dataset.variables.values())))

# %%
import matplotlib.pyplot as plt
import math

def plot_all_vars(dataset: Dataset) -> None:
    cols_num, len_vars = 10, len(dataset.variables)
    _, axes = plt.subplots(math.ceil(len_vars / cols_num), cols_num, figsize=(12, 12))
    idx: int = 0
    for var in dataset.variables.values():
        i, j = idx // cols_num, idx % cols_num
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

def modify_convert_uniform_land(src: Dataset, var_names: list[str]) -> Dataset:
    '''
    Convert all variables in the src file to uniform average only on land
    src         source dataset
    var_names   list of variable names to average
    '''
    mask_array = src.variables['LANDMASK'][0][:] == 1

    for var_name in var_names:
        print(f'Averaging {var_name}...', end='\r')
        modified_var, var_shape = src.variables[var_name][:], src.variables[var_name].shape
        if len(var_shape) == 3:
            for timestep in range(var_shape[0]):
                average_value = np.mean(src.variables[var_name][timestep][mask_array])
                modified_var[timestep][mask_array] = average_value
        elif len(var_shape) == 4:
            for timestep in range(var_shape[0]):
                for height in range(var_shape[1]):
                    average_value = np.mean(src.variables[var_name][timestep][height][mask_array])
                    modified_var[timestep][height][mask_array] = average_value

        src.variables[var_name][:] = modified_var

    return src

# %%

def modify_file(input_name: str, output_name: str) -> None:
    with Dataset(input_name, 'r', format='NETCDF4') as src:
        with Dataset(output_name, 'w', format='NETCDF4') as out:
            # Get the attributes of the original file
            attributes = src.__dict__

            # Add extra field to attrs, e.g. notes
            attributes['TITLE'] += ' (MODIFIED)'
            attributes['NOTE'] = 'Idealized Urban grassland by Mok'

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

            # landsea?
            var_names = ['PRES', 'GHT', 'HGTTROP', 'TTROP', 'PTROPNN', 'PTROP', 'VTROP', 'UTROP', 'HGTMAXW', 'TMAXW',
                         'PMAXWNN', 'PMAXW', 'VMAXW', 'UMAXW', 'SKINTEMP', 'SOILHGT', 'PSFC', 'RH', 'VV', 'UU', 'TT',
                         'PMSL', 'VAR_SSO', 'OL4', 'OL3', 'OL2', 'OL1', 'OA4', 'OA3', 'OA2', 'OA1', 'VAR', 'CON']
            out = modify_convert_uniform(out, var_names)

            var_names_land = ['SM', 'ST', 'ST100200', 'ST040100', 'ST010040', 'ST000010',
                              'SM100200', 'SM040100', 'SM010040', 'SM000010', 'SNOW', 'SNOWH']
            out = modify_convert_uniform_land(out, var_names_land)
            out.variables['LANDSEA'][:] = src.variables['LANDMASK'][:]

        print('Done! Congrats 🎉', end='\r')

# %%

import os
import subprocess

output_names = []

for input_name in all_files:
    print(f'Modifying {input_name}', end='\r')
    file_name: str = os.path.basename(input_name)
    output_name: str = root_dir + 'modified-files/' + file_name
    if len(glob(output_name)) > 0: os.remove(output_name)
    modify_file(input_name, output_name)
    output_names.append(output_name)

# %%

# Replace the destination file
if is_py:
    for i in range(len(all_files)):
        subprocess.call(['mv', output_names[i], all_files[i]])
else:
    # Test reading output file
    out_dataset = Dataset(output_names[0])
    plot_all_vars(out_dataset)
