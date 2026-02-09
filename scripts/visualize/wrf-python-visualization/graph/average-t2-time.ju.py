
# %%

from netCDF4 import Dataset
from glob import glob
import numpy as np

from wrf import getvar, ALL_TIMES, extract_times

# %%

import matplotlib.pyplot as plt

RUN_IDS = [57, 59, 69]

# BUILD_AREA_FRACTION   BUILDING PLAN AREA DENSITY 
# BUILD_SURF_RATIO      BUILDING SURFACE AREA TO PLAN AREA RATIO
# BUILD_HEIGHT          AVERAGE BUILDING HEIGHT WEIGHTED BY BUILDING PLAN AREA
# MH_URB2D              Mean Building Height
# STDH_URB2D            Standard Deviation of Building Height
# LF_URB2D              Frontal Area Index
# Z0_URB2D              Roughness length for momentum
# LF_URB2D_S            Frontal area index
# AHE                   Anthropogenic heat emission

DEPENDENT_VAR = 'Z0_URB2D'
rural_land_type = 'forest'

plt.rcParams['font.size'] = 14
plt.rcParams['font.family'] = 'DejaVu Sans Mono'
# plt.subplots_adjust(wspace=0.7)

import matplotlib.dates as mdates

times = [] 

ANALYZE_VARS = ['T2', 'SPEED10', 'PBLH', 'CLDFRA', 'QRAIN']
fig, axes = plt.subplots(len(ANALYZE_VARS), 1, figsize=(12, 11), sharex=True)

for i, run_id in enumerate(RUN_IDS):
    file_name = glob(f'/home/guc/runs/{run_id:03}-*/wrfout*')[0]
    dataset = Dataset(file_name)

    if len(times) == 0:
        times = extract_times(dataset, timeidx=ALL_TIMES)

    for j, var_name in enumerate(ANALYZE_VARS):
        if var_name == 'SPEED10':
            u10 = getvar(dataset, 'U10', timeidx=ALL_TIMES)
            v10 = getvar(dataset, 'V10', timeidx=ALL_TIMES)
            var_values = np.sqrt(u10**2 + v10**2)
        else: 
            var_values = getvar(dataset, var_name, timeidx=ALL_TIMES)

        if (len(var_values.shape) <= 3):
            mean_var_values = np.mean(var_values, axis=(1, 2))
        else:
            mean_var_values = np.mean(var_values, axis=(1, 2, 3))

        axes[j].plot(times, mean_var_values, label=f"ID={run_id}")
        axes[j].legend()
        axes[j].grid()
        axes[j].set_xlabel('Time')
        axes[j].xaxis.set_major_formatter(mdates.DateFormatter('%b %d-%H:%M'))
        axes[j].set_xticks(times[::len(times)//4])
        axes[j].set_ylabel(var_name)
        axes[j].set_xlim(times[0], times[-1])

# axes[0][0].set_title('Time Series of Mean Temperature vs. AHE Value')
# axes[0][1].set_title('Time Series of Mean Temperature in Urban Area vs. AHE Value')
#
# axes[1][0].set_title('Time Series of Max Temperature vs. AHE Value')
# axes[1][1].set_title('Time Series of Max Temperature in Urban Area vs. AHE Value')

fig.suptitle('Time Series of Mean Variables Value on Different Rural Landuse')

# plt.savefig('/home/guc/results/mean-vars-diff-landuse.png')
