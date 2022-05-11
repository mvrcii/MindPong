import queue
import sys
import time

import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore

main_window = None
queues = list()
is_window_ready = False


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))

        self.graphWidget.setYRange(-1.1, 1.1)
        self.graphWidget.addLegend()

        self.graphWidget.setBackground('k')
        # self.graphWidget.showGrid(x=True, y=True)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def add_plot(self, queue):
        global queues
        plot = self.graphWidget.plot(self.x, list(queue[2].queue), name=queue[0], pen=pg.mkPen(width=2, color=queue[1]))
        queues.append((queue[2], plot, list(range(100))))

    def update_plot_data(self):
        """
        Periodically called to update the values by extracting the current values from the queues.
        """
        try:
            global queues
            # update x value
            self.x = self.x[1:]  # Remove the first y element.
            self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

            for index, queueItem in enumerate(queues):
                # update values
                q = queueItem[0]
                plot = queueItem[1]
                data_line = queueItem[2]

                data_line = data_line[1:]  # Get and remove the first element of the queue
                data_line.append(q.get())
                plot.setData(self.x, data_line)  # Update the data.
                queues[index] = (q, plot, data_line)
        except:
            time.sleep(0.005)


def add_queue(q: (str, str, queue.Queue)):
    """
    Adds a queue to the live plot
    :param q: consists of the name of the label and the corresponding queue
    """
    global main_window
    if main_window:
        main_window.add_plot(q)


def start_liveplot():
    """
    starts the live plot window
    """
    global main_window
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    main_window.showFullScreen()
    global is_window_ready
    is_window_ready = True
    window = app.exec_()
    sys.exit(window)
