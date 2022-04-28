import queue
import time

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

AXES_SIZE = 200
# global data
plt.style.use('ggplot')
# necessary!!! to make sure the backend is the correct one
matplotlib.use('TkAgg')
queues = list()
fig = None
plots = dict()


class PlotData:
    """
    Stores plot relevant data for a queue:
        - q         = queue
        - ax        = subplot
        - x_data    = x-values
        - y_data    = y-values
        - line      = 2D-line (=> plot)
        - name      = name of the plot

    Used to update each plot in liveplot cycle
    """
    def __init__(self, q: queue.Queue, ax, plot_label):
        self.q = q
        self.ax = ax
        self.x_data = list(range(AXES_SIZE))
        self.y_data = np.zeros(AXES_SIZE)
        self.line, = ax.plot(self.x_data, self.y_data)
        self.name = plot_label


def live_plotter(plot_data: PlotData):
    """
    Updates the plot line and the x-axes label and automatically adjusts the boundaries.
    :param plot_data: requires a PlotData object
    :return PlotData.line: 2D-Line
    """
    # after the figure, axis, and line are created, we only need to update the y-data
    plot_data.line.set_ydata(plot_data.y_data)
    # adjust limits if new data goes beyond bounds
    if np.min(plot_data.y_data) <= plot_data.line.axes.get_ylim()[0] or np.max(plot_data.y_data) >= plot_data.line.axes.get_ylim()[1]:
        plot_data.ax.set_ylim([np.min(plot_data.y_data) - np.std(plot_data.y_data), np.max(plot_data.y_data) + np.std(plot_data.y_data)])

    # ascending x-values only the label a changes, the x-range remains the same
    plot_data.line.axes.set_xticklabels(plot_data.x_data)
    # return line, so we can update it again in the next iteration
    return plot_data.line


def perform_live_plot():
    """
    Periodically plots new values from each queue in queues.
    :param pause_time: refresh rate of the plot
    """
    global fig, queues
    if fig:
        for plot_data in queues:
            if plot_data.q.empty():
                # skip if queue has no new values
                continue
            content_y = list()
            # read all new values from the queue
            while not plot_data.q.empty() or len(content_y) > AXES_SIZE:
                content_y.append(plot_data.q.get(True))
            content_y = np.asarray(content_y)
            bound = plot_data.x_data[-1] + 1
            # create a list with the same dimensions as content_y and as start value the last one of x_data
            content_x = list(range(bound, bound + len(content_y)))
            # remove as many elements from the list as new ones are added
            plot_data.x_data = plot_data.x_data[len(content_x):]
            # append the new values
            plot_data.x_data += content_x
            # add same amount of 0 at the end of the array, as new values are going to be added to the array
            plot_data.y_data = np.append(plot_data.y_data[len(content_y):], [0.0] * len(content_y))
            # overwrite the last elements with the new values
            plot_data.y_data[-len(content_y):] = content_y
            # replot data
            plot_data.line = live_plotter(plot_data)
        # draw canvas
        fig.canvas.draw()


def connect_queue(queue: queue.Queue, plot_label, subplot_index):
    """
    Creates a PlotData object for the queue and assigns the queue to a subplot.
    :param queue: queue which should be plotted
    :param plot_label: class name
    :param subplot_index: position of th subplot
    """
    while not fig:
        time.sleep(0.05)
    if plot_label in plots:
        ax = plots.get(plot_label)
    else:
        ax = fig.add_subplot(subplot_index)
        ax.set_xlabel('Time')
        ax.set_ylabel(plot_label)
        plots[plot_label] = ax
    queues.append(PlotData(queue, ax, plot_label))


def start_live_plot(figure):
    """
    Initializes plot window.
    """
    global fig
    fig = figure
