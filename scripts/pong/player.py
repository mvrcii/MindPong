import time
from enum import Enum

import scripts.pong.game as game
import scripts.pong.target as target
from scripts.config import *

import scripts.data.extraction.trial_handler as trial_handler


class Labels(Enum):
    INVALID = 99
    LEFT = 0
    RIGHT = 1
    EYES_OPEN = 2
    EYES_CLOSED = 3

# Define paddle properties and functions
class Player:
    """
    A Class to create the player

    Methods:
    ----------
    :method update(self, delta_time): Update velocity according to the time
    :method calculate_velocity(self): Calculate velocity
    :method draw(self): Draw the paddle
    :method reset(self): Reset the paddle
    :method init(self): Initializes the paddle object and its position
    :method move_left(self, evt): Move paddle left
    :method move_right(self, evt): Move paddle right
    :method collision_with_target(self): checks collision with target
    """

    def __init__(self, root, canvas, width, height, color, target, strategy):
        """
        Constructor method
        :param Any root: root
        :param Any canvas: Canvas for drawing
        :param Any width: width of player
        :param Any height: height of player
        :param Any color: color of player
        :attribute Any self.root: Root
        :attribute Any self.canvas: Canvas
        :attribute Any self.canvas:width: Canvas width
        :attribute Any self.height: Canvas height
        :attribute Any self.color: Color
        :attribute Any self.width: Width
        :attribute Any self.height: Height
        :attribute None self.pos: Position
        :attribute int self.speed_factor: Speed factor
        :attribute None self.id: Id
        :attribute int self.root: Root
        :attribute int self.v_x: v_x
        :attribute int self.direction: Direction
        :attribute bool self.wall_hit: Wall hit
        :attribute bool self.start_pos: Start position
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
        self.velocity_x_axis = 0
        self.direction = 0
        self.wall_hit = False
        self.start_pos = True
        self.direction_update = False
        self.target = target
        self.hit_occurred = False
        self.start_time_trial = time.time()
        self.trial_is_valid = True
        self.last_direction_update = 0
        self.trial_label = Labels.INVALID

        self.request(strategy).__str__(self)

        self.init()

    @staticmethod
    def request(strategy):
        """
        Returns the control strategy that is used for the player movement
        :param strategy: Strategy class to
        :return: Strategy class that is used
        """
        return strategy()

    def update(self, delta_time):
        """
        Update the delta time
        :param delta_time: delta time for velocity x-axis
        :return: None
        """

        self.collision_with_target()
        self.velocity_x_axis = self.calculate_velocity() * delta_time
        # every time the direction is not updated the player gets slower
        if self.direction_update:
            self.direction_update = False
            self.speed_factor = 1
        else:
            self.speed_factor -= (delta_time * 4) / TIME_TO_STOP_PLAYER
            # prevents the speed_factor from becoming negative
            if self.speed_factor <= 0:
                self.speed_factor = 0

        if self.target.spawn_target:
            self.root.change(game.Respawn)
            self.stop_trial()
            self.target.spawn_target = False
            self.hit_occurred = False

    def calculate_velocity(self):
        """
        Calculates velocity of the player depending on his direction and whether he should be stopped
        :return: Calculated velocity
        :rtype: int
        """
        if self.start_pos:
            return 0

        if self.hit_occurred:
            return 0

        if self.direction == 1:
            if self.pos[2] >= self.canvas_width:
                if not self.wall_hit:
                    self.wall_hit = True
                return 0
            if self.pos[0] <= 0:
                if not self.wall_hit:
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
                if not self.wall_hit:
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

        self.canvas.move(self.id, self.velocity_x_axis * self.speed_factor, 0)
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
        self.canvas.move(self.id, (self.canvas_width - self.width) / 2, self.canvas_height * 0.5 - self.height)
        # Update position
        self.pos = self.canvas.coords(self.id)
        self.target.spawn_new_target(self.pos)

    def move_left(self, event):
        """
        Move paddle left
        :return: None
        """

        # Prevent player movement while the game state is not playing
        if self.root.state.name is not game.Playing.name:
            return

        if self.start_pos:
            self.start_pos = False
        self.direction = -1
        self.direction_update = True
        self.is_trial_valid()

    def move_right(self, event):
        """
        Move paddle right
        :return: None
        """

        # Prevent player movement while the game state is not playing
        if self.root.state.name is not game.Playing.name:
            return

        if self.start_pos is True:
            self.start_pos = False
        self.direction = 1
        self.direction_update = True
        self.is_trial_valid()

    def collision_with_target(self):
        """
        (1) Detects if target is hit
        (2) Initiates the handling of the hit
        :return: None
        """
        hit_from_right = self.target.pos[0] <= self.pos[2] <= self.target.pos[2]
        hit_from_left = self.target.pos[2] >= self.pos[0] >= self.target.pos[0]
        if hit_from_left or hit_from_right:
            self.hit_occurred = True
            self.target.respawn()

    def start_trial(self):
        self.start_time_trial = time.time()

    def is_trial_valid(self):
        # Trial has not started
        if self.last_direction_update == 0:
            print(self.pos[0])
            print(self.target.pos[0])
            # Target is right and player moves to the right
            if self.pos[0] < self.target.pos[0] and self.direction == 1:
                print("right")
                self.trial_label = Labels.RIGHT
                self.start_trial()
                self.last_direction_update = self.direction
            # Target is left and player moves to the left
            elif self.pos[0] > self.target.pos[0] and self.direction == -1:
                print("left")
                self.trial_label = Labels.LEFT
                self.start_trial()
                self.last_direction_update = self.direction
        # Player is still moving in the same direction --> Trial is valid
        elif self.last_direction_update == self.direction:
            self.last_direction_update = self.direction
        # Player do not move in the right direction --> Trial is invalid
        else:
            print("Stopped Trial")
            self.stop_trial()

    def stop_trial(self):
        """
        Stops
        :return:
        """
        stop_time_trial = time.time()
        print("stop")
        if (stop_time_trial - self.start_time_trial) > MIN_DURATION_OF_TRIAL and self.last_direction_update is not None:
            #trial_handler.mark_trial(self.start_trial(), stop_time_trial, self.trial_label)
            print("Valid trial is stored")
            print(self.start_time_trial, stop_time_trial, self.trial_label)
        self.last_direction_update = 0
