import random
import time

from scripts.config import *


class Target:
    def __init__(self, root, canvas, color, size):

        self.canvas = canvas
        self.canvas_width = canvas.winfo_reqwidth()
        self.canvas_height = canvas.winfo_reqheight()
        self.color = color
        self.size = size
        self.pos = None
        self.id = self.canvas.create_oval(0, 0, self.size, self.size, fill=self.color)
        self.pos = self.canvas.coords(self.id)
        self.hit_player_target = False
        self.spawn_target = False
        self.counter = 0
        self.timestamp_last_hit = time.time()

    def update(self, delta_time):
        if self.hit_player_target:
            self.canvas.itemconfig(self.id, fill='green')
            if self.counter >= TIME_NEW_SPAWN:
                self.hit_player_target = False
                self.spawn_target = True
                self.counter = 0
                self.timestamp_last_hit = None
            else:
                self.counter += delta_time
        elif (time.time() - self.timestamp_last_hit) >= TIME_TO_CATCH:
            self.spawn_target = True

    def spawn_new_target(self, player_pos):
        min_x = 0
        max_x = self.canvas_width - self.size
        condition = True
        while condition:
            random_x = random.uniform(min_x, max_x)
            print(random_x)
            if (random_x + (self.size / 2) + MIN_DISTANCE_TARGET) <= player_pos[0] or (
                    random_x - (self.size / 2) - MIN_DISTANCE_TARGET) >= player_pos[2]:
                condition = False
        self.canvas.itemconfig(self.id, fill='red')
        self.timestamp_last_hit = time.time()
        self.canvas.moveto(self.id, random_x, self.canvas_height * 0.5)
        self.pos = self.canvas.coords(self.id)
