# %%

from netCDF4 import Dataset
from glob import glob

# %%

root_dir = '/home/guc/results/'
data_dir = 'no-coriolis/images/ideal-draft-2/'

all_files = glob(root_dir + data_dir + '*')

# %%

import matplotlib.pyplot as plt
import cartopy.crs as crs
import numpy as np
import os

from wrf import CoordPair, getvar, latlon_coords, get_cartopy, to_np, cartopy_xlim, cartopy_ylim, destagger

plt.rcParams["font.family"] = "DejaVu Sans Mono"

def get_data(file_name):
    dataset = Dataset(file_name)
    u_data = getvar(dataset, "tc")[0]
    z_data = getvar(dataset, "z")[0]
    return u_data, z_data

def plot_image(file_name):
    u_data, z_data = get_data(file_name)
    date, time = os.path.basename(file_name).split('_')[-2:]
    
    cart_proj = get_cartopy(z_data)
    lats, lons = latlon_coords(z_data)
    
    fig = plt.figure(figsize=(6, 6))
    ax = plt.axes(projection=cart_proj)

    plot_lim = np.linspace(-7, 28, 21)
    
    plt.contour(to_np(lons), to_np(lats), to_np(z_data), colors="black", linewidths=0.5, transform=crs.PlateCarree())
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

    plt.colorbar(shrink=.9, ticks=plot_lim[::4])
    # plt.colorbar()
    plt.title(f"Temperature (Celsius) at Surface, Real Model,\nNo Coriolis Avg by Height at\n{date + ' ' + time}")

# %%

from wrf import vertcross

def plot_cross_section(file_name):
    dataset = Dataset(file_name)
    t_data = getvar(dataset, "tc")
    z_data = getvar(dataset, "z")

    date, time = os.path.basename(file_name).split('_')[-2:]

    start_point = CoordPair(lat = 30, lon = -80)
    end_point = CoordPair(lat = 30, lon = -75)

    t_cross = vertcross(
        t_data,
        z_data,
        wrfin=dataset,
        start_point=start_point,
        end_point=end_point,
        latlon=True,
        meta=True
    )

    coord_pairs = to_np(t_cross.coords['xy_loc'])

    fig = plt.figure(figsize=(6, 6))
    ax = plt.axes()

    ax.set_xticks(np.arange(coord_pairs.shape[0])[::20])
    ax.set_xticklabels([pair.latlon_str() for pair in to_np(coord_pairs)][::20], rotation=45)
    ax.set_xlabel('(Latitude, Longitude)')
    ax.set_ylabel('Height (m)')

    ax.set_ylim(0, 100)

    plot_lim = np.arange(-100, 25 + 1, 5)

    plt.contourf(to_np(t_cross), plot_lim, cmap="rainbow")
    plt.colorbar(shrink=.9, ticks=plot_lim[::5])
    plt.title(f"Temperature Cross Section (Celsius), Real Model\nNo Coriolis Avg by Height at\n {date + ' ' + time}")
# %%

for fname in all_files[:5]:
    plot_image(fname)
    # plot_cross_section(fname)
    new_name = root_dir + 'no-coriolis/images/average-by-h-vert/' + ('_'.join(os.path.basename(fname).split('_')[-2:])) + '.png'
    # print(f'Saving {new_name}...', end="\r")
    plt.show()
    # plt.clf()
    plt.savefig(new_name)
    plt.close()
print('Done!!!\n')
