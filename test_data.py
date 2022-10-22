import os
import numpy as np
from scipy.interpolate import griddata
from read_input_data import replace_values
import scipy.io
import itertools
import matplotlib.pyplot as plt
from scipy import interpolate
from pathlib import Path
import re
from typing import Optional, Tuple


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def glob_re(pattern, strings):
    return filter(re.compile(pattern).match, strings)


def generate_2D_profile(scenario: str, key: str, time: float) -> np.ndarray:

    # File path to geometric data
    data_geom_path = Path('data') / 'equilibrium.npz'
    data_geom_COMPASS = np.load(str(data_geom_path))

    # Time index
    psi_n_index = np.where(np.isclose(data_geom_COMPASS['time'], time))

    # Get geometrical data and replace non-physical values with 0
    data_psi_n = data_geom_COMPASS['psi_n'][psi_n_index].squeeze()
    data_psi_n = np.where((data_psi_n > 1) | (data_psi_n < 0), 0, data_psi_n)

    # Interpolate data
    r, z = data_geom_COMPASS['r'], data_geom_COMPASS['z']
    r_new = np.linspace(r.min(), r.max(), num=1000)
    z_new = np.linspace(z.min(), z.max(), num=1000)

    f = interpolate.interp2d(r, z, data_psi_n.T)
    data_time_psi_n_interpolated = f(r_new, z_new)

    plt.imshow(data_time_psi_n_interpolated)
    plt.show()

    # File path to scenario data
    data_scenario_path = Path() / 'scenarios-data'

    list_of_mat_files = [item.name for item in list(data_scenario_path.glob('*.mat'))]
    names = glob_re(f'{scenario}.*{key.lower()}p.mat', list_of_mat_files)
    physical_data_path = next(names)

    mat_file = scipy.io.loadmat(data_scenario_path / physical_data_path)
    data_physical_time = np.array(list(itertools.chain.from_iterable(mat_file['signal']['time_axis'].item()['data'][0])),
                                  dtype=np.float32).squeeze()
    # Physical index
    physical_index = find_nearest(data_physical_time, time)
    print(physical_index)




generate_2D_profile('3100', 'Te', 0.1)
# Geometrical data with psi_n(r,z)


print("Geometrical data")
data_COMPASS = np.load(os.path.join('data','equilibrium.npz'))
data_psi_n, data_time_psi_n = replace_values(data_COMPASS)
print("Key values: ", end=' ')
for key in data_COMPASS:
    print(key, end=' ')
print()

print(f"Shape of r {data_COMPASS['r'].shape}")
print(f"Shape of z {data_COMPASS['z'].shape}")
print(f"Shape of psi_n {data_COMPASS['psi_n'].shape}")
print(f"Shape of time {data_COMPASS['time'].shape}")



# Physical data with Te and Ne
print("\n")
print("Physical data")
mat_Ne = scipy.io.loadmat(os.path.join('scenarios-data', '3100_profil0d_nep.mat'))
data_Ne = np.array(list(itertools.chain.from_iterable(mat_Ne['signal']['data'][0])), dtype=np.float32)

mat_Te = scipy.io.loadmat(os.path.join('scenarios-data', '3100_profil0d_tep.mat'))
data_Te = np.array(list(itertools.chain.from_iterable(mat_Te['signal']['data'][0])), dtype=np.float32)

data_time_Ne_Te = np.array(list(itertools.chain.from_iterable(mat_Ne['signal']['time_axis'].item()['data'][0])), dtype=np.float32).squeeze()
print(f"Shape of time {data_time_Ne_Te.shape}")
print(f"Shape of Ne {data_Ne.shape}")
print(f"Shape of Te {data_Te.shape}")

