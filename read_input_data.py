import numpy as np
from bokeh.models import ColumnDataSource
from scipy import interpolate
import pandas as pd
import os
from pathlib import Path

def replace_values(data):
    """
    Change unphysical values where psi_n > 1 or psi_n < 0 to -1

    :param data: data from equilibrium.npz
    :return: 2D array with psi_n values
    """
    data_out = []
    for time_index in range(len(data['time'])):
        data_out.append(np.where((data['psi_n'][time_index, :, :] > 1) | (data['psi_n'][time_index, :, :] < 0), 0, data['psi_n'][time_index, :, :]))
    return data_out, data["time"]


def replace_with_physical_values(data_psi_n, data_physical, key):
    """
    Replace array with psi_n values to corresponding physical values Te or Ne. If psi_n is equal to -1  physical value
    is set to 0.

    :param data_psi_n: array with psi_n values, shape: r_size, z_size
    :param data_physical: array with psi_n values and corresponding to it physical value Te or Ne
    :return: data_psi_n: array with physical value Te or Ne
    """

    z_size = data_psi_n.shape[1]
    r_size = data_psi_n.shape[0]

    for y in range(z_size):
        for x in range(r_size):
            if data_psi_n[x][y] != 0:
                f = interpolate.interp1d(data_physical['Reff'], data_physical[key])
                Reff_new = np.arange(0,1,0.001)
                data_physical_interpolated = f(Reff_new)
                idx = (np.abs(Reff_new - data_psi_n[x][y])).argmin()
                data_psi_n[x][y] = data_physical_interpolated[idx]
            else:
                data_psi_n[x][y] = 0

    return data_psi_n


def get_2D_section(filename, key, to_file = False, rotate = False):
    """
    Return dictionary with 2D crossections of physical value Te or Ne.

    :param filename: file with physical value: Te or Ne with respect to time and psi_n
    :param to_file: bool, if True data with Te are not divided by 10 ** 19
    :param rotate: bool, if True data are transposed
    :return:
    """

    data_COMPASS = np.load(os.path.join('data','equilibrium.npz'))

    dict_2D_sections = {}
    #data_COMPASS['psi_n'].shape[0]

    for i in range(1,data_COMPASS['psi_n'].shape[0]):
        data_cleaned, time = replace_values(data=data_COMPASS)
        time_Te = pd.read_table(os.path.join('data','time.txt'), header=None).iloc[:, 0].values
        idx = (np.abs(time_Te - time[i])).argmin()
        psi = pd.read_table(os.path.join('data','psi_n.txt'), skiprows=2, sep=' ').iloc[0].values
        data_Te = pd.read_table(filename,skiprows=2, sep=' ', names= psi).iloc[idx].reset_index()
        data_Te.rename(columns = {'index': 'Reff', idx: key}, inplace = True)

        data_with_physical_values = replace_with_physical_values(data_psi_n=data_cleaned[i],  data_physical=data_Te, key=key)
        if rotate:
            data_with_physical_values = data_with_physical_values.T
        if os.path.basename(filename) == 'electron_temp.txt':
            dict_2D_sections[i] = data_with_physical_values
        else:
            if not to_file:
                dict_2D_sections[i] = data_with_physical_values / 10 ** 19
            else:
                dict_2D_sections[i] = data_with_physical_values

    return dict_2D_sections


def get_physical_data(dir, filename):
    """
    Return data with physical value: Te or Ne with respect to time and psi_n

    :param filename: file with physical value: Te or Ne with respect to time and psi_n
    :return:
    """
    psi = pd.read_table(os.path.join(dir, 'psi_n.txt'), skiprows=2, sep=' ').iloc[0].values
    time = pd.read_table(os.path.join(dir, 'time.txt'), header=None).iloc[:, 0].values

    data_Ne = pd.read_table(os.path.join(dir, filename), skiprows=2, sep=' ',
                            names=[str(np.round(i, 2)) for i in psi])
    data_Ne = data_Ne.transpose()
    data_Ne.columns = [str(np.round(column, 3)) for column in time]
    return data_Ne


def get_CDS_cross_sections(dir, filename, key):
    """
    Return array of ColumnDataSource with 2D data Te or Ne. Length of array is eqaul to number of time steps.

    :param filename:
    :param key:
    :return:
    """
    data_arr = get_2D_section(os.path.join(dir, filename), to_file=True, key=key)

    data = np.load(os.path.join(dir, 'equilibrium.npz'))

    id_z_start = (np.abs(data['z'] + 0.5)).argmin()
    id_z_stop = (np.abs(data['z'] - 0.5)).argmin()

    y = data['r']
    x = data['z'][id_z_start:id_z_stop]

    ynew = np.linspace(0.25, 1.5, num=200)
    xnew = np.linspace(-0.5, 0.5, num=200)

    CDS_arr = []
    data_COMPASS = np.load(os.path.join(dir, 'equilibrium.npz'))
    #data_COMPASS['psi_n'].shape[0]
    #for i in range(1, data_COMPASS['psi_n'].shape[0]):
    for i in range(1,2):
        data_cross_section = np.array(data_arr[i])
        f = interpolate.interp2d(x, y, data_cross_section[:, id_z_start:id_z_stop], kind='linear')
        if filename == 'electron_density.txt':
            pd.DataFrame(f(xnew,ynew)).replace('e', 'E').to_csv('data.txt', sep='\t', index=False, header=False, float_format='%0.6E')
        if filename == 'electron_temp.txt':
            pd.DataFrame(f(xnew,ynew)).replace('e', 'E').to_csv('data.txt', sep='\t', index=False, header=False,  float_format='%0.6E')
        CDS_arr.append(ColumnDataSource(data=pd.read_csv('data.txt',index_col=False)))

    znew = xnew
    rnew = ynew
    return CDS_arr, znew, rnew


def get_z_and_R_range():
    """
    Calculates range of coordinates z[m] and R[m]

    :return: z_min, z_max, r_min, r_max
    """
    data = np.load(os.path.join('data', 'equilibrium.npz'))
    z_min = data['z'].min()
    z_max = data['z'].max()
    r_min = data['r'].min()
    r_max = data['r'].max()
    return z_min, z_max, r_min, r_max


if __name__ == "__main__":
    dir = Path() / 'input-data' / f"data-{str(3100)}"
    dict_2D_sections = get_2D_section(filename=os.path.join(dir,'electron_density.txt'), key='Te', to_file=False, rotate=False)
    print(dict_2D_sections)
