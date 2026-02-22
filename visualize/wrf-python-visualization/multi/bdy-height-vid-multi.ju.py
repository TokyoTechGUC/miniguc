# %%

from netCDF4 import Dataset
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as crs
from wrf import get_cartopy, getvar, latlon_coords, to_np, extract_times, ALL_TIMES
import os, sys

is_py = os.path.basename(sys.argv[0]) == 'bdy-height-vid-multi.ju.py'
RUN_IDS = [51, 52, 53, 54, 55, 56]

root_dir = '/home/guc/'
data_dir = 'tmp/'
image_dir = glob(root_dir + data_dir)[0]

template_dataset = Dataset(glob(f'/home/guc/runs/*ahe-100-rnd-wind/wrfout*')[0])
template_var = getvar(template_dataset, "PBLH", timeidx=0)
column_size = len(RUN_IDS)

# %%

def plot_image(debug: bool = False) -> None:
    times = extract_times(template_dataset, timeidx=ALL_TIMES)

    z_data = getvar(template_dataset, "z", timeidx=0)
    lats, lons = latlon_coords(z_data)
    cart_proj = get_cartopy(z_data)
    plot_lim = np.linspace(0, 3000, 21)
    
    if debug: times = times[120:121]

    for time_idx, datetime in enumerate(times):
        fig, axes = plt.subplots(1, column_size, figsize=(20, 3), subplot_kw={'projection': cart_proj})
        for i, run_id in enumerate(RUN_IDS):
            print(f'Processing RUN_ID={run_id}, {datetime}', end='\r')

            file_name = glob(f'/home/guc/runs/0{run_id}*/wrfout*')[0]

            dataset = Dataset(file_name)

            var_data = getvar(dataset, "PBLH", timeidx=time_idx)

            gridlines = axes[i].gridlines(
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

            plt.contourf(lons, lats, to_np(var_data), plot_lim, cmap="Spectral_r", transform=crs.PlateCarree())

            contour = axes[i].contourf(
                to_np(lons),
                to_np(lats),
                var_data,
                plot_lim,
                cmap="Spectral_r",
                extend='max',
                transform=crs.PlateCarree()
            )

            axes[i].set_title(f'ID = {run_id}', y=-0.15)

            axes[i].grid(linewidth=0.1)

            if i == column_size - 1:
                fig.subplots_adjust(right=0.8)
                cbar_ax = fig.add_axes((0.825, 0.125, 0.01, 0.75))
                cbar = fig.colorbar(contour, cax=cbar_ax, ticks=plot_lim[::5])
                cbar.ax.set_ylabel('Height (m)')

        if not debug:
            output_name = image_dir + np.datetime_as_string(datetime, unit='s') + '.png'
            plt.savefig(output_name)
            plt.clf()
            plt.close()

# %%
plt.rcParams["font.family"] = "DejaVu Sans Mono"
plt.rcParams["font.size"] = 6

import subprocess
print(f'Starting visualization for bdy-height-vid-multi')
plot_image(not is_py)

# Call ffmpeg to create video
if is_py:
    subprocess.call(['/home/guc/scripts/visualize/tmp-generate-video.sh'])
    subprocess.call(['mv', 'out.mp4', root_dir + f'results/bdy-height-multi-{len(glob(root_dir + f'results/bdy-height-multi*.mp4')) + 1}.mp4'])
    for image_name in glob(image_dir + '*.png'):
        os.remove(image_name)
    print('Done!!')
