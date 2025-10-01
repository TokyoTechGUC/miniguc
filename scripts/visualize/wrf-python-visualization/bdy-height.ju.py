# %%

from netCDF4 import Dataset
from glob import glob
import sys, os

is_py = os.path.basename(sys.argv[0]) == 'bdy-height.ju.py'
RUN_ID = int(sys.argv[1]) if is_py and len(sys.argv) > 1 else 15

root_dir = '/home/guc/'
data_dir = f'runs/{RUN_ID:03}*/'
root_data_dir = glob(root_dir + data_dir)[0]

image_dir = root_data_dir + 'results/images/'
if len(glob(image_dir)) == 0:
    os.mkdir(image_dir)

# %%

def list_variables(dataset: Dataset) -> None:
    '''
    List all variables in the nc dataset for adjustment
    dataset:    netcdf dataset
    '''
    print('\n'.join(map(lambda x: f"{x.name}: {dataset[x.name].__dict__.get('description')} {x.dimensions}", dataset.variables.values())))

# %%

import matplotlib.pyplot as plt
import cartopy.crs as crs
import numpy as np
import os

from wrf import getvar, to_np, extract_times, ALL_TIMES, latlon_coords, get_cartopy

plt.rcParams["font.family"] = "DejaVu Sans Mono"

def plot_image(dataset: Dataset, debug: bool = False, has_latlon: bool = True) -> None:
    times = extract_times(dataset, timeidx=ALL_TIMES)
    if debug: times = times[120:130]
    for time_idx, datetime in enumerate(times):
        datetime_string = np.datetime_as_string(datetime, unit='m').replace('T', ' ')
        print(f"Saving {datetime_string}...", end='\r')

        var_data = getvar(dataset, "PBLH", time_idx)

        z_data = getvar(dataset, "z", time_idx)[0]
        cart_proj = get_cartopy(z_data)

        plot_lim = np.linspace(0, 8000, 21)

        if has_latlon:
            lats, lons = latlon_coords(z_data)
            plt.figure(figsize=(6, 6)) # WIDTH, HEIGHT
            ax = plt.axes(projection=cart_proj)
            gridlines = ax.gridlines(
                crs=crs.PlateCarree(),
                draw_labels=True,
                x_inline=False,
                y_inline=False,
                linewidth=0.1,
                color="black",
                linestyle="dotted",
            )
            gridlines.top_labels = None
            gridlines.right_labels = None
        else:
            lons = np.arange(0, var_data.shape[0])
            lats = np.arange(0, var_data.shape[1])
            plt.figure(figsize=(7, 6)) # WIDTH, HEIGHT

        plt.contourf(lons, lats, to_np(var_data), plot_lim, cmap="Spectral_r",
                     transform=crs.PlateCarree() if has_latlon else None)

        cbar = plt.colorbar(shrink=.9, ticks=plot_lim[::5], extend="max")
        cbar.ax.set_ylabel('Boundary Layer Height (m)')
        plt.title(f"Boundary Layer Height, Real Model,\nNo Coriolis Urban Grassland ideal condition at\n{datetime_string}")

        if not debug:
            output_name = image_dir + np.datetime_as_string(datetime, unit='s') + '.png'
            plt.savefig(output_name)
            plt.clf()
            plt.close()

# %%

import subprocess
dataset = Dataset(glob(root_data_dir + 'wrfout*')[0])
print(f'Starting visualization for run {RUN_ID:03}')
plot_image(dataset, not is_py, True)

# Call ffmpeg to create video
if is_py:
    subprocess.call(['/home/guc/scripts/visualize/generate-video.sh', f'{RUN_ID:03}'])
    subprocess.call(['mv', 'out.mp4', root_dir + f'results/{RUN_ID:03}-{len(glob(root_dir + f'results/{RUN_ID:03}*.mp4')) + 1}.mp4'])
    for image_name in glob(image_dir + '*.png'):
        os.remove(image_name)
    print('Done!!')
