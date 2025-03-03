﻿"""Simple 1D & 2D plotting utilities package for "Synchrotron Radiation Workshop" (SRW).

``uti_plot`` currently wraps ``matplotlib``, but other backends are
planned.  If no suitable backend is available, ``uti_plot_init`` sets
the backend to ``uti_plot_none`` so that the calling program is still
functional.  This is useful for systems where there is no graphing
library available, but you still want to see the results of the
SRW program.

Usage:

    import uti_plot as up

    up.uti_plot_init()
    uti_plot1d(...)
    uti_plot_show()

Modules:

    uti_plot
        This module, which loads all other modules dynamically

    uti_plot_matplotlib
        Does the actually plotting using matplotlib.pyplot.  Currently, loaded in all cases except
        when ``backend`` is ``None``

    test_uti_plot
        Simple tests for uti_plot

.. moduleauthor:: Rob Nagler <nagler@radiasoft.net>
"""
try: #OC15112022
    from . import uti_plot_com
except:
    import uti_plot_com
#import uti_plot_com
import sys
import traceback

_backend = None

DEFAULT_BACKEND = '<default>'

def uti_plot_init(backend=DEFAULT_BACKEND, fname_format=None):
    """Initializes plotting engine with backend and, optionally, save plots to fname_format

    Tries to initialize `backend` as the plotting engine.  If not found, an
    error will be printed, and this module's functions will be no-ops.  If
    DEFAULT_BACKEND provided, an appropriate backend will be chosen and printed.
    Plots may also be saved if fname_format is supplied.

    You may call ``uti_plot_init(None)`` explicitly so that no plotting occurs.

    :param str backend: a matplot backend (TkAgg, etc.) or ``inline`` in IPython
    :param str fname_format: where to save plots. format field is a sequential plot number, starting at 0.
    """
    global _backend
    if backend is not None:
        try:
            from . import uti_plot_matplotlib
            _backend = uti_plot_matplotlib.Backend(backend, fname_format)
            return
        except:
            traceback.print_exc()
            print(backend + ': unable to import specified backend (or its dependency); no plots')
    elif fname_format is not None:
        #raise Value(fname_format + ': fname_format must be null if backend is None')
        raise ValueError(fname_format + ': fname_format must be null if backend is None')
    _backend = _BackendNone()

def uti_plot_show():
    """Display the plots"""
    #if '_backend' not in locals(): uti_plot_init() #?
    _backend.uti_plot_show()

def uti_plot1d(ar1d, x_range, labels=('Photon Energy [eV]', 'ph/s/0.1%bw'), units=None):
    """Generate one-dimensional line plot from given array

    :param array ar1d: data points
    :param list x_range: Passed to numpy.linspace(start sequence, stop sequnce, num samples)
    :param tuple labels: [x-axis, y-axis]
    """
    #if '_backend' not in locals(): uti_plot_init() #?
    
    if(units is not None):
        x_range, x_unit = uti_plot_com.rescale_dim(x_range, units[0])
        units = [x_unit, units[1]]
        strTitle = '' if(len(labels) < 3) else labels[2]
        labels = (labels[0] + ' [' + units[0] + ']', labels[1] + ' [' + units[1] + ']', strTitle)

    #print('uti_plot1d:', x_range)
    _backend.uti_plot1d(ar1d, x_range, labels)

def uti_plot1d_ir(ary, arx=None, labels=('Longitudinal Position [m]', 'Horizontal Position [m]'), units=None): #OC25102019
#def uti_plot1d_ir(ary, arx, labels=('Longitudinal Position [m]', 'Horizontal Position [m]'), units=None): #OC15112017
    """Generate one-dimensional line plot from given array

    :param array arx: abscissa array
    :param array ary: ordinate array
    :param tuple labels: [x-axis, y-axis]
    """
    #if '_backend' not in locals(): uti_plot_init() #?
    
    if(units is not None):
        #x_range = [min(arx), max(arx), len(arx)]
        #x_range, x_unit = uti_plot_com.rescale_dim(x_range, units[0])
        #units = [x_unit, units[1]]
        strTitle = '' if(len(labels) < 3) else labels[2]
        labels = (labels[0] + ' [' + units[0] + ']', labels[1] + ' [' + units[1] + ']', strTitle)

    #OC25102019 (added stuff below)
    if(arx is None):
        ary0 = ary
        if(not(isinstance(ary0, list) or isinstance(ary0, array) or isinstance(ary0, tuple))):
            raise Exception("Incorrect definition of data arrays / lists to be plotted")

        lenData = len(ary)
        #arx = array.array('d', [0]*lenData)
        #aryNew = array.array('d', [0]*lenData)
        arx = [0]*lenData
        aryNew = [0]*lenData
        for i in range(lenData):
            ay_i = ary[i]
            arx[i] = ay_i[0]
            aryNew[i] = ay_i[1]
        ary = aryNew
    
    _backend.uti_plot1d_ir(ary, arx, labels)

