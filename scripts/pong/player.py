import select
import time

import scripts.pong.game as game
import scripts.config as config

import scripts.data.extraction.trial_handler as trial_handler
from scripts.mvc.models import ConfigData


# Define player properties and functions
class Player:
    """
    A Class to create the player

    Methods:
    ----------
    :method update(self, delta_time): Update velocity according to the time
    :method calculate_velocity(self): Calculate velocity
    :method draw(self): Draw the plyer
    :method reset(self): Reset the player
    :method init(self): Initializes the player object and its position
    :method move_left(self, evt): Moves player left
    :method move_right(self, evt): Moves player right
    :method collision_with_target(self): checks collision with target
    :method start_trial(self): sets the timestamp of the start of a trial
    :method is_trial_valid(self): checks if the trial is still valid (player moves to target)
    :method stop_trial(self): stops trial recording and saves valid trials
    """

    def __init__(self, root, canvas, width, height, color, target, strategy):
        """
        Constructor method
        :param Any root: root
        :param Any canvas: Canvas for drawing
        :param Any width: width of player
        :param Any height: height of player
        :param Any color: color of player
        :param Any target: target
        :param Any strategy: strategy for player movement
        :attribute Any self.root: Root
        :attribute Any self.canvas: Canvas
        :attribute Any self.canvas:width: Canvas width
        :attribute Any self.height: Canvas height
        :attribute Any self.color: Color of the player
        :attribute Any self.width: Width of the player
        :attribute Any self.height: Height of the player
        :attribute None self.pos: Position of the player in x axis
        :attribute int self.speed_factor: Speed factor
        :attribute None self.id: ID
        :attribute int self.root: Root
        :attribute int self.velocity_x_axis: velocity in x axis
        :attribute int self.direction: Direction of player movement
        :attribute bool self.wall_hit: Had the player an hit with the wall
        :attribute bool self.start_pos: Is player at the start position
        :attribute bool self.direction_update: Occurred a direction update
        :attribute Any self.target: target of the game
        :attribute bool self.hit_occurred: Occurred a hit with the target
        :attribute Any self.start_time_trial: timestamp of the start of a trial in s
        :attribute int self.last_direction_update: last direction update
        :attribute Label self.trial_label: type of the event in the trial
        """

        self.root = root
        self.canvas = canvas
        self.config_data = self.root.config_data
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
        self.start_time_trial = time.time()
        self.last_direction_update = 0
        self.trial_label = trial_handler.Labels.INVALID
        self.y_pos = self.canvas_height * 0.5 - self.height

        self.request(strategy).control(self)

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
        Update the delta time (time between now and the time at the last update)
        :param delta_time: delta time for velocity x-axis
        """
        self.velocity_x_axis = self.calculate_velocity() * delta_time

        self.collision_with_target()

        # every time the direction is not updated the player gets slower
        if self.direction_update:
            self.direction_update = False
            self.speed_factor = 1
        else:
            self.speed_factor -= (delta_time * 4) / config.TIME_TO_STOP_PLAYER
            # prevents the speed_factor from becoming negative
            if self.speed_factor <= 0:
                self.speed_factor = 0

    def calculate_velocity(self):
        """
        Calculates velocity of the player depending on his direction and whether he should be stopped
        :return: Calculated velocity
        :rtype: int
        """
        if self.start_pos:
            return 0

        if self.direction == 1:
            if self.pos[2] + (self.velocity_x_axis * self.speed_factor) >= self.canvas_width:
                if not self.wall_hit:
                    self.wall_hit = True
                return 0
            if self.pos[0] + (self.velocity_x_axis * self.speed_factor) <= 0:
                if not self.wall_hit:
                    self.wall_hit = True
                    return 0
                else:
                    return 1
            else:
                return 1

        elif self.direction == -1:
            if self.pos[0] + (self.velocity_x_axis * self.speed_factor) <= 0:
                if self.wall_hit is False:
                    self.wall_hit = True
                return 0
            elif self.pos[2] + (self.velocity_x_axis * self.speed_factor) >= self.canvas_width:
                if not self.wall_hit:
                    self.wall_hit = True
                    return 0
                else:
                    return -1
            else:
                return -1

    def draw(self):
        """Draw the player"""
        vorher = self.pos[0]
        self.canvas.move(self.id, self.velocity_x_axis * self.speed_factor, 0)
        self.pos = self.canvas.coords(self.id)
        if self.pos[0] <= 0:
            print("Vorher: ", vorher, "Nacher: ", self.pos[0])

    def reset(self):
        """Reset the player"""

        self.canvas.delete(self.id)
        self.start_pos = True
        self.speed_factor = 1
        self.init()

    def init(self):
        """Initializes the player object and its position"""

        self.id = self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.color)
        # Move to initial position
        self.canvas.move(self.id, (self.canvas_width - self.width) / 2, self.y_pos)
        # Update position
        self.pos = self.canvas.coords(self.id)
        self.target.spawn_new_target(self.pos)

    def move_left(self, event=None):
        """Move player left"""

        # Prevent player movement while the game state is not playing
        if self.root.state.name is not game.Playing.name:
            return

        if self.start_pos:
            self.start_pos = False
        self.direction = -1
        self.direction_update = True

        # Checks only if the trial is valid if trials are recorded
        if self.root.data.trial_recording:
            self.is_trial_valid()

    def move_right(self, event=None):
        """Move player right"""

        # Prevent player movement while the game state is not playing
        if self.root.state.name is not game.Playing.name:
            return

        if self.start_pos is True:
            self.start_pos = False
        self.direction = 1
        self.direction_update = True

        # Checks only if the trial is valid if trials are recorded
        if self.root.data.trial_recording:
            self.is_trial_valid()

    def collision_with_target(self):
        """
        (1) Detects if target is hit
        (2) Initiates the handling of the hit
        """
        hit_from_right = self.target.pos[0] <= self.pos[2]+(self.velocity_x_axis * self.speed_factor) <= self.target.pos[2]
        hit_from_left = self.target.pos[2] >= self.pos[0]+(self.velocity_x_axis * self.speed_factor) >= self.target.pos[0]
        if hit_from_left or hit_from_right:
            self.velocity_x_axis = 0
            self.root.change(game.Hit)
            if hit_from_left:
                self.canvas.moveto(self.id, self.target.pos[2], self.y_pos)
            else:
                self.canvas.moveto(self.id, self.target.pos[0]-self.width, self.y_pos)

    def start_trial(self):
        """Saves the timestamp by the start of a trial"""
        self.start_time_trial = time.time()

    def is_trial_valid(self):
        """
        1. Checks if a trial is still valid during his recording
            a) At the start of a trial it checks if the player is moving in the direction of the player
            b) During the recording it checks if the player is still moving in the right direction
        2. Stops the trial recording if the trial is not valid anymore
        """
        # Trial has not started
        if self.last_direction_update == 0:
            # Target is right and player moves to the right
            if self.pos[0] < self.target.pos[0] and self.direction == 1:
                self.trial_label = trial_handler.Labels.RIGHT
                self.start_trial()
                self.last_direction_update = self.direction
            # Target is left and player moves to the left
            elif self.pos[0] > self.target.pos[0] and self.direction == -1:
                self.trial_label = trial_handler.Labels.LEFT
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
        """Stops the recording of a trial and stores valid trials"""
        stop_time_trial = time.time()
        if (stop_time_trial - self.start_time_trial) > self.config_data.trial_min_duration/1000 and self.last_direction_update != 0:
            trial_handler.mark_trial(self.start_time_trial, stop_time_trial, self.trial_label)
            print("Valid trial is stored")
        self.last_direction_update = 0
