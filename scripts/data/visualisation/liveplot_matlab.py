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
queues = []
line1 = []
size = 100
x_label = list(range(size))
q = queue.Queue(size)
x_vec = np.linspace(0, 100, size + 1)[0:-1]  # scaling of x-axis
y_vec = np.zeros(size)
fig = plt.figure(tight_layout=True)


def live_plotter(identifier='', pause_time=0.1):
    global x_vec, y_vec, line1
    y1_data = y_vec

    if line1 == []:
        global fig, x_label
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        ax = fig.add_subplot(111)
        # create a variable for the line, so we can later update it
        line1, = ax.plot(x_vec, y1_data, '-o', alpha=0.8)
        # update plot label/title
        plt.ylabel('Time')
        plt.title('Signal Plot'.format(identifier))
        # to maximize figure, but it shows a strange behavior
        # mng = plt.get_current_fig_manager()
        # mng.resize(*mng.window.maxsize())
        plt.show()

    # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    # adjust limits if new data goes beyond bounds
    if np.min(y1_data) <= line1.axes.get_ylim()[0] or np.max(y1_data) >= line1.axes.get_ylim()[1]:
        plt.ylim([np.min(y1_data) - np.std(y1_data), np.max(y1_data) + np.std(y1_data)])

    # ascending x-values only the label a changes the x-range remains the same
    x_label = x_label[1:]  # Remove the first y element.
    x_label.append(x_label[-1] + 1)
    # TODO: listen to the warning and Use a FixedLocator
    line1.axes.set_xticklabels(x_label)

    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    # return line so we can update it again in the next iteration
    return line1


# fill queue for testing purposes with random values
def create_values():
    while True:
        rand_val = np.random.randn(1)
        try:
            q.put(rand_val)
            # print('Alive')
        except queue.Empty:
            time.sleep(0.005)


def do_live_plot():
    global y_vec, x_vec, line1, fig
    while True:
        # necessary if you want to get out of the endless loop after the figure is closed
        if not plt.get_fignums():
            break
        try:
            rand_val = q.get_nowait()
            y_vec[-1] = rand_val
            line1 = live_plotter()
            y_vec = np.append(y_vec[1:], 0.0)

        except queue.Empty:
            time.sleep(0.005)


if __name__ == '__main__':

    threading.Thread(target=create_values, daemon=True).start()
    do_live_plot()
