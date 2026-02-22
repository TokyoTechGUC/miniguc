from netCDF4 import Dataset
import matplotlib.pyplot as plt
from glob import glob
import os

#|%%--%%| <qRvm3W7rtE|ANDsNHSABv>

# Change these values for different dirs
root_dir = "../../../results/"
model_dir = "no-coriolis"

#|%%--%%| <ANDsNHSABv|twUyPhcMZb>

all_files = sorted(glob(root_dir + model_dir + '/open/*'))
for i, fname in enumerate(all_files):
    all_files[i] = os.path.basename(fname)

#|%%--%%| <twUyPhcMZb|ilxS9sm3AN>

def save_image(image_data, fname, save_dir, title, clim = (-10, 10)):
    plt.imshow(image_data, cmap='rainbow')
    plt.clim(clim)
    plt.colorbar()

    date, time = fname.split('_')[-2:]

    plt.title(f'{title} at\n {date + '_' + time}')
    plt.xlabel('x')
    plt.ylabel('y')

    plt.savefig(save_dir + fname)
    plt.clf()

#|%%--%%| <ilxS9sm3AN|R0hfTFSjVZ>

def save_images(files, get_data, save_dir, title, clim = (-10, 10)):
    for fpath in files:
        dataset = Dataset(fpath)
        dataset_values = get_data(dataset)
        save_image(
            dataset_values,
            os.path.basename(fpath),
            save_dir,
            title,
            clim
        )

#|%%--%%| <R0hfTFSjVZ|bJj3ANs6zU>

def save_images_compare(files_1, files_2, get_data, save_dir, title, clim = (-10, 10)):
    if (len(files_1) != len(files_2)):
        raise ValueError('files_1 length does not match with files_2')

    for i in range(len(files_1)):
        fpath_1 = files_1[i]
        fpath_2 = files_2[i]

        dataset_1 = Dataset(fpath_1)
        dataset_2 = Dataset(fpath_2)

        dataset_1_values = get_data(dataset_1)
        dataset_2_values = get_data(dataset_2)

        diffs = dataset_1_values - dataset_2_values
        save_image(
            diffs,
            os.path.basename(fpath_1),
            save_dir,
            title,
            clim
        )

#|%%--%%| <bJj3ANs6zU|XncwnilMaf>

default_results = glob(root_dir + 'default/periodic/*')
no_coriolis_results = glob(root_dir + 'no-coriolis/periodic/*')

save_dir_new = root_dir + 'default/images/default-no-coriolis/'

def get_data(data):
    return data['U'][0][0][:]

# save_images(
#     no_coriolis_results,
#     get_data,
#     save_dir_new,
#     'Surface X-wind, No-Coriolis Real Model',
#     (-20, 20)
# )

save_images_compare(
    default_results,
    no_coriolis_results,
    get_data,
    save_dir_new,
    'Surface X-wind Difference, Default - No-Coriolis Real Model',
    (-0.2, 0.2)
)

#|%%--%%| <XncwnilMaf|VUVW1yY1Au>

import numpy as np

def plot_mean():
    means = []
    labels = []

    for fname in all_files[:-1]:
        open_filepath = root_dir + model_dir + '/open/' + fname
        open_dataset = Dataset(open_filepath)
        mean_value = np.mean(open_dataset['U'][0][0][:])
        mean_label = os.path.basename(fname).split('_')[-1]

        means.append(mean_value)
        labels.append(mean_label)

    plt.title('Mean Wind Speed (x-direction) on Surface, No Coriolis')
    plt.ylabel('U avg')
    plt.xlabel('time')
    plt.grid()
    plt.xticks(np.arange(0, len(all_files), 60))
    plt.plot(labels, means)
    plt.savefig('result-graph.png')

