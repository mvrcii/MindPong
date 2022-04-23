import queue
import threading
import time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
# source and idea from https://makersportal.com/blog/2018/8/14/real-time-graphing-in-python

plt.style.use('ggplot')
# necessary!!! to make sure the backend ist the correct one
matplotlib.use('TkAgg')
queues = list()
size = 100
x_data = list(range(100))
fig = plt.figure(tight_layout=True)
ax = None
q1 = queue.Queue(100)
q2 = queue.Queue(100)


class PlotData:
    def __init__(self, q: queue.Queue):
        self.q = q
        self.y_data = np.zeros(size)
        print(type(ax))
        self.line, = ax.plot(x_data, self.y_data)


def live_plotter(plot_data: PlotData, x_data):
    # after the figure, axis, and line are created, we only need to update the y-data
    plot_data.line.set_ydata(plot_data.y_data)
    # adjust limits if new data goes beyond bounds
    if np.min(plot_data.y_data) <= plot_data.line.axes.get_ylim()[0] or np.max(plot_data.y_data) >= plot_data.line.axes.get_ylim()[1]:
        plt.ylim([np.min(plot_data.y_data) - np.std(plot_data.y_data), np.max(plot_data.y_data) + np.std(plot_data.y_data)])

    # ascending x-values only the label a changes the x-range remains the same
    # TODO: listen to the warning and Use a FixedLocator
    plot_data.line.axes.set_xticklabels(x_data)
    # return line, so we can update it again in the next iteration
    return plot_data.line


def do_live_plot():
    global x_data, fig, queues
    while True:
        # necessary if you want to get out of the endless loop after the figure is closed
        if not plt.get_fignums():
            break
        try:
            x_data = x_data[1:]  # Remove the first y element.
            x_data.append(x_data[-1] + 1)
            for plot_data in queues:
                new_val = plot_data.q.get_nowait()
                plot_data.y_data[-1] = new_val
                plot_data.line = live_plotter(plot_data, x_data)
                plot_data.y_data = np.append(plot_data.y_data[1:], 0.0)
            plt.pause(0.1)
        except queue.Empty:
            time.sleep(0.01)


def connect_queue(toggle_plot, queue: queue.Queue):
    while not ax:
        time.sleep(0.1)
    queues.append(PlotData(queue))


def start_live_plot(identifier='Signal Plot'):
    global fig, ax
    # this is the call to matplotlib that allows dynamic plotting
    plt.ion()
    ax = fig.add_subplot(111)
    # update plot label/title
    plt.ylabel('Time')
    plt.title('{}'.format(identifier))
    # to maximize figure, but it shows a strange behavior
    # mng = plt.get_current_fig_manager()
    # mng.resize(*mng.window.maxsize())
    plt.show()
    # start liveplot
    do_live_plot()


# fill queue for testing purposes with random values
def handle_queue():
    global q1, q2
    connect_queue(None, q1)
    connect_queue(None, q2)
    while True:
        rand_val = np.random.randn(1)
        try:
            q1.put(rand_val)
            q2.put(rand_val + 2)
            # print('Alive')
        except queue.Empty:
            time.sleep(0.005)


if __name__ == '__main__':
    threading.Thread(target=handle_queue, daemon=True).start()
    start_live_plot()
