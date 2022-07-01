import numpy as np

from bokeh.plotting import figure, show
from bokeh.layouts import layout
from bokeh.models import Image, ColumnDataSource, Slider, CustomJS

#dummy data taken from https://docs.bokeh.org/en/2.4.0/docs/gallery/image.html
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data = np.load('data/equilibrium.npz')

def replace_values(data):
    data_out  = []
    for time_index in range(len(data['time'])):
        data_out.append(np.where((data['psi_n'][time_index,:,:] > 1) | (data['psi_n'][time_index,:,:] < 0), -1, data['psi_n'][time_index,:,:]))
        #data_out.append(data['psi_n'][time_index, :, :])
        #print(data['psi_n'][time_index, :, :])
    return data_out, data["time"]

def replace_with_Te_values(data,data_Te):
    for j in range(data.shape[1]):
        for i in range(data.shape[0]):
            #print(data[i][j])
            if data[i][j] != -1:
                idx = (np.abs(data_Te['Reff'] - data[i][j])).argmin()
                data[i][j] = data_Te['Te'][idx]
            else:
                data[i][j] = 0
    return data

def get_2D_section(data):
    dict = {}
    for i in range(1,54):
        data2,time = replace_values(data=data)
        time_Te = pd.read_table('data/time.txt', header=None).iloc[:, 0].values
        idx = (np.abs(time_Te - time[i])).argmin()
        #print(idx)

        psi = pd.read_table('data/psi_n.txt', skiprows=2, sep=' ').iloc[0].values
        data_Te = pd.read_table('data/electron_temp.txt', skiprows=2, sep=' ', names= psi).iloc[idx].reset_index()
        data_Te.rename(columns = {'index':'Reff', idx:'Te'}, inplace = True)
        #print(data_Te)


        data3 = replace_with_Te_values(data=data2[i], data_Te=data_Te)
        dict[i-1] = data3.T
        #plt.imshow(data3.T, interpolation='none')
        #plt.xlabel('R')
        #plt.ylabel('Z')
        #plt.show()
    return dict

dict1 = get_2D_section(data)
print(dict[0])

x = np.linspace(0, 10,69)
y = np.linspace(0, 10, 69)
xx, yy = np.meshgrid(x, y)
d1 = np.sin(xx)*np.cos(yy)
#make a second image
d2 = np.sin(xx**2)*np.cos(yy**2)
print(d1)

p = figure(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@im")])
p.x_range.range_padding = p.y_range.range_padding = 0

#initialize a column datasource and assign first image into it
src = ColumnDataSource(data={'x':[0],'y':[0],'dw':[10],'dh':[10],'im':[dict1[1]]})
#create the image randerer pointing to the field names in src, and the source itself
im_rend = p.image(image='im', x='x', y='y', dw='dw', dh='dh', palette="Spectral11", level="image",source=src)

p.grid.grid_line_width = 0.5

#a widget to put a callback on
sl = Slider(start=1,end=49,value=1,step=1,width=100)

#the key here is to pass a dictionary to the callback all the information you need to UPDATE the columndatasource that's driving the renderer
# imdict is basically this --> if slider value is 0, i want to get d1, if slider value is 1, i want to get d2
cb = CustomJS(args=dict(src=src,imdict=dict1,sl=sl)
              ,code='''
              //assign the im field in the datasource the 2D image associated with the slider value
              src.data['im'] = [imdict[sl.value]]
              src.change.emit()
              ''')
sl.js_on_change('value',cb)
lo = layout([p,sl])
show(lo)