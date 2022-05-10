import random
import scripts.pong.game as game
import scripts.config as config


class Target:
    """
    Target class

    Methods:
    ----------
    method: update(delta_time): handles time for new spawn
    method: spawn_new_target(player_pos): spawns the target at a random postion
    """

    def __init__(self, root, canvas, color, size):
        self.start_distance = 0
        self.root = root
        self.canvas = canvas
        self.canvas_width = canvas.winfo_reqwidth()
        self.canvas_height = canvas.winfo_reqheight()
        self.color = color
        self.size = size
        self.pos = None
        self.id = self.canvas.create_oval(0, 0, self.size, self.size, fill=self.color)
        self.pos = self.canvas.coords(self.id)
        self.time_last_hit = 0

    def update(self, delta_time):
        """
        handle time for a new spawn when target was not reached in time
        :param delta_time:
        """
        self.time_last_hit += delta_time
        if self.time_last_hit >= config.TIME_TO_CATCH_PER_PIXEL * self.start_distance:
            self.root.miss += 1
            self.root.change(game.Respawn)

    def spawn_new_target(self, player_pos):
        """
        Spawns a new target with a random position with a min. distance
        :param player_pos: position of the player object
        """
        offset_border = 70.0  # Offset to prevent that the text is in the border
        min_x = 0
        max_x = self.canvas_width - self.size

        condition = True
        while condition:
            random_x = random.uniform(min_x, max_x)
            if (random_x + (self.size / 2) + offset_border + config.MIN_DISTANCE_TARGET) <= player_pos[0]:
                condition = False
                self.start_distance = player_pos[0] - random_x
            elif (random_x - (self.size / 2) - offset_border - config.MIN_DISTANCE_TARGET) >= player_pos[2]:
                condition = False
                self.start_distance = random_x - player_pos[2]

        self.canvas.itemconfig(self.id, fill='red')
        self.time_last_hit = 0
        self.canvas.moveto(self.id, random_x, self.canvas_height * 0.5 - self.size)
        self.pos = self.canvas.coords(self.id)
