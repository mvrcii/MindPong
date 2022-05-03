import queue
import time
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# constants
AXES_SIZE = 200
MIN_Y_BORDER_SCALING = -1
MAX_Y_BORDER_SCALING = 1

# global data
queues = list()
fig = None
plots = dict()

# necessary!!! to make sure the backend is the correct one
matplotlib.use('TkAgg')
# set matplotlib theme
pth = Path(__file__).resolve().parent
styles_dir = Path(pth / 'themes')
style_path = styles_dir / 'liveplot_light.mplstyle'
plt.style.use(str(style_path))


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

    def __init__(self, q: queue.Queue, ax, plot_label, colour, name):
        self.q = q
        self.ax = ax
        self.designation = name
        self.x_data = list(range(AXES_SIZE))
        # initialize label with -1 alias not defined
        self.y_data = np.zeros(AXES_SIZE) if plot_label != 'label' else np.full(AXES_SIZE, -1)
        # use straight edges for label
        if plot_label == 'label':
            self.line, = ax.step(self.x_data, self.y_data, color=colour,  label=self.designation)
        else:
            self.line, = ax.plot(self.x_data, self.y_data, color=colour, label=self.designation)
        self.color = colour
        self.title = plot_label


def live_plotter(plot_data: PlotData):
    """
    Updates the plot line and the x-axes label and automatically adjusts the boundaries.
    :param plot_data: requires a PlotData object
    :return PlotData.line: 2D-Line
    """
    # after the figure, axis, and line are created, we only need to update the y-data
    plot_data.line.set_ydata(plot_data.y_data)

    # find coherent graph's in subplots
    share_plot_object = None
    # check if there is another plot_data object in queue which has the same title
    # it is assumed that there are only 2 graphs in a plot for the sake of clarity
    for plotdata_object in queues:
        if plotdata_object.title == plot_data.title and plotdata_object != plot_data:
            share_plot_object = plotdata_object
            break

    if share_plot_object is not None:
        # determine the min and max from both graphs within one plot
        min_value = min(np.min(plot_data.y_data), np.min(plotdata_object.y_data))
        max_value = max(np.max(plot_data.y_data),  np.max(plotdata_object.y_data))

        # adjust limits if new data goes beyond bounds, borders are defined within
        # MIN_Y_BORDER_SCALING and MAX_Y_BORDER_SCALING constants which means the scaling of the y-axis doesn't go
        # above or below that range
        if min_value <= plot_data.line.axes.get_ylim()[0] or max_value >= plot_data.line.axes.get_ylim()[1]:
            plot_data.ax.set_ylim([min(min_value - np.std(plot_data.y_data), MIN_Y_BORDER_SCALING), max(max_value + np.std(plot_data.y_data), MAX_Y_BORDER_SCALING)])
        elif min_value >= plot_data.line.axes.get_ylim()[0] or max_value <= plot_data.line.axes.get_ylim()[1]:
            plot_data.ax.set_ylim([min(min_value - np.std(plot_data.y_data), MIN_Y_BORDER_SCALING), max(max_value + np.std(plot_data.y_data), MAX_Y_BORDER_SCALING)])

    # return line, so we can update it again in the next iteration
    return plot_data.line


def perform_live_plot():
    """
    Periodically plots new values from each queue in queues.
    """
    global fig, queues
    if fig:
        has_changes = False
        for plot_data in queues:
            if plot_data.q.empty():
                # skip if queue has no new values
                continue
            has_changes = True
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
            # replot data and legend
            plot_data.line = live_plotter(plot_data)
            # show legend with graph description
            plot_data.ax.legend(loc='upper left')
        if has_changes:
            # draw canvas only if values have changed
            fig.canvas.draw()


def remove_all_plots():
    global queues, plots, fig
    if fig:
        fig.clf()
        queues = list()
        plots = dict()


def connect_queue(queue: queue.Queue, plot_label, row: int, color: str, name: str, column: int, position: int, y_labels:list = None):
    """
    Creates a PlotData object for the queue and assigns the queue to a subplot.
    :param color: color of the plotted line graph
    :param name: name of the plotted line graph
    :param y_labels: custom y lables
    :param position: Position of the subplot, counting from right to left and from top to bottom.
    :param column: arrangement of the subplot in the corresponding column
    :param row: arrangement of the subplot in the corresponding row
    :param queue: queue which should be plotted
    :param plot_label: class name
    """
    if plot_label in plots:
        ax = plots.get(plot_label)
    else:
        ax = fig.add_subplot(row, column, position)
        ax.set_title(plot_label)
        ax.axes.xaxis.set_ticklabels([])
        if y_labels:
            ax.set_ylim(-1.1, 1.1)
            ax.set_yticks([-1, 0, 1])
            ax.set_yticklabels(y_labels)
        plots[plot_label] = ax
    queues.append(PlotData(queue, ax, plot_label, color, name))


def start_live_plot(figure):
    """
    Initializes plot window.
    """
    global fig, queues, plots
    fig = figure
