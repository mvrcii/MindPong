import queue
import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import time

MAIN_WINDOW = None
QUEUES = list()
WINDOW_READY = False


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))

        # self.graphWidget.setYRange(-10, 10)
        self.graphWidget.addLegend()

        self.graphWidget.setBackground('k')
        # self.graphWidget.showGrid(x=True, y=True)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def add_plot(self, queues):
        global QUEUES
        plot = self.graphWidget.plot(self.x, list(queues[2].queue), name=queues[0], pen=pg.mkPen(width=2, color=queues[1]))
        QUEUES.append((queues[2], plot, list(range(100))))

    def update_plot_data(self):
        """
        Periodically called to update the values by extracting the current values from the queues.
        """
        try:
            global QUEUES
            # update x value
            self.x = self.x[1:]  # Remove the first y element.
            self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

            for index, queueItem in enumerate(QUEUES):
                # update values
                q = queueItem[0]
                plot = queueItem[1]
                data_line = queueItem[2]

                data_line = data_line[1:]  # Get and remove the first element of the queue
                data_line.append(q.get())
                plot.setData(self.x, data_line)  # Update the data.
                QUEUES[index] = (q, plot, data_line)
        except:
            time.sleep(0.005)


def add_queue(q: (str, str, queue.Queue)):
    """
    Adds a queue to the live plot
    :param q: consists of the name of the label and the corresponding queue
    """
    global MAIN_WINDOW
    if MAIN_WINDOW:
        MAIN_WINDOW.add_plot(q)


def start_liveplot():
    """
    starts the live plot window
    """
    global MAIN_WINDOW
    app = QtWidgets.QApplication(sys.argv)
    MAIN_WINDOW = MainWindow()
    MAIN_WINDOW.show()
    global WINDOW_READY
    WINDOW_READY = True
    window = app.exec_()
    sys.exit(window)
