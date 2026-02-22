# %%

from netCDF4 import Dataset
from glob import glob
import numpy as np

root_dir: str = '/home/guc/'
# model_dir: str = 'Build_WRF/models/real/run/'
model_dir: str = 'runs/001-seabreeze/'

all_files = glob(root_dir + model_dir + 'wrfout*')
print(all_files)

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

# A function to list all the variables in this file
list_variables(dataset)

# %%
import math

VAR_INDEX = 5

def plot_all_vars(dataset: Dataset) -> None:
    global VAR_INDEX
    print(f'Displaying frame {VAR_INDEX} of {dataset.variables['XLAT'].shape[0]} (1-index)')
    cols_num, len_vars = 10, len(dataset.variables)
    _, axes = plt.subplots(math.ceil(len_vars / cols_num), cols_num, figsize=(10, 24))
    idx: int = 0
    for var in dataset.variables.values():
        i, j = idx // cols_num, idx % cols_num
        axes[i][j].set_title(var.name, x=0.5, y=0.35, fontweight="500", fontsize=6)
        if j != 0: axes[i][j].set_yticklabels([])
        if i != 0: axes[i][j].set_xticklabels([])
        if len(var.shape) == 3: axes[i][j].contourf(var[VAR_INDEX - 1], cmap='Spectral')
        elif len(var.shape) == 4: axes[i][j].contourf(var[VAR_INDEX - 1][0], cmap='Spectral')
        else: continue
        idx += 1

plot_all_vars(dataset)

# %%
