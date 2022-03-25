# Define paddle properties and functions
class Paddle:
    def __init__(self, canvas, width, height, color):
        self.canvas = canvas
        self.canvas_width = canvas.winfo_reqwidth()
        self.canvas_height = canvas.winfo_reqheight()
        self.color = color
        self.width = width
        self.height = height
        self.pos = None
        self.speed_factor = 1
        self.id = None

        self.v_x = 0
        self.direction = 0
        self.wall_hit = False
        self.start_pos = True

        self.canvas.bind_all('<KeyPress-Left>', self.move_left)
        self.canvas.bind_all('<KeyPress-Right>', self.move_right)

        self.init()

    def update(self, delta_time):
        self.v_x = self.calculate_velocity() * delta_time

    def calculate_velocity(self):
        if self.start_pos is True:
            return 0

        if self.direction == 1:
            if self.pos[2] >= self.canvas_width:
                if self.wall_hit is False:
                    self.wall_hit = True
                return 0
            if self.pos[0] <= 0:
                if self.wall_hit is False:
                    self.wall_hit = True
                    return 0
                else:
                    return 1
            else:
                return 1

        elif self.direction == -1:
            if self.pos[0] <= 0:
                if self.wall_hit is False:
                    self.wall_hit = True
                return 0
            elif self.pos[2] >= self.canvas_width:
                if self.wall_hit is False:
                    self.wall_hit = True
                    return 0
                else:
                    return -1
            else:
                return -1

    def draw(self):
        self.canvas.move(self.id, self.v_x, 0)
        self.pos = self.canvas.coords(self.id)

    def reset(self):
        self.canvas.delete(self.id)
        self.start_pos = True
        self.init()

    def init(self):
        """Initializes the paddle object and its position."""
        self.id = self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.color)
        # Move to initial position
        self.canvas.move(self.id, (self.canvas_width - self.width) / 2, self.canvas_height * 0.9)
        # Update position
        self.pos = self.canvas.coords(self.id)

    def move_left(self, evt):
        if self.start_pos is True:
            self.start_pos = False
        self.direction = -1

    def move_right(self, evt):
        if self.start_pos is True:
            self.start_pos = False
        self.direction = 1

