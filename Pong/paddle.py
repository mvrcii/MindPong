# Define paddle properties and functions
class Paddle:
    def __init__(self, canvas, width, height, color):
        self.canvas = canvas
        self.canvas_width = canvas.winfo_reqwidth()
        self.canvas_height = canvas.winfo_reqheight()
        self.width = width
        self.id = canvas.create_rectangle(0, 0, width, height, fill=color)
        self.canvas.move(self.id, (self.canvas_width - self.width) / 2, self.canvas_height * 0.9)
        self.x_speed = 0
        self.canvas.bind_all('<KeyPress-Left>', self.move_left)
        self.canvas.bind_all('<KeyPress-Right>', self.move_right)

    def update(self, delta_time):
        pos = self.canvas.coords(self.id)
        if pos[0] <= 0:
            self.x_speed = 0
        if pos[2] >= self.canvas_width:
            self.x_speed = 0

    def draw(self):
        self.canvas.move(self.id, self.x_speed, 0)

    def move_left(self, evt):
        self.canvas.move(self.id, -10, 0)

    def move_right(self, evt):
        self.canvas.move(self.id, 10, 0)
