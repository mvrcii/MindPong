import queue
from scripts.data.visualisation.liveplot_matlab import connect_queue, remove_all_plots, initial_draw

"""Class to handle the Queues for the live plot"""


class QueueManager:
    def __init__(self):
        self.queue_label = queue.Queue(100)
        self.queue_clabel = queue.Queue(100)

        self.queue_c3_pow = queue.Queue(100)
        self.queue_c4_pow = queue.Queue(100)

        self.queue_hcon = queue.Queue(100)
        self.queue_hcon_stand = queue.Queue(100)

    def clear_all_queues(self):
        self.queue_label.queue.clear()
        self.queue_clabel.queue.clear()
        self.queue_c3_pow.queue.clear()
        self.queue_c4_pow.queue.clear()
        self.queue_hcon.queue.clear()
        self.queue_hcon_stand.queue.clear()

    def connect_queues(self):
        self.clear_all_queues()
        remove_all_plots()
        connect_queue(self.queue_c3_pow, 'pow', color='#0096db', row=3, column=1, position=1, name='C3 pow')
        connect_queue(self.queue_c4_pow, 'pow', color='#009d6b', row=3, column=1, position=1, name='C4 pow')
        connect_queue(self.queue_hcon, 'hcon', color='#f17a2c', row=3, column=1, position=2, name='hcon')
        connect_queue(self.queue_hcon_stand, 'hcon', color='#FFC107', row=3, column=1, position=2, name='hcon normalized')
        connect_queue(self.queue_clabel, 'label', color='#96669e', row=3, column=1, position=3, y_labels=['n', 'l', 'r'], name='calculated label')
        initial_draw()
