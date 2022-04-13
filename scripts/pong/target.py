import random
from scripts.config import MIN_DISTANCE_TARGET


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

    def spawn_new_target(self, player_pos):
        min_x = self.size / 2
        max_x = self.canvas_width - (self.size / 2)
        condition = True
        while condition:
            random_x = random.uniform(min_x, max_x)
            print(random_x)
            if (random_x + (self.size / 2) + MIN_DISTANCE_TARGET) <= player_pos[0] or (
                    random_x - (self.size / 2) - MIN_DISTANCE_TARGET) >= player_pos[2]:
                condition = False
        print('out of while')
        self.canvas.move(self.id, random_x, self.canvas_height * 0.5)
        self.pos = self.canvas.coords(self.id)