def uti_plot1d_m(ars, labels=('X', 'Y'), units=None, styles=None, legend=None): #OC25102019
    """Plot multiple one-dimensional curves in one graph

    :param array ars: multiple data arrays, assuming: ars = [curve_1,curve_2,...], where curve_i can be:
        curve_i = [[y1_i,y2_i,...],[x_min_i,x_max_i,nx_i]] or
        curve_i = [[y1_i,y2_i,...],[x1_i,x2_i,...]] or
        curve_i = [[x1_i,y1_i],[x2_i,y2_i],...] 
    :param tuple labels: (x-axis, y-axis)
    :param tuple units: (x-units, y-units)
    """
    #if '_backend' not in locals(): uti_plot_init() #?
    if(units is not None):
        strTitle = '' if(len(labels) < 3) else labels[2]
        labels = (labels[0] + ' [' + units[0] + ']', labels[1] + ' [' + units[1] + ']', strTitle)

    _backend.uti_plot1d_m(ars, labels, styles, legend)

def uti_plot2d(ar2d, x_range=None, y_range=None, labels=('Horizontal Position [m]','Vertical Position [m]', 'Intensity'), units=None): #OC23082021
#def uti_plot2d(ar2d, x_range=None, y_range=None, labels=('Horizontal Position [m]','Vertical Position [m]'), units=None): #OC30052020
#def uti_plot2d(ar2d, x_range=None, y_range=None, labels=('Horizontal Position [m]','Vertical Position [m]', 'Intensity'), units=None, show=False): #OC16082021
#def uti_plot2d(ar2d, x_range, y_range, labels=('Horizontal Position [m]','Vertical Position [m]'), units=None):
    """Generate quad mesh plot from given "flattened" array

    :param array ar2d: flat 2d array or list of data points, non-flat 2d array or list, or PIL image
    :param list x_range: Passed to numpy.linspace(start sequence, stop sequnce, num samples)
    :param list y_range: y axis (same structure as x_range)
    :param tuple labels: (x-axis, y-axis, z-axis)
    :param tuple units: (x-axis, y-axis, z-axis)
    """
    #if '_backend' not in locals(): uti_plot_init() #?

    if((units is not None) and (x_range is not None) and (y_range is not None)): #OC30052020
    #if(units is not None):
        x_range, x_unit = uti_plot_com.rescale_dim(x_range, units[0])
        y_range, y_unit = uti_plot_com.rescale_dim(y_range, units[1])
        units = [x_unit, y_unit,  units[2]]
        strTitle = '' if(len(labels) < 3) else labels[2]
        labels = (labels[0] + ' [' + units[0]+ ']', labels[1] + ' [' + units[1] + ']', strTitle)

    _backend.uti_plot2d(ar2d, x_range, y_range, labels)
    #if(show): uti_plot_show() #OC16082021 (commented-out back)

def uti_plot2d1d(ar2d, x_range, y_range, x=0, y=0, labels=('Horizontal Position', 'Vertical Position', 'Intensity'), units=None, graphs_joined=True): #OC23082021
#def uti_plot2d1d(ar2d, x_range, y_range, x=0, y=0, labels=('Horizontal Position', 'Vertical Position', 'Intensity'), units=None, graphs_joined=True, show=False): #OC16082021
    """Generate 2d quad mesh plot from given "flattened" array, and 1d cuts passing through (x, y)

    :param array ar2d: flat 2d array of data points
    :param list x_range: Passed to numpy.linspace(start sequence, stop sequnce, num samples)
    :param list y_range: y axis (same structure as x_range)
    :param x: x value for 1d cut
    :param y: y value for 1d cut
    :param tuple labels: (x-axis, y-axis, z-axis)
    :param tuple units: (x-axis, y-axis, z-axis)
    :param graphs_joined: switch specifying whether the 2d plot and 1d cuts have to be displayed in one panel or separately
    """
    
    #if '_backend' not in locals(): uti_plot_init() #?
    if(units is not None): #checking / re-scaling x, y

        #OC17032019
        xRangeOrig = x_range[1] - x_range[0]
        yRangeOrig = y_range[1] - y_range[0] #AH30082019
        #yStartOrig = y_range[1] - y_range[0]
        
        x_range, x_unit = uti_plot_com.rescale_dim(x_range, units[0])
        y_range, y_unit = uti_plot_com.rescale_dim(y_range, units[1])

        #OC17032019
        if(x != 0): x *= (x_range[1] - x_range[0])/xRangeOrig
        if(y != 0): y *= (y_range[1] - y_range[0])/yRangeOrig
        
        units = [x_unit, y_unit,  units[2]]

        strTitle = labels[2]
        label2D = (labels[0] + ' [' + units[0]+ ']', labels[1] + ' [' + units[1] + ']', strTitle)

        #strTitle = 'At ' + labels[1] + ': ' + str(y)
        strTitle = 'At ' + labels[1] + ': ' + str(round(y, 6)) #OC17032019
        
        if y != 0: strTitle += ' ' + units[1]
        label1X = (labels[0] + ' [' + units[0] + ']', labels[2] + ' [' + units[2] + ']', strTitle)

        #strTitle = 'At ' + labels[0] + ': ' + str(x)
        strTitle = 'At ' + labels[0] + ': ' + str(round(x, 6)) #OC17032019
        
        if x != 0: strTitle += ' ' + units[0]
        label1Y = (labels[1] + ' [' + units[1] + ']', labels[2] + ' [' + units[2] + ']', strTitle)
        
    else: #OC081115
        strTitle = labels[2]
        label2D = (labels[0], labels[1], strTitle)

        strTitle = 'At ' + labels[1] + ': ' + str(y)
        label1X = (labels[0], labels[2], strTitle)

        strTitle = 'At ' + labels[0] + ': ' + str(x)
        label1Y = (labels[1], labels[2], strTitle)

    labels = [label2D, label1X, label1Y]

    _backend.uti_plot2d1d(ar2d, x_range, y_range, x, y, labels, graphs_joined)
    #if(show): uti_plot_show() #OC16082021 (commented-out back)

