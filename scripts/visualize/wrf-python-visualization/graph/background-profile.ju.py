# %% [md]
"""
### Scenario Background Profile Plotter
A python script to visualize the background profile of the created scenario, taken from `wrfinput` file
#### How to Use
* A

"""

# %%

from netCDF4 import Dataset
from glob import glob
import numpy as np
from wrf import getvar, ALL_TIMES, extract_times
import math

# %%

import matplotlib.pyplot as plt
from time import time

RUN_ID = {
    'tokyo':    88,
    'cairo':    86,
}
rural_land_type = 'barren'

plt.rcParams['font.size'] = 18
plt.rcParams['font.family'] = 'DejaVu Sans Mono'

file_name = glob(f'/home/mok/miniguc/runs/{RUN_ID['tokyo']:03}-*/wrfinput*')[0]
dummy_dataset: Dataset = Dataset(file_name)

# Print variables
print('Variable names:')
for x in dummy_dataset.variables.values():
    unit = dummy_dataset.variables[x.name].__dict__.get('units')
    print(f'{x.name}: {dummy_dataset.variables[x.name].__dict__.get('description')} ({unit})')

# %%

times = []

ANALYZE_VARS = ['T', 'SPEED', 'QVAPOR']
fig, axes = plt.subplots(1, len(ANALYZE_VARS), figsize=(9, 3), sharey='row')

custom_var_unit = {
    'SPEED': 'm/s',
    'T': 'C',
    'QVAPOR': '',
}

custom_var_name = {
    'SPEED': 'Wind Speed',
    'T': 'Potential\nTemperature',
    'W': 'Vertical Wind Speed',
    'QVAPOR': 'Water Vapor\n Mixing Ratio',
}

for i, var_name in enumerate(ANALYZE_VARS):
    print(f'Processing {var_name} of {rural_land_type}...' + (' ' * 40), end='\r')
    mean_var_values = []
    mean_var_values_urban = []
    mean_var_values_rural = []

    wrfinput_name = glob(f'/home/mok/miniguc/runs/{RUN_ID['cairo']:03}-*/wrfinput*')[0]
    wrfinput = Dataset(wrfinput_name)

    if var_name == 'SPEED':
        u_values = getvar(wrfinput, 'U', timeidx=ALL_TIMES)
        mean_u_values = np.mean(u_values, axis=(1, 2))

        v_values = getvar(wrfinput, 'V', timeidx=ALL_TIMES)
        mean_v_values = np.mean(v_values, axis=(1, 2))

        mean_var_values = np.sqrt(mean_u_values**2 + mean_v_values**2)
    else:
        var_values = getvar(wrfinput, var_name, timeidx=ALL_TIMES)
        mean_var_values = np.mean(var_values, axis=(1, 2))

    z_values = getvar(wrfinput, 'z', timeidx=ALL_TIMES)
    mean_z_values = np.mean(z_values, axis=(1, 2))

    axes[i].plot(mean_var_values[:len(mean_z_values)], mean_z_values, '-', color='red', mfc='white', linewidth=2)
    axes[i].set_ylim(0, 20000)
    axes[i].spines['top'].set_visible(False)
    axes[i].spines['right'].set_visible(False)

    var_unit = wrfinput.variables[var_name].units if not var_name in custom_var_unit else custom_var_unit[var_name]
    axes[i].set_xlabel(f'{var_name if not var_name in custom_var_name else custom_var_name[var_name]} ({var_unit})', { 'size': 14 })

axes[0].set_ylabel(f'Height (m)')
fig.suptitle(f'Plot of Variables Background Profile, Cairo')

plt.savefig(f'/home/mok/miniguc/results/var-comparison/loc-var-profile-cairo.png', bbox_inches="tight")
