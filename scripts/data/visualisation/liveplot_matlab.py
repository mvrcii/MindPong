import queue
import threading
import time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('ggplot')
# necessary!!! to make sure the backend ist the correct one
matplotlib.use('TkAgg')
queues = list()
size = 200
fig = plt.figure(tight_layout=True, figsize=(8, 8))
q1 = queue.Queue(100)
q2 = queue.Queue(100)
qm = None
plots = dict()


class PlotData:
    def __init__(self, q: queue.Queue, ax, plot_label):
        self.q = q
        self.ax = ax
        self.x_data = list(range(size))
        self.y_data = np.zeros(size)
        self.line, = ax.plot(self.x_data, self.y_data)
        self.name = plot_label


def live_plotter(plot_data: PlotData, x_data):
    # after the figure, axis, and line are created, we only need to update the y-data
    plot_data.line.set_ydata(plot_data.y_data)
    # adjust limits if new data goes beyond bounds
    if np.min(plot_data.y_data) <= plot_data.line.axes.get_ylim()[0] or np.max(plot_data.y_data) >= plot_data.line.axes.get_ylim()[1]:
        plot_data.ax.set_ylim([np.min(plot_data.y_data) - np.std(plot_data.y_data), np.max(plot_data.y_data) + np.std(plot_data.y_data)])

    # ascending x-values only the label a changes the x-range remains the same
    # TODO: listen to the warning and Use a FixedLocator
    plot_data.line.axes.set_xticklabels(x_data)
    # return line, so we can update it again in the next iteration
    return plot_data.line


def do_live_plot(pause_time):
    global fig, queues
    while True:
        # necessary if you want to get out of the endless loop after the figure is closed
        if not plt.get_fignums():
            break
        for plot_data in queues:
            if plot_data.q.empty():
                continue
            if plot_data.name == 'pow':
                print('Ist was drin')
            content_y = np.asarray(list(plot_data.q.queue))
            plot_data.q.queue.clear()
            bound = plot_data.x_data[-1] + 1
            content_x = list(range(bound, bound+ len(content_y)))  # creates a list with the same dimensions as content_y and as start value the last one of x_data
            plot_data.x_data = plot_data.x_data[len(content_x):]  # takes as many elements from the list as new ones are added
            plot_data.x_data += content_x                         # append the new values
            plot_data.y_data = np.append(plot_data.y_data[len(content_y):], [0.0] * len(content_y)) # concatenate 2 arrays
            plot_data.y_data[-len(content_y):] = content_y          # overwrites the last elements with the new values
            plot_data.line = live_plotter(plot_data, plot_data.x_data)

            print()
        plt.pause(pause_time)


def connect_queue(toggle_plot, queue: queue.Queue, plot_label, subplot_index):
    if plot_label in plots:
        ax = plots.get(plot_label)
    else:
        ax = fig.add_subplot(subplot_index)
        ax.set_xlabel(plot_label)
        ax.set_ylabel('Time')
        plots[plot_label] = ax
    queues.append(PlotData(queue, ax, plot_label))


def start_live_plot(queue_manager, pause_time):
    global fig, qm
    qm = queue_manager
    # this is the call to matplotlib that allows dynamic plotting
    plt.ion()
    plt.show()
    # start liveplot
    do_live_plot(pause_time)


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
