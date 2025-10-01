# %%

from netCDF4 import Dataset
from glob import glob

file_names = glob('/home/guc/runs/051-*/wrfout*')
dataset = Dataset(file_names[0])

print(dataset.variables['LU_INDEX'][0][:])

# %%

