import scripts.pong.main as main


# Define paddle properties and functions
class Paddle:
    """
    A Class to create the paddle

    Methods:
    ----------
    :method update(self, delta_time): Update velocity according to the time
    :method calculate_velocity(self): Calculate velocity
    :method draw(self): Draw the paddle
    :method reset(self): Reset the paddle
    :method init(self): Initializes the paddle object and its position
    :method move_left(self, evt): Move paddle left
    :method move_right(self, evt): Move paddle right
    """

    def __init__(self, root, canvas, width, height, color):
        """
        Constructor method
        :param Any root: root
        :param Any canvas: Canvas for drawing
        :param Any width: width of paddle
        :param Any height: height of paddle
        :param Any color: color of paddle
        """

        self.root = root
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
        """
        Update the delta time
        :param delta_time: delta time for velocity x-axis
        :return: None
        """

        self.v_x = self.calculate_velocity() * delta_time

    def calculate_velocity(self):
        """
        Calculate the velocity
        :return: velocity
        :rtype: int
        """

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
        """
        Draw the paddle
        :return: None
        """

        self.canvas.move(self.id, self.v_x * self.speed_factor, 0)
        self.pos = self.canvas.coords(self.id)

    def reset(self):
        """
        Reset the paddle
        :return: None
        """

        self.canvas.delete(self.id)
        self.start_pos = True
        self.speed_factor = 1
        self.init()

    def init(self):
        """
        Initializes the paddle object and its position
        :return: None
        """

        self.id = self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.color)
        # Move to initial position
        self.canvas.move(self.id, (self.canvas_width - self.width) / 2, self.canvas_height * 0.9)
        # Update position
        self.pos = self.canvas.coords(self.id)

    def move_left(self, evt):
        """
        Move paddle left
        :return: None
        """

        # Prevent paddle movement while the game state is not playing
        if self.root.state.name is not main.Playing.name:
            return
        if self.start_pos:
            self.start_pos = False
        self.direction = -1

    def move_right(self, evt):
        """
        Move paddle right
        :return: None
        """

        # Prevent paddle movement while the game state is not playing
        if self.root.state.name is not main.Playing.name:
            return
        if self.start_pos is True:
            self.start_pos = False
        self.direction = 1

