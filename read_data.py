import numpy as np
from bokeh.models import ColumnDataSource
from scipy import interpolate
import pandas as pd
import os


def replace_values(data):
    """
    Change unphysical values where psi_n > 1 or psi_n < 0 to -1
    :param data: data from equilibrium.npz
    :return: 2D array with psi_n values
    """
    data_out  = []
    for time_index in range(len(data['time'])):
        data_out.append(np.where((data['psi_n'][time_index,:,:] > 1) | (data['psi_n'][time_index,:,:] < 0), -1, data['psi_n'][time_index,:,:]))
    return data_out, data["time"]


def replace_with_Te_values(data,data_Te):
    for j in range(data.shape[1]):
        for i in range(data.shape[0]):
            if data[i][j] != -1:
                idx = (np.abs(data_Te['Reff'] - data[i][j])).argmin()
                data[i][j] = data_Te['Te'][idx]
            else:
                data[i][j] = 0
    return data


def get_2D_section(filename, to_file = False, rotate = False):

    data = np.load(os.path.join('data','equilibrium.npz'))

    dict = {}
    #53
    for i in range(1,3):
        data2,time = replace_values(data=data)
        time_Te = pd.read_table(os.path.join('data','time.txt'), header=None).iloc[:, 0].values
        idx = (np.abs(time_Te - time[i])).argmin()
        psi = pd.read_table(os.path.join('data','psi_n.txt'), skiprows=2, sep=' ').iloc[0].values
        data_Te = pd.read_table(filename,skiprows=2, sep=' ', names= psi).iloc[idx].reset_index()
        data_Te.rename(columns = {'index':'Reff', idx:'Te'}, inplace = True)

        data3 = replace_with_Te_values(data=data2[i], data_Te=data_Te)
        if rotate:
            data3 = data3.T
        if filename == 'electron_temp.txt':
            dict[i] = data3
        else:
            if not to_file:
                dict[i] = data3 / 10 ** 19
            else:
                dict[i] = data3

    return dict


def get_data_Ne():
    psi = pd.read_table(os.path.join('data', 'psi_n.txt'), skiprows=2, sep=' ').iloc[0].values
    time = pd.read_table(os.path.join('data', 'time.txt'), header=None).iloc[:, 0].values

    data_Ne = pd.read_table(os.path.join('data', 'electron_density.txt'), skiprows=2, sep=' ',
                            names=[str(np.round(i, 2)) for i in psi])
    data_Ne = data_Ne.transpose()
    data_Ne.columns = [str(np.round(column, 3)) for column in time]
    return data_Ne


def get_data_Te():
    psi = pd.read_table(os.path.join('data', 'psi_n.txt'), skiprows=2, sep=' ').iloc[0].values
    time = pd.read_table(os.path.join('data', 'time.txt'), header=None).iloc[:, 0].values

    data_Te = pd.read_table(os.path.join('data', 'electron_temp.txt'), skiprows=2, sep=' ',
                            names=[str(np.round(i, 2)) for i in psi])
    data_Te = data_Te.transpose()
    data_Te.columns = [str(np.round(column, 3)) for column in time]
    return data_Te


def get_CDS_cross_sections(filename = 'electron_temp.txt'):
    data_arr = get_2D_section(os.path.join('data', filename), to_file=True)

    data = np.load(os.path.join('data', 'equilibrium.npz'))

    id_z_start = (np.abs(data['z'] + 0.5)).argmin()
    id_z_stop = (np.abs(data['z'] - 0.5)).argmin()

    y = data['r']
    x = data['z'][id_z_start:id_z_stop]

    ynew = np.linspace(0.25, 1.5, num=200)
    xnew = np.linspace(-0.5, 0.5, num=200)

    CDS_arr = []

    for i in range(1,3):
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





