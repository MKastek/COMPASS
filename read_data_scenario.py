import itertools
import scipy.io
import os
import numpy as np
import pandas as pd


def save_physical_data(filename,key):
    mat = scipy.io.loadmat(os.path.join('Scenarios - data', filename))
    data = np.array(list(itertools.chain.from_iterable(mat['signal']['data'][0])), dtype=np.float32)
    time_length = data.shape[0]
    psi_length = data.shape[1]
    file_to_save = 'electron_temp.txt' if key == 'Te' else 'electron_density.txt'
    pd.DataFrame(data).to_csv(file_to_save, sep=' ', index=False, header=False, float_format='%0.18e')
    line_unit = '[eV]' if key == 'Te' else '[m-3]'
    line_shape = str(time_length)+'x'+str(psi_length)+' '+'time'+' '+'x'+' '+'psi'
    with open(file_to_save, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line_unit.rstrip('\r\n') + '\n' + line_shape.rstrip('\r\n') + '\n' + content)


def save_geometry_data(filename):
    mat = scipy.io.loadmat(os.path.join('Scenarios - data', filename))
    data = np.array(list(itertools.chain.from_iterable(mat['signal']['axis1'].item()['data'][0][0])), dtype=np.float32)
    print(data)
    time_length = data.shape[0]
    psi_length = data.shape[1]
    file_to_save = 'psi_n.txt'
    pd.DataFrame(data).to_csv(file_to_save, sep=' ', index=False, header=False, float_format='%0.18e')
    line_unit = '[znormalizowane]'
    line_shape = str(time_length) + 'x' + str(psi_length) + ' ' + 'time' + ' ' + 'x' + ' ' + 'psi'
    with open(file_to_save, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line_unit.rstrip('\r\n') + '\n' + line_shape.rstrip('\r\n') + '\n' + content)


def save_time_data(filename):
    mat = scipy.io.loadmat(os.path.join('Scenarios - data', filename))
    data = np.array(list(itertools.chain.from_iterable(mat['signal']['time_axis'].item()['data'][0])), dtype=np.float32)
    file_to_save = 'time.txt'
    pd.DataFrame(data).to_csv(file_to_save, sep=' ', index=False, header=False, float_format='%0.18e')