#def uti_plot_img(_img, _x_range=None, _y_range=None, ): #OC29052020
#    _backend.uti_plot_img(_img)

def uti_plot_data_file(_fname, _read_labels=1, _e=0, _x=0, _y=0, _graphs_joined=True, #Same as uti_data_file_plot, but better fits function name decoration rules in this module (uti_plot*)
                       _multicolumn_data=False, _column_x=None, _column_y=None, #MR31102017
                       _scale='linear', _width_pixels=None):
    """Generate plot from configuration in _fname

    :param str _fname: config loaded from here
    :param bool _read_labels: whether to read labels from _fname
    :param float _e: photon energy adjustment
    :param float _x: horizonal position adjustment
    :param float _y: vertical position adjustment
    :param bool _graphs_joined: if true, all plots in a single figure
    :param bool _multicolumn_data: if true, visualize multicolumn data data
    :param str _column_x: column for horizontal axis
    :param str _column_x: column for vertical axis
    :param str _scale: the scale to use for plotting data (linear by default, but could use log, log2, log10)  
    :param int _width_pixels: the width of the final plot in pixels  
    """
    #if '_backend' not in locals(): uti_plot_init() #?
    _backend.uti_plot_data_file(_fname, _read_labels, _e, _x, _y, _graphs_joined,
                                _multicolumn_data, _column_x, _column_y, #MR31102017
                                _scale, _width_pixels)

#def uti_data_file_plot(_fname, _read_labels=1, _e=0, _x=0, _y=0, _graphs_joined=True):
#def uti_data_file_plot(_fname, _read_labels=1, _e=0, _x=0, _y=0, _graphs_joined=True, _traj_report=False, _traj_axis='x'): #MR29072016
#def uti_data_file_plot(_fname, _read_labels=1, _e=0, _x=0, _y=0, _graphs_joined=True, _traj_report=False, _traj_axis='x', _scale='linear', _width_pixels=None): #MR20012017  
def uti_data_file_plot(_fname, _read_labels=1, _e=0, _x=0, _y=0, _graphs_joined=True,
                       _multicolumn_data=False, _column_x=None, _column_y=None, #MR31102017
                       _scale='linear', _width_pixels=None):
    """Generate plot from configuration in _fname

    :param str _fname: config loaded from here
    :param bool _read_labels: whether to read labels from _fname
    :param float _e: photon energy adjustment
    :param float _x: horizonal position adjustment
    :param float _y: vertical position adjustment
    :param bool _graphs_joined: if true, all plots in a single figure
    :param bool _multicolumn_data: if true, visualize multicolumn data data
    :param str _column_x: column for horizontal axis
    :param str _column_x: column for vertical axis
    :param str _scale: the scale to use for plotting data (linear by default, but could use log, log2, log10)  
    :param int _width_pixels: the width of the final plot in pixels  
    """
    #if '_backend' not in locals(): uti_plot_init() #?
    #_backend.uti_data_file_plot(_fname, _read_labels, _e, _x, _y, _graphs_joined)
    #_backend.uti_data_file_plot(_fname, _read_labels, _e, _x, _y, _graphs_joined, _traj_report, _traj_axis) #MR29072016
    #_backend.uti_data_file_plot(_fname, _read_labels, _e, _x, _y, _graphs_joined, _traj_report, _traj_axis, _scale, _width_pixels) #MR20012017  
    #_backend.uti_data_file_plot(_fname, _read_labels, _e, _x, _y, _graphs_joined,
    #                            _multicolumn_data, _column_x, _column_y, #MR31102017
    #                            _scale, _width_pixels)
    uti_plot_data_file(_fname, _read_labels, _e, _x, _y, _graphs_joined, _multicolumn_data, _column_x, _column_y, _scale, _width_pixels) #OC16112017

class _BackendBase(object):
    def __getattr__(self, attr):
        return self._backend_call

class _BackendMissing(_BackendBase):
    def _backend_call(self, *args, **kwargs):
        uti_plot_init()
        method_name = sys._getframe(1).f_code.co_name
        func = getattr(_backend, method_name)
        return func(*args)

class _BackendNone(_BackendBase):
    def _backend_call(*args, **kwargs):
        pass

_backend = _BackendMissing()
