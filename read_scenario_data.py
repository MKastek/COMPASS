import itertools
import scipy.io
import os
import numpy as np
import pandas as pd
import shutil


def save_physical_data(filename, key, file_to_save_dir):
    mat = scipy.io.loadmat(os.path.join('scenarios-data', filename))
    data = np.array(list(itertools.chain.from_iterable(mat['signal']['data'][0])), dtype=np.float32)
    time_length = data.shape[0]
    psi_length = data.shape[1]
    file_to_save = 'electron_temp.txt' if key == 'Te' else 'electron_density.txt'
    pd.DataFrame(data).to_csv(os.path.join(file_to_save_dir, file_to_save), sep=' ', index=False, header=False, float_format='%0.18e')
    line_unit = '[eV]' if key == 'Te' else '[m-3]'
    line_shape = str(time_length)+'x'+str(psi_length)+' '+'time'+' '+'x'+' '+'psi'
    with open(os.path.join(file_to_save_dir, file_to_save), 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line_unit.rstrip('\r\n') + '\n' + line_shape.rstrip('\r\n') + '\n' + content)


def save_geometry_data(filename, file_to_save_dir):
    mat = scipy.io.loadmat(os.path.join('scenarios-data', filename))
    data = np.array(list(itertools.chain.from_iterable(mat['signal']['axis1'].item()['data'][0][0])), dtype=np.float32)
    print(data)
    time_length = data.shape[0]
    psi_length = data.shape[1]
    file_to_save = 'psi_n.txt'
    pd.DataFrame(data).to_csv(os.path.join(file_to_save_dir, file_to_save), sep=' ', index=False, header=False, float_format='%0.18e')
    line_unit = '[znormalizowane]'
    line_shape = str(time_length) + 'x' + str(psi_length) + ' ' + 'time' + ' ' + 'x' + ' ' + 'psi'
    with open(file_to_save, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line_unit.rstrip('\r\n') + '\n' + line_shape.rstrip('\r\n') + '\n' + content)


def save_time_data(filename, file_to_save_dir):
    mat = scipy.io.loadmat(os.path.join('scenarios-data', filename))
    data = np.array(list(itertools.chain.from_iterable(mat['signal']['time_axis'].item()['data'][0])), dtype=np.float32)
    file_to_save = 'time.txt'
    pd.DataFrame(data).to_csv(os.path.join(file_to_save_dir, file_to_save), sep=' ', index=False, header=False, float_format='%0.18e')


def read_scenarios():
    scenarios = ['3100', '3210', '5400', '23400', '24300']
    for scenario in scenarios:
        # if directory for scenario does not exist - create one
        isDir = os.path.isdir('data-' + scenario)
        if not isDir:
            os.mkdir('data-' + scenario)

    files_with_data = [f for f in os.listdir(os.path.join('scenarios-data')) if os.path.isfile(os.path.join(os.path.join(
        'scenarios-data'), f))]

    for scenario in scenarios:
        for word in files_with_data:
            if word.startswith(scenario):

                if word.endswith('nep.mat'):
                    save_physical_data(word, 'Ne', 'data-' + scenario)
                    save_time_data(word, 'data-' + scenario)

                if word.endswith('tep.mat'):
                    save_physical_data(word, 'Te', 'data-' + scenario)

        shutil.copy(os.path.join('data','psi_n.txt'),os.path.join('data-' + scenario))
        shutil.copy(os.path.join('data', 'equilibrium.npz'), os.path.join('data-' + scenario))
