import pandas as pd
import numpy as np
from functools import partial
from bokeh.io import show
from bokeh.layouts import column, row
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, CustomJS, Div
from bokeh.models import Select, Button
from bokeh.models.tools import HoverTool
from bokeh.plotting import figure
from bokeh.layouts import layout
from bokeh.models import Image, ColumnDataSource, Slider, CustomJS
from bokeh.plotting import figure, output_file, save
import os
from read_data import get_2D_section, get_data_Ne, get_data_Te, get_CDS_cross_sections

data_Ne = get_data_Ne()
ds_Ne = ColumnDataSource(data_Ne)

data_Te = get_data_Te()
ds_Te = ColumnDataSource(data_Te)


title = Div(text='<h1 style="text-align: center"> COMPASS Upgrade</h1><p>Author: Marcin Kastek</p>')

p_Ne = figure(toolbar_location="above", x_axis_label=r"$$ \psi = \frac{R_{eff}}{a} $$", y_axis_label=r"$$N_{e} [m^{-3}]$$",
              y_range=(data_Ne.min().min(), data_Ne.max().max()), x_range=(-0.1, 1.1),
              title=r"Electron density Ne [m-3]")

p_Te = figure(toolbar_location="above", x_axis_label=r"$$ \psi = \frac{R_{eff}}{a} $$", y_axis_label=r"$$T_{e} [eV]$$",
              y_range=(data_Te.min().min(), data_Te.max().max()), x_range=(-0.1, 1.1),
              title=r"Electron temperature Te [eV]")

p_Ne.add_tools(HoverTool(tooltips=[("y", "@index")]))
p_Te.add_tools(HoverTool(tooltips=[("y", "@index")]))

line_renderer_Ne = p_Ne.line('index', '0.0', source=ds_Ne)
line_renderer_Te = p_Te.line('index', '0.0', source=ds_Te)

handler_Ne = CustomJS(args=dict(line_renderer=line_renderer_Ne), code="""
   line_renderer.glyph.y = {field: cb_obj.value};
""")
handler_Te = CustomJS(args=dict(line_renderer=line_renderer_Te), code="""
   line_renderer.glyph.y = {field: cb_obj.value};
""")

select = Select(title="time [s]: ", options=list(data_Te.columns))
select.js_on_change('value', handler_Ne)
select.js_on_change('value', handler_Te)

data = np.load('data/equilibrium.npz')

dict_Te = get_2D_section(filename=os.path.join('data','electron_temp.txt'),rotate=True)
#dic_Te = {key:data.T for data,key in zip(dict_Te.values(),dict_Te.keys())}


p_Te_2D = figure(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@im")],x_axis_label=r"$$ R [m] $$", y_axis_label=r"$$z [m]$$",
                 title=r"Electron temperature Te [eV]")
p_Te_2D.x_range.range_padding = p_Te_2D.y_range.range_padding = 0


src_Te_2D = ColumnDataSource(data={'x':[0.25],'y':[-1],'dw':[1.25],'dh':[2],'im':[dict_Te[1]]})
im_rend_Te = p_Te_2D.image(image='im', x='x', y='y', dw='dw', dh='dh', palette="Plasma11", level="image",source=src_Te_2D)

p_Te_2D.grid.grid_line_width = 0.5


sl = Slider(start=1,end=54,value=1,step=1,title='Time atfer ignition [s]: 0.050 Time step')


cb = CustomJS(args=dict(src=src_Te_2D,imdict=dict_Te,sl=sl)
              ,code='''
              //assign the im field in the datasource the 2D image associated with the slider value
              src.data['im'] = [imdict[sl.value]]
              src.change.emit()
              ''')
sl.js_on_change('value',cb)
lo_Te_2D = layout([p_Te_2D])

dict_Ne = get_2D_section(filename=os.path.join('data','electron_density.txt'),rotate=True)
#dic_Ne = {key:data.T for data,key in zip(dict_Ne.values(),dict_Ne.keys())}

p_Ne_2D = figure(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@im e+19")],x_axis_label=r"$$ R [m] $$", y_axis_label=r"$$z [m]$$",
                 title=r"Electron density Ne [m-3]")
p_Ne_2D.x_range.range_padding = p_Ne_2D.y_range.range_padding = 0

src_Ne_2D = ColumnDataSource(data={'x':[0.25],'y':[-1],'dw':[1.25],'dh':[2],'im':[dict_Ne[1]]})

im_rend_Ne = p_Ne_2D.image(image='im', x='x', y='y', dw='dw', dh='dh', palette="Plasma11", level="image",source=src_Ne_2D)

p_Ne_2D.grid.grid_line_width = 0.5


cb = CustomJS(args=dict(src=src_Ne_2D,imdict=dict_Ne,sl=sl)
              ,code='''
              //assign the im field in the datasource the 2D image associated with the slider value
              src.data['im'] = [imdict[sl.value]]
              src.change.emit()
              ''')
sl.js_on_change('value',cb)
lo_Ne_2D = layout([p_Ne_2D])

div = Div(text = 'Time after ignition', name = "time")

code = "var div = Bokeh.documents[0].get_model_by_name('time');" \
       "div.text = 'data[sl.value]'"
sl.js_on_change('value',CustomJS(args=dict(data=data["time"],sl=sl,div=div),code = '''
              //assign the im field in the datasource the 2D image associated with the slider value
              var div = Bokeh.documents[0].get_model_by_name('time');
              var avg = data[sl.value];
              div.text = 'Time atfer ignition [s]: '.concat(avg.toFixed(3).toString());
              var val = sl.value;
              sl.title = div.text.concat(' Time step');
              src.change.emit()
              '''))

output_file(filename="COMPASS_test.html", title="COMPASS")

button_Ne = Button(label="Save Ne", button_type='primary', margin = (5, 25, 5, 5))
button_Te = Button(label="Save Te", button_type='primary', margin = (5, 25, 5, 5))

source = get_CDS_cross_sections(filename='electron_density.txt')
button_Ne.js_on_click(CustomJS(args=dict(source=source,sl=sl,data=data["time"]),
                           code=open("download.js").read()))
#button.on_click(partial(save_cross_sections,sl))

div_Ne = Div(text = 'Save selected cross sections of Ne to file', name = "file_Ne", margin = (5, 5, 5, 25))

div_Te = Div(text = 'Save selected cross sections of Te to file', name = "file_Te", margin = (5, 5, 5, 25))


show(column(title, select, row(p_Ne, p_Te), sl, row(lo_Ne_2D, lo_Te_2D), row(div_Ne, button_Ne, div_Te, button_Te)))
