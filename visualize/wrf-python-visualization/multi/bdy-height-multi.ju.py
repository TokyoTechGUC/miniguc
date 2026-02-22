# %%

from netCDF4 import Dataset
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as crs
from wrf import get_cartopy, getvar, latlon_coords, to_np, extract_times, ALL_TIMES

Z0_VALUES = [0.5, 1, 2, 5, 10]
AHE_VALUES = [0, 10, 50, 100, 500, 1000]

# %%

template_dataset = Dataset(glob(f'/home/guc/runs/*ahe-100-z0-1/wrfout*')[0])
template_var = getvar(template_dataset, "PBLH", timeidx=0)
times = extract_times(template_dataset, timeidx=ALL_TIMES)

# %%

results = {}

# for z0 in Z0_VALUES:
for ahe in AHE_VALUES:
    # file_name = glob(f'/home/guc/runs/*-urban-grassland-ahe-100-z0-{z0}/wrfout*.backup')[0]
    file_name = glob(f'/home/guc/runs/*-urban-grassland-ahe-{ahe}-z0-1/wrfout*.backup')[0]
    dataset = Dataset(file_name)

    var_means = np.array([])

    for time_idx, datetime in enumerate(times):
        # print(f'Processing Z0={z0}, {datetime}', end='\r')
        print(f'Processing AHE={ahe}, {datetime}', end='\r')
        var_data = getvar(dataset, "PBLH", timeidx=time_idx)

        if time_idx == 0:
            var_means = np.abs(to_np(var_data))
            template_var = var_data
        else:
            var_means += np.abs(to_np(var_data))

    results[ahe] = var_means

# %%
plt.rcParams["font.family"] = "DejaVu Sans Mono"
plt.rcParams["font.size"] = 6

plot_lim = np.linspace(0, 2000, 21)

z_data = getvar(template_dataset, "z", timeidx=0)
lats, lons = latlon_coords(z_data)
cart_proj = get_cartopy(z_data)

column_size = 6

fig, axes = plt.subplots(1, column_size, figsize=(20, 3), subplot_kw={'projection': cart_proj})
# fig, axes = plt.subplots(1, column_size, figsize=(20, 4))

for idx, ahe in enumerate(AHE_VALUES):
    i, j = idx // column_size, idx % column_size

    var = results[ahe]
    gridlines = axes[j].gridlines(
        crs=crs.PlateCarree(),
        draw_labels=True,
        x_inline=False,
        y_inline=False,
        linewidth=0.1,
        color="black",
        linestyle="dotted",
    )
    gridlines.bottom_labels = None
    gridlines.right_labels = None

    if j != 0:
        gridlines.left_labels = None
    if i == 0:
        axes[j].set_xlabel('Coordinates')

    contour = axes[j].contourf(
        to_np(lons),
        to_np(lats),
        var / len(times),
        plot_lim,
        cmap="Spectral_r",
        extend='max',
        transform=crs.PlateCarree()
    )

    # axes[j].set_title(f'Z0 = {z0}')
    axes[j].set_title(f'AHE = {ahe}', y=-0.15)

    axes[j].grid(linewidth=0.1)

    if i == 0 and j == column_size - 1:
        fig.subplots_adjust(right=0.8)
        cbar_ax = fig.add_axes((0.825, 0.125, 0.01, 0.75))
        cbar = fig.colorbar(contour, cax=cbar_ax, ticks=plot_lim[::5])
        cbar.ax.set_ylabel('Height (m)')

fig.suptitle(f"Average Planetary Boundary Layer Height, Real Model, Urban Grassland ZO = 1")
# plt.savefig('/home/guc/results/pblh-z0-ahe-100.png')
plt.savefig('/home/guc/results/pblh-ahe-z0-1.png')

# %%

for z0 in Z0_VALUES:
    file_name = glob(f'/home/guc/runs/*-urban-grassland-ahe-500-z0-{z0}/wrfout*')[0]
    print(file_name)
