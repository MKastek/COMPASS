from read_data import get_2D_section, get_CDS_cross_sections, get_physical_data
from bokeh.models import ColumnDataSource, Slider, CustomJS, Div
from bokeh.plotting import figure, output_file, save
from bokeh.models.tools import HoverTool
from bokeh.layouts import column, row
from bokeh.models import Select, Button
from bokeh.io import show, curdoc
from bokeh.layouts import layout
import os
import numpy as np

data_1D_Ne = get_physical_data('electron_density.txt')
ds_1D_Ne = ColumnDataSource(data_1D_Ne)

data_1D_Te = get_physical_data('electron_temp.txt')
ds_1D_Te = ColumnDataSource(data_1D_Te)

data = np.load(os.path.join('data','equilibrium.npz'))

title_div = Div(text='<h1 style="text-align: center"> COMPASS Upgrade</h1><p>Author: Marcin Kastek</p>')
select_1D = Select(title="time [s]: ", options=list(data_1D_Ne.columns))


fig_1D_Ne = figure(toolbar_location="above", x_axis_label=r"$$ \psi = \frac{R_{eff}}{a} $$", y_axis_label=r"$$N_{e} [m^{-3}]$$",
              y_range=(data_1D_Ne.min().min(), data_1D_Ne.max().max()), x_range=(-0.1, 1.1),
              title=r"Electron density Ne [m-3]")

fig_1D_Te = figure(toolbar_location="above", x_axis_label=r"$$ \psi = \frac{R_{eff}}{a} $$", y_axis_label=r"$$T_{e} [eV]$$",
              y_range=(data_1D_Te .min().min(), data_1D_Te.max().max()), x_range=(-0.1, 1.1),
              title=r"Electron temperature Te [eV]")

fig_1D_Ne.add_tools(HoverTool(tooltips=[("y", "@index")]))
fig_1D_Te.add_tools(HoverTool(tooltips=[("y", "@index")]))

line_renderer_1D_Ne = fig_1D_Ne.line('index', '0.0', source=ds_1D_Ne)
line_renderer_1D_Te = fig_1D_Te.line('index', '0.0', source=ds_1D_Te)

handler_1D_Ne = CustomJS(args=dict(line_renderer=line_renderer_1D_Ne), code="""
   line_renderer.glyph.y = {field: cb_obj.value};
""")
handler_1D_Te = CustomJS(args=dict(line_renderer=line_renderer_1D_Te), code="""
   line_renderer.glyph.y = {field: cb_obj.value};
""")


select_1D.js_on_change('value', handler_1D_Ne)
select_1D.js_on_change('value', handler_1D_Te)

data_2D_Te = get_2D_section(filename=os.path.join('data','electron_temp.txt'),rotate=True)



fig_2D_Te = figure(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@im")],x_axis_label=r"$$ R [m] $$", y_axis_label=r"$$z [m]$$",
                 title=r"Electron temperature Te [eV]",aspect_ratio=1.0)
fig_2D_Te.x_range.range_padding = fig_2D_Te.y_range.range_padding = 0


src_Te_2D = ColumnDataSource(data={'x':[0.25],'y':[-1],'dw':[1.25],'dh':[2],'im':[data_2D_Te[1]]})
im_rend_2D_Te =fig_2D_Te.image(image='im', x='x', y='y', dw='dw', dh='dh', palette="Plasma11", level="image",source=src_Te_2D)

fig_2D_Te.grid.grid_line_width = 0.5


slider_2D = Slider(start=1,end=54,value=1,step=1,title='Time atfer ignition [s]: 0.050 Time step')


cb = CustomJS(args=dict(src=src_Te_2D,imdict=data_2D_Te,sl=slider_2D)
              ,code='''
              //assign the im field in the datasource the 2D image associated with the slider value
              src.data['im'] = [imdict[sl.value]]
              src.change.emit()
              ''')
slider_2D.js_on_change('value',cb)
lo_Te_2D = layout([fig_2D_Te])

