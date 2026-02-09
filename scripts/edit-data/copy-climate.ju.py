# %%

from netCDF4 import Dataset
from glob import glob
import sys, os

is_py = os.path.basename(sys.argv[0]) == 'copy-climate.ju.py'
RUN_ID_CLIMATE = int(sys.argv[1]) if is_py and len(sys.argv) > 1 else 86
RUN_ID_LAND = int(sys.argv[2]) if is_py and len(sys.argv) > 2 else 88
RUN_ID_DEST = int(sys.argv[3]) if is_py and len(sys.argv) > 3 else 89

root_dir = '/home/mok/miniguc/'
data_dir_climate = glob(root_dir + f'runs/{RUN_ID_CLIMATE:03}*/')[0]
data_dir_land = glob(root_dir + f'runs/{RUN_ID_LAND:03}*/')[0]

climate_wrfin = Dataset(glob(data_dir_climate + 'wrfin*')[0])
land_wrfin = Dataset(glob(data_dir_land + 'wrfin*')[0])

climate_wrfbdy = Dataset(glob(data_dir_climate + 'wrfbdy*')[0])
land_wrfbdy = Dataset(glob(data_dir_land + 'wrfbdy*')[0])

# %%

def list_variables(dataset: Dataset) -> None:
    '''
    List all variables in the nc dataset for adjustment
    dataset:    netcdf dataset
    '''
    print('\n'.join(map(lambda x: f'{x.name}: {dataset[x.name].__dict__.get('description')} {x.dimensions}', dataset.variables.values())))

def copy_variable(src: Dataset, dest: Dataset, var_name: str) -> Dataset:
    '''
    Copy the variable {var_name} from src to dest
    returns the dest dataset
    '''
    dest.variables[var_name][:] = src.variables[var_name][:]
    return dest

# list_variables(climate_wrfbdy)

# %%

def mix_file(climate_ds: Dataset, land_ds: Dataset, new_name: str) -> None:
    '''
    Take the climate variables from climate_ds + the rest from land_ds and copy it to out
    save it as new name
    '''
    climate_vars = [
        'U', 'V', 'W', 'T', 'THM', 'T_INIT', 'MU', 'MUB', 'P',
        'AL', 'ALB', 'PB', 'T_BASE', 'Q2', 'T2', 'TH2', 'PSFC',
        'U10', 'V10', 'QVAPOR', 'QCLOUD', 'QRAIN', 'QICE', 'QSNOW',
        'QGRAUP', 'QNICE', 'QNRAIN', 'qke_adv', 'FCX', 'GCX',
        'U_BASE', 'V_BASE', 'QV_BASE', 'U_FRAME', 'V_FRAME', 'P_TOP',
        'T00', 'P00', 'P_STRAT', 'CLDFRA', 'QSFC_MOSAIC', 'SST', 'PC'
    ]

    with Dataset(new_name, 'w', format='NETCDF4') as out:
        attributes = land_ds.__dict__
        attributes['TITLE'] += ' (MODIFIED)'
        attributes['NOTE'] = f'Climate from run ID {RUN_ID_CLIMATE} + Land from run ID {RUN_ID_LAND}'
        out.setncatts(attributes)

        for name, dimension in land_ds.dimensions.items():
            dimension_size = len(dimension) if not dimension.isunlimited() else None
            out.createDimension(name, dimension_size)

        for name, variable in land_ds.variables.items():
            out.createVariable(
                name,
                variable.datatype,
                variable.dimensions,
                zlib = True,            # Lossless compression (optional)
                complevel = 5,          # Lossless compression (optional)
                shuffle = True          # Lossless compression (optional)
            )
            out[name].setncatts(land_ds[name].__dict__)
            out[name][:] = land_ds[name][:]

        # wrfinput case
        for var_name in climate_vars:
            if not var_name in land_ds.variables: continue
            print(f'Copying {var_name}', end='\r')
            out = copy_variable(climate_ds, out, var_name)

        # wrfbdy case
        for var_name in climate_vars:
            for suffix in ['BXS', 'BXE', 'BYS', 'BYE']:
                if not (var_name + f'_{suffix}') in land_ds.variables: break
                print(f'Copying {var_name}', end='\r')
                out = copy_variable(climate_ds, out, var_name + f'_{suffix}')

            for suffix in ['BTXS', 'BTXE', 'BTYS', 'BTYE']:
                if not (var_name + f'_{suffix}') in land_ds.variables: break
                print(f'Copying {var_name}', end='\r')
                out = copy_variable(climate_ds, out, var_name + f'_{suffix}')
    print()

# %%

import os

print('Modifying wrfinput')

output_dir_wrfin = (glob(root_dir + f'runs/{RUN_ID_DEST:03}*/')[0]) + 'wrfinput_d01'
if len(glob(output_dir_wrfin)) > 0:
    raise Exception(f'wrfinput file already exists on run ID {RUN_ID_DEST}')

mix_file(climate_wrfin, land_wrfin, output_dir_wrfin)

print('Modifying wrfbdy')

output_dir_wrfbdy = (glob(root_dir + f'runs/{RUN_ID_DEST:03}*/')[0]) + 'wrfbdy_d01'
if len(glob(output_dir_wrfbdy)) > 0:
    raise Exception(f'wrfbdy file already exists on run ID {RUN_ID_DEST}')

mix_file(climate_wrfbdy, land_wrfbdy, output_dir_wrfbdy)
print('Done!')

# %%

if not is_py:
    test_ds = Dataset(output_dir_wrfin)
    print(test_ds.variables['T'][:] - climate_wrfin.variables['T'][:])

if not is_py:
    test_ds = Dataset(output_dir_wrfbdy)
    print(test_ds.variables['T_BXS'][:] - climate_wrfbdy['T_BXS'][:])
