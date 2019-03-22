# plotting.py
# Author: Joshua Beard
# Created: 2019-01-08

# TODO:
# [ ] Better placement of on-chart text relative to bar height
# [ ] Support for "below"-bar on-chart text
# [ ] Test non-scaled bars
# [ ] different logic if labels are numbers as opposed to strings?
# [ ] support show=False
# [ ] label_rotation = 45 causes part of long labels to be placed off page. Can I rectify this?
# [ ] init of Plot2D should use a kwarg

import numpy as np
from matplotlib import pyplot as plt
from . import util
from collections import Iterable
from os.path import join as pathjoin


def bars(data,
         labels=None,
         bar_width=0.75,
         figsize=(12, 8),
         title='',
         ylim=None,
         max_val_pad=0.1,
         sort_by=None,
         show_bottom_labels=True,
         show_legend=False,
         show_max_val=False,
         show=True,
         save=False,
         save_name=None,
         scale_by=None,
         show_bar_labels=False,
         bar_label_format=None,
         multicolor=True,
         show_as_percent=False,
         debug=False,
         ):
    """
        Plots separate bars as independent categories, coloring them differently
        Parameters:
            data: <list>, <tuple>, or <np.ndarray> of the bar heights
            labels: <list>, <tuple>, or <np.ndarray> of labels for the different bars (optionally displayed)
            bar_width: <int> or <float> defining bar width
            figsize: <list>, <tuple>, or <np.ndarray> of figure size
            title: <str> defining the graph title, which is scaled based on figure size. If save_name is not defined, but save==True, this is also the save name
            ylim: <list>, <tuple>, or <np.ndarray> of y limits, None does autoscaling
            max_val_pad: <int> or <float> defining the proportional padding above the max value. Autoscaling uses 0.1
            sort_by: <str>, <tuple>, <list>, <np.ndarray> defining order of data displayed ('ascending' or 'descending', or some canonical ordering). None does no sorting
            show_bottom_labels: <bool> switch for displaying labels at the bottom
            show_legend: <bool> switch for displaying legend
            show_max_val: <bool> switch for displaying dashed line at maximum value
            show: <bool> whether to show the plot NOTE: as of version 0.1.2, setting this to False does nothing
            save: <bool> whether to save the plot
            scale_by: <int>, <float>, <tuple>, <list>, <np.ndarray> the factor by which to scale the data. Note this must be broadcastable to the data
            show_bar_labels: <bool> switch for displaying labels at top of each bar
            bar_label_format: function format for bars label. If None, displays raw data
            show_as_percent: <bool> scales everything as percentages
        Returns: Nothing
    """

    valid_options = {'data': (list, np.ndarray),
                     'labels': (list, np.ndarray),
                     'bar_width': (float),
                     'figsize': (list, tuple, np.ndarray),
                     'title': (str),
                     'ylim': (list, tuple, np.ndarray, None),
                     'max_val_pad': (int, float, None),
                     'sort_by': (None, 'ascending', 'descending', tuple, list, np.ndarray),
                     'show_bottom_labels': (bool),
                     'show_legend': (bool),
                     'show_max_val': (bool),
                     'show': (bool),
                     'save': (bool),
                     'save_name': (str, None),
                     'scale_by': (list, tuple, int, float, np.ndarray, None),
                     'show_bar_labels': (bool),
                     'bar_label_format': (None, type(lambda x: x)),
                     'save': (bool),
                     }

    data = np.array(data)
    labels = np.array(labels)

    # Only sort if specified, and do so either ascending or descending
    util.check_parameter(sort_by, 'sort_by', valid_options)
    if sort_by is not None:
        if debug:
            import ipdb
            ipdb.set_trace()

        if isinstance(sort_by, str):
            order = np.argsort(data)
            if sort_by.lower() == 'descending':
                order = order[::-1]
        else:
            order = np.array(sort_by)
        data = data[order]
        labels = labels[order]

    # If we're showing labels at the bottom (and they're defined):
    util.check_parameter(labels, 'labels', valid_options)
    if show_bottom_labels and labels is not None:
        if len(labels) != len(data):
            raise ValueError('len(labels) != len(data)')

        bottom_labels = [labels[i] + '\nN = {}'.format(data[i])
                         for i in range(len(labels))]

        # If there are lots of items, rotate the labels
        if len(labels) > 7:
            label_rotation = 45
        else:
            label_rotation = 0
    else:
        bottom_labels = None

    # Used if normalizing
    if scale_by is not None:
        data = data / np.array(scale_by)
        max_val = 1
    else:
        max_val = data.max()

    # Separation between bars
    #string_dtype = np.dtype('<U1')
    #if labels.dtype == string_dtype:
    #    offsets = list(range(len(labels)))
    #else:
    #    offsets = list(range(len(labels)))
    offsets = list(range(len(labels)))

    # If we're displaying percentages, scale the y-axis accordingly
    if show_as_percent:
        data *= 100
        if ylim is not None:
            ylim = (ylim[0] * 100, ylim[1] * 100)

    # Now let's plot the damn thing
    bars = []
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    if multicolor:
        for i in range(len(labels)):
            bars.append(ax.bar(offsets[i], data[i], bar_width))
    else:
        bars = ax.bar(offsets, data, bar_width)

    # Show a line at the maximum value
    if show_max_val:
        max_val = 100 if show_as_percent else max_val
        ax.plot([min(offsets) - 1, max(offsets) + 1],
                [max_val, max_val],
                '--',
                color=[0.75, 0.75, 0.75])

    # Text drawn on the graph labeling the bars with their data
    if show_bar_labels:

        util.check_parameter(bar_label_format, 'bar_label_format', valid_options)
        # bar_label_format should either be None or some function
        if bar_label_format is not None:
            fmt = bar_label_format
        else:
            def fmt(x):
                return '{}'.format(x)

        if scale_by is not None:
            y_offset = 0.05

        for i in range(len(labels)):
            plt.text(x=offsets[i], y=data[i] + y_offset, s=fmt(data[i]))

    # If ylim is not specified, autoscale
    if ylim is None:
        ylim = (0, max(data) + max(data) * max_val_pad)

    # Limits and tick spacing
    ax.set_ylim(ylim)
    ax.set_xlim(-bar_width, (len(data) - 1) + bar_width)
    ax.set_xticks(offsets)
    plt.tick_params(labelsize=max(figsize))

    # If bottom labels were defined
    if bottom_labels is not None:
        xtick_labels = ax.set_xticklabels(bottom_labels)
        plt.setp(xtick_labels, rotation=label_rotation)
    else:
        xtick_labels = ax.set_xticklabels(['' for i in data])

    # Using a legend
    if show_legend:
        ax.legend(bars, labels, prop={'size': max(figsize)})

    # Title
    fig.suptitle(title, fontsize=max(figsize) * 2)

    # Saving uses title if save_name is not defined
    if save:
        if save_name is not None:
            plt.savefig(save_name)
        else:
            plt.savefig(title)

    if show:
        plt.show()


