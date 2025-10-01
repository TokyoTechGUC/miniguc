# %%

from netCDF4 import Dataset
from glob import glob
import sys, os

is_py = os.path.basename(sys.argv[0]) == 'wind-dir.ju.py'
RUN_ID = int(sys.argv[1]) if is_py and len(sys.argv) > 1 else 25

root_dir = '/home/guc/'
data_dir = f'runs/{RUN_ID:03}*/'
root_data_dir = glob(root_dir + data_dir)[0]

image_dir = root_data_dir + 'results/images/'
if len(glob(image_dir)) == 0:
    os.mkdir(image_dir)

# %%

import matplotlib.pyplot as plt
import cartopy.crs as crs
import numpy as np
import os

from wrf import getvar, to_np, extract_times, ALL_TIMES, latlon_coords, get_cartopy

plt.rcParams["font.family"] = "DejaVu Sans Mono"

def plot_image(dataset: Dataset, debug: bool = False) -> None:
    times = extract_times(dataset, timeidx=ALL_TIMES)
    if debug: times = times[90:91]
    for time_idx, datetime in enumerate(times):
        datetime_string = np.datetime_as_string(datetime, unit='m').replace('T', ' ')
        print(f"Saving {datetime_string}...", end='\r')

        u_data = getvar(dataset, "U10", time_idx)
        v_data = getvar(dataset, "V10", time_idx)
        var_data = np.sqrt(u_data**2 + v_data**2)
        # var_data = getvar(dataset, "T2", time_idx) - 273.15

        z_data = getvar(dataset, "z", time_idx)[0]
        cart_proj = get_cartopy(z_data)
        lats, lons = latlon_coords(z_data)

        # plot_lim = np.linspace(-10, 30, 21)
        plot_lim = np.linspace(0, 10, 21)

        mask = (slice(None, None, 6), slice(None, None, 6))

        plt.figure(figsize=(6, 6))
        ax = plt.axes(projection=cart_proj)
        plt.contourf(lons, lats, abs(to_np(var_data)), plot_lim, cmap="Spectral_r", transform=crs.PlateCarree(), extend="max")
        ax.quiver(
            to_np(lons)[mask],
            to_np(lats)[mask],
            to_np(u_data)[mask],
            to_np(v_data)[mask],
            transform=crs.PlateCarree(),
            scale=75,
            width=0.003
        )
        
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

        cbar = plt.colorbar(shrink=.8, ticks=plot_lim[::5])
        cbar.ax.set_ylabel('Wind Speed (m/s)')
        # cbar.ax.set_ylabel('Temperature (Celsius)')
        plt.title(f"Wind Speed (m/s) and Direction at 10 Meters\nReal Model Urban Grassland ideal condition at\n{datetime_string}")
        # plt.title(f"Temperature (Celsius) at 2 Meters, Real Model,\nGrassland ideal condition at\n{datetime_string}")

        if not debug:
            output_name = image_dir + np.datetime_as_string(datetime, unit='s') + '.png'
            plt.savefig(output_name)
            plt.clf()
            plt.close()

# %%

import subprocess
dataset = Dataset(glob(root_data_dir + 'wrfout*')[0])
print(f'Starting visualization for run {RUN_ID:03}')
plot_image(dataset, not is_py)

# Call ffmpeg to create video
if is_py:
    subprocess.call(['/home/guc/scripts/visualize/generate-video.sh', f'{RUN_ID:03}'])
    subprocess.call(['mv', 'out.mp4', root_dir + f'results/{RUN_ID:03}-{len(glob(root_dir + f'results/{RUN_ID:03}*.mp4')) + 1}.mp4'])
    for image_name in glob(image_dir + '*.png'):
        os.remove(image_name)
    print('Done!!')