dict_Ne = get_2D_section(filename=os.path.join('data','electron_density.txt'),rotate=True)
#dic_Ne = {key:data.T for data,key in zip(dict_Ne.values(),dict_Ne.keys())}

fig_2D_Ne = figure(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@im e+19")],x_axis_label=r"$$ R [m] $$", y_axis_label=r"$$z [m]$$",
                 title=r"Electron density Ne [m-3]",aspect_ratio=1.0)
fig_2D_Ne.x_range.range_padding = fig_2D_Ne.y_range.range_padding = 0

src_Ne_2D = ColumnDataSource(data={'x':[0.25],'y':[-1],'dw':[1.25],'dh':[2],'im':[dict_Ne[1]]})

im_rend_Ne = fig_2D_Ne.image(image='im', x='x', y='y', dw='dw', dh='dh', palette="Plasma11", level="image",source=src_Ne_2D)

fig_2D_Ne.grid.grid_line_width = 0.5


cb = CustomJS(args=dict(src=src_Ne_2D,imdict=dict_Ne,sl=slider_2D)
              ,code='''
              //assign the im field in the datasource the 2D image associated with the slider value
              src.data['im'] = [imdict[sl.value]]
              src.change.emit()
              ''')
slider_2D.js_on_change('value',cb)
lo_Ne_2D = layout([fig_2D_Ne])

div = Div(text = 'Time after ignition', name = "time")

code = "var div = Bokeh.documents[0].get_model_by_name('time');" \
       "div.text = 'data[sl.value]'"
slider_2D.js_on_change('value',CustomJS(args=dict(data=data["time"],sl=slider_2D,div=div),code = '''
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

source_cds_2D_Ne, znew, rnew = get_CDS_cross_sections(filename='electron_density.txt')
source_cds_2D_Te, znew, rnew = get_CDS_cross_sections(filename='electron_temp.txt')


div_range = Div(text='Generate cross sections from selected region of z[m] and R[m]', margin = (5, 5, 5, 25))


div_Ne = Div(text = 'Save selected cross sections of Ne to file', name = "file_Ne", margin = (5, 5, 5, 25))

div_Te = Div(text = 'Save selected cross sections of Te to file', name = "file_Te", margin = (5, 5, 5, 25))

slider_zmin = Slider(start=-0.5,end=0.5,value=-0.5,step=0.01,title='zmin', width=250, width_policy="fixed", margin = (5, 25, 5, 25))
slider_zmax = Slider(start=-0.5,end=0.5,value=0.5,step=0.01,title='zmax',width=250, width_policy="fixed",  margin = (5, 25, 5, 25))
slider_rmin = Slider(start=0.25,end=1.5,value=0.25,step=0.01,title='rmin', width=250, width_policy="fixed",  margin = (5, 25, 5, 25))
slider_rmax = Slider(start=0.25,end=1.5,value=1.5,step=0.01,title='rmax', width=250, width_policy="fixed",  margin = (5, 25, 5, 25))
### slider min max

button_Ne.js_on_click(CustomJS(args=dict(source=source_cds_2D_Ne ,sl=slider_2D,data=data["time"],file='Ne', sl_zmin=slider_zmin, sl_zmax=slider_zmax, sl_rmin=slider_rmin, sl_rmax=slider_rmax, znew=znew, rnew=rnew),
                           code=open("download.js").read()))
button_Te.js_on_click(CustomJS(args=dict(source=source_cds_2D_Te,sl=slider_2D,data=data["time"],file='Te', sl_zmin=slider_zmin, sl_zmax=slider_zmax, sl_rmin=slider_rmin, sl_rmax=slider_rmax, znew=znew, rnew=rnew),
                           code=open("download.js").read()))

show(column(title_div, select_1D, row(fig_1D_Ne, fig_1D_Te), slider_2D, row(lo_Ne_2D, lo_Te_2D), div_range,row(slider_zmin,slider_zmax,slider_rmin,slider_rmax), row(div_Ne, button_Ne, div_Te, button_Te)))
