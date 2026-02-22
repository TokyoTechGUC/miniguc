from netCDF4 import Dataset
import matplotlib.pyplot as plt
from glob import glob

root_dir = "/home/guc/Build_WRF/models/seabreeze2d/test/em_seabreeze2d_x"
all_files = glob(f'{root_dir}/wrfout_*')

file_index = -1
print(f'Opening {all_files[file_index]}')
nc = Dataset(all_files[file_index])
t2_data = nc['T2'][0]

plt.imshow(t2_data)
plt.show()
# plt.savefig('result.png')