class Plot2D():
    def __init__(self, **kwargs):
        plot_type = kwargs.get('plot_type').lower()
        if plot_type == 'bars':
            data = kwargs.get('data') 
            if data is None:
                data = kwargs.get('x') 
            bars(data, **kwargs)
        elif plot_type == 'lines':
            self.plot = Lines(**kwargs)


class Lines(Plot2D):
    constraints = {'x': Iterable,
                   'y': Iterable,
                   'labels': (lambda x: util.isiterable(x) or type(x) == str),
                   'figsize': Iterable,
                   'title': str,
                   'ylim': Iterable,
                   'max_val_pad': (int, float, '>=0'),
                   'show_bottom_labels': bool,
                   'show_legend': bool,
                   'show': bool,
                   'save': bool,
                   'save_name': str,
                   'xlabel': str,
                   'ylabel': str,
                   }
    defaults = {'x': None,
                'y': None,
                'labels': None,
                'figsize': (12, 8),
                'title': '',
                'ylim': None,
                'max_val_pad': 0,
                'show_bottom_labels': False,
                'show_legend': True,
                'show': True,
                'save': False,
                'save_name': None,
                'xlabel': None,
                'ylabel': None,
                }
    def __init__(self, **kwargs):
        self.params = util.ParameterRegister(constraints=constraints, defaults=defaults, accept_none=True)
        self.params.set(**kwargs)
        self.params.set_uninitialized_params()

        self._fig = plt.figure(figsize=self._figsize)
        self._ax = self._fig.add_subplot(111)

        self._savename = self.params['save_name']
        if self._savename is None:
            self._savename = 'graph_' + '_'.join(self.title.split(' '))

        self._lines = []
        
        # Do the plotting (and add legend if labels are given)
        if self.params['labels'] is not None:
            # TODO do I need to do something special if x is None?
            for i, (y, label) in enumerate(zip(self.params['x'], self.params['y'])):
                self._lines.append(self._ax.plot(self.params['x'], y, label=label))
            plt.legend()
        else:
            for i, y in enumerate(self.params['y']):
                self._lines.append(self._ax.plot(self.params['x'], y))

        # Title
        plt.title(self.params['title'])

        # x and y labels
        if self.params['xlabel'] is not None:
            self._ax.set_xlabel(self.params['xlabel'])

        if self.params['ylabel'] is not None:
            self._ax.set_ylabel(self.params['ylabel'])

        # Save and show now if needed
        if self.params['save']:
            self.save()

        if self.params['show']:
            self.show()

    def show(self):
        plt.show()

    def save(self, savename=None):
        if savename is not None:
            self._savename = savename

        plt.savefig(pathjoin('figs', self._savename))

