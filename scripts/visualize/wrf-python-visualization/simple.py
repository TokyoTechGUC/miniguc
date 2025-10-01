
from netCDF4 import Dataset
from glob import glob

# |%%--%%| <NYpki1Lsdz|LiDSxxpCxE>

root_dir = '/home/guc/results/'
data_dir = 'default/periodic/'

all_files = glob(root_dir + data_dir + '*')

# |%%--%%| <LiDSxxpCxE|B8w2NYfYkp>

import matplotlib.pyplot as plt
import cartopy.crs as crs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import numpy as np
import os

from wrf import getvar, latlon_coords, get_cartopy, to_np, cartopy_xlim, cartopy_ylim, destagger

import matplotlib.ticker as mticker

plt.rcParams["font.family"] = "DejaVu Sans Mono"

def get_data(file_name):
    dataset = Dataset(file_name)
    u_data = destagger(getvar(dataset, "U"), stagger_dim=2)[0]
    z_data = getvar(dataset, "z")[0]
    return u_data, z_data

def plot_image(file_name):
    u_data, z_data = get_data(file_name)
    date, time = os.path.basename(file_name).split('_')[-2:]
    
    cart_proj = get_cartopy(z_data)
    lats, lons = latlon_coords(z_data)
    
    fig = plt.figure(figsize=(6, 6))
    ax = plt.axes(projection=cart_proj)

    plot_lim = np.linspace(-10, 20, 16)
    
    plt.contour(to_np(lons), to_np(lats), to_np(z_data), plot_lim, colors="black", linewidths=0.5, transform=crs.PlateCarree())
    plt.contourf(to_np(lons), to_np(lats), to_np(u_data), plot_lim, cmap="rainbow", transform=crs.PlateCarree())
    
    ax.set_xlim(cartopy_xlim(z_data))
    ax.set_ylim(cartopy_ylim(z_data))
    
    # gridlines coordinate labels setup
    # https://medium.com/the-barometer/plotting-wrf-data-using-python-wrf-python-and-cartopy-edition-b7bf45ff46bb
    gridlines = ax.gridlines(
        crs=crs.PlateCarree(),
        draw_labels=True,
        x_inline=False,
        y_inline=False,
        color="black",
        linestyle="dotted"
    )
    gridlines.top_labels = None
    gridlines.right_labels = None

    plt.colorbar(shrink=.9, ticks=plot_lim[::3])
    plt.title(f"Wind Speed (X-direction), Real Model at\n {date + ' ' + time}")

# |%%--%%| <B8w2NYfYkp|Ab3KFLJcvZ>

for fname in all_files:
    plot_image(fname)
    new_name = root_dir + 'default/images/periodic-wrf-python/' + ('_'.join(os.path.basename(fname).split('_')[-2:])) + '.png'
    print(f'Saving {new_name}...', end="\r")
    # plt.show()
    plt.savefig(new_name)
    plt.clf()
    # plt.close()
