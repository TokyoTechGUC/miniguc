# %%

from netCDF4 import Dataset
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as crs
from wrf import get_cartopy, getvar, latlon_coords, to_np, extract_times, ALL_TIMES

Z0_VALUES = [0.5, 1, 2, 5, 10]
AHE_VALUES = [50, 100, 200]
threshold_datetime = np.datetime64('2025-03-10')

# %%

template_dataset = Dataset(glob(f'/home/guc/runs/*ahe-100-z0-10/wrfout*')[0])
template_var = getvar(template_dataset, "U10", timeidx=0)
times = extract_times(template_dataset, timeidx=ALL_TIMES)
times = times[times >= threshold_datetime]

# %%

results_u = {}
results_v = {}

for ahe in AHE_VALUES:
# for z0 in Z0_VALUES:
#     file_name = glob(f'/home/guc/runs/*-urban-grassland-ahe-100-z0-{z0}/wrfout*')[0]
    file_name = glob(f'/home/guc/runs/*-urban-grassland-ahe-{ahe}-rnd-wind/wrfout*')[0]
    dataset = Dataset(file_name)

    u_means = np.array([])
    v_means = np.array([])

    for time_idx, date_time in enumerate(times):
        # print(f'Processing Z0={z0}, {date_time}', end='\r')
        print(f'Processing AHE={ahe}, {date_time}', end='\r')
        u_data = getvar(dataset, "U10", timeidx=time_idx)
        v_data = getvar(dataset, "V10", timeidx=time_idx)

        if date_time == threshold_datetime:
            u_means = to_np(u_data)
            v_means = to_np(v_data)
            template_var = u_data
        else:
            u_means += to_np(u_data)
            v_means += to_np(v_data)

    results_u[ahe] = u_means
    results_v[ahe] = v_means

# %%
plt.rcParams["font.family"] = "DejaVu Sans Mono"
plt.rcParams["font.size"] = 6

plot_lim = np.linspace(0, 2.5, 21)

z_data = getvar(template_dataset, "z", timeidx=0)
lats, lons = latlon_coords(z_data)
cart_proj = get_cartopy(z_data)

column_size = 3

fig, axes = plt.subplots(1, column_size, figsize=(20, 4), subplot_kw={'projection': cart_proj})
# fig, axes = plt.subplots(1, column_size, figsize=(20, 4))

for idx, ahe in enumerate(AHE_VALUES):
# for idx, z0 in enumerate(Z0_VALUES):
    i, j = idx // column_size, idx % column_size

    u = results_u[ahe] / len(times)
    v = results_v[ahe] / len(times)

    u[u > 1000] = 0
    v[v > 1000] = 0
    var = np.sqrt(u**2 + v**2)

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

    contour = axes[j].contourf(
        to_np(lons),
        to_np(lats),
        var,
        plot_lim,
        cmap="Spectral_r",
        extend='max',
        transform=crs.PlateCarree()
    )

    mask = (slice(None, None, 6), slice(None, None, 6))

    # axes[j].set_title(f'Z0 = {z0}', y=-0.15)
    axes[j].set_title(f'AHE = {ahe}', y=-0.15)
    axes[j].quiver(
        to_np(lons)[mask],
        to_np(lats)[mask],
        to_np(u)[mask],
        to_np(v)[mask],
        transform=crs.PlateCarree(),
        scale=40,
        width=0.003
    )

    if i == 0 and j == column_size - 1:
        fig.subplots_adjust(right=0.8)
        cbar_ax = fig.add_axes((0.825, 0.125, 0.01, 0.75))
        cbar = fig.colorbar(contour, cax=cbar_ax, ticks=plot_lim[::5])
        # cbar.ax.set_ylabel('Height (m)')
        # cbar.ax.set_ylabel('Temperature (Celsius)')
        cbar.ax.set_ylabel('Wind Speed (m/s)')

fig.suptitle(f"Average U-direction Wind Speed at 10 Meters, Real Model, Urban Grassland, Z0 = 1")
# fig.suptitle(f"Average Temperature at 2 Meters, Real Model, Urban Grassland Z0 = 1")
# plt.savefig('/home/guc/results/wind-z0-ahe-100.png')
plt.savefig('/home/guc/results/wind-ahe-rnd-init-wind.png')

# %%

for z0 in Z0_VALUES:
    file_name = glob(f'/home/guc/runs/*-urban-grassland-ahe-500-z0-{z0}/wrfout*')[0]
    print(file_name)
