from enum import Enum
from tkinter import *
import tkinter as tk
import time

import scripts.pong.player as player
import scripts.pong.target as target
import scripts.config as config




class GameState(object):
    """
    A class used to handle the state management in the Game

    Attributes:
    ----------
    name: str
        the name of the state
    allowed: [str]
        a list of the allowed state names to switch to

    Methods:
    ----------
    switch(state):
        Switches the current state to the passed state if it is listed in the allowed states

    """
    name = "state"
    allowed = []

    def switch(self, state):
        """Switches to the given state

        If the argument `state` is not listed in the allowed attribute, the state will not switch.
        Use this method and do not set the state attribute manually
        :param GameState state: the state to switch to
        :return: None
        """

        if state.name in self.allowed:
            print('Current State:', self, ' => switched to new state', state.name)
            self.__class__ = state
            print(self.__class__)
        else:
            print('Current State:', self, ' => switching to', state.name, 'not possible.')

    def __str__(self):
        """
        :return: self.name: attribute name
        :rtype: str
         """
        return self.name


class Playing(GameState):
    """
    A child of GameState defining the state playing
    """
    name = "playing"
    allowed = ['idle', 'hit', 'end', 'respawn']


class Idle(GameState):
    """
    A child of GameState defining the state idle
    """

    name = "idle"
    allowed = ['playing', 'hit', 'respawn', 'end']


class Hit(GameState):
    """A child of GameState defining the state hit"""
    name = "hit"
    allowed = ['idle', 'respawn', 'end']


class Respawn(GameState):
    """A child of GameState defining the state respawn"""
    name = "respawn"
    allowed = ['idle', 'playing', 'end']


class End(GameState):
    """A child of GameState defining the state end"""
    name = "end"
    allowed = []


class Game(tk.Frame):
    """
    A class representing the game

    Methods:
    ----------
    update():
        Calls the update methods of all objects and is responsible for the game loop and state handling
    handle_time():
        Handles the time and returns a delta for correction
    clear():
        Clears the canvas background. Very important function to avoid flickering and artifacts
    change(state):
        Changes the internal state to state if possible
    """

    def __init__(self, parent, controller):
        """
        Constructor method
        :param Any parent: parent
        :param Any controller: controller
        :attribute int self.width: the width of the pong window
        :attribute int self.height: the height of the pong window
        :attribute GameState self.state: the current game state
        :attribute int self.score: the current game score
        :attribute int self.miss: the current amount of missed targets
        :attribute float self.curr_restart_timer: the current restart timer, which will be set to a value and then count down
            until it reaches zero. This variable is also displayed while the game is being restarted
        :attribute int self.update_counter: the tick counter
        :attribute float self.last_update: the timestamp of the last update
        :attribute float self.passed_time: the time that has passed since last_update
        :attribute Canvas self.canvas: the canvas to draw on
        :attribute Player self.player: the player object
        :attribute Target self.target: the target object
        :attribute int self.curr_restart_time: counts time for hit state
        :attribute float[] self.remaining_time_history: list with left over time
        """

        tk.Frame.__init__(self, parent)

        # override window dimensions
        global WINDOW_WIDTH, WINDOW_HEIGHT
        WINDOW_WIDTH = self.winfo_screenwidth()
        WINDOW_HEIGHT = self.winfo_screenheight()
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT

        # State of the game - default is idle
        self.state = Idle()

        self.score = 0
        self.miss = 0

        self.remaining_time_history = []

        self.curr_restart_time = 0

        self.update_counter = 0
        self.last_update = 0
        self.passed_time = 0

        self.canvas = Canvas(self, width=self.width, height=self.height, bd=0, highlightthickness=0, relief='ridge')
        self.score_label, self.score_per_label, self.time_label, self.average_time_label = None, None, None, None

        self.target = target.Target(self, self.canvas, 'red', 60)
        self.player = player.Player(self, self.canvas, 60, 60, 'blue', target=self.target,
                                    strategy=config.USED_STRATEGY_CLASS)
        self.target.spawn_new_target(self.player.pos)
        self.ground = self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, 10, fill='Black')
        self.canvas.move(self.ground, 0, WINDOW_HEIGHT * 0.5)

        self.score_y_pos = self.target.pos[1] - 20

        self.init_labels()
        self.canvas.pack()

        self.bind("<space>", lambda event: self.change(Playing) if self.state.name is Idle.name else self.change(Idle))

        # ToDo mro: Connect the session saving with the GUI here
        self.bind('e', lambda event: self.change(End))

        self.update()

    def update(self):
        """
        Calls the update methods of all objects and is responsible for the game loop and state handling
        :return: None
        """

        curr_state = self.state.name

        delta = self.handle_time()

        if curr_state is Idle.name:
            pass

        elif curr_state is Playing.name:
            # Clear
            self.clear()
            # Update
            self.player.update(delta_time=delta / 4)
            self.target.update(delta_time=delta)
            # Draw
            self.player.draw()

        elif curr_state is Hit.name:
            if self.curr_restart_time == 0:
                self.canvas.itemconfig(self.target.id, fill='green')

                # time that player needed to reach the target in s
                needed_time = self.target.time_last_hit / 1000.0

                # time that the player had available to reach the target in s
                max_time = config.TIME_TO_CATCH_PER_PIXEL * self.target.start_distance / 1000.0

                remaining_time_percentage = (1 - (needed_time / max_time)) * 100
                self.remaining_time_history.append(remaining_time_percentage)

                if config.SHOW_SCORE:
                    self.canvas.moveto(self.time_label, self.target.pos[0] + (self.target.size / 2),
                                       self.score_y_pos)
                    self.canvas.itemconfig(self.time_label,
                                           text=str(round(needed_time, 1)) + "s",
                                           state=NORMAL)
                    """"
                    self.canvas.itemconfig(self.time_label,
                                           text="Time left: " + str(round(remaining_time_percentage)) + "%",
                                           state=NORMAL)
                    """

            if self.curr_restart_time >= config.TARGET_RESPAWN_TIME:
                self.curr_restart_time = 0
                self.score += 1
                self.canvas.itemconfig(self.time_label, state=HIDDEN)
                self.change(Respawn)

            else:
                self.curr_restart_time += delta

        elif curr_state is Respawn.name:

            self.canvas.delete(self.target.id)

            self.player.speed_factor = 0
            del self.target
            self.target = target.Target(self, self.canvas, 'red', 60)
            self.player.target = self.target
            self.target.spawn_new_target(self.player.pos)

            self.change(Playing)

        elif curr_state is End.name:
            self.canvas.itemconfig(self.time_label, state=HIDDEN)
            self.canvas.itemconfig(self.player.id, state=HIDDEN)
            self.canvas.itemconfig(self.target.id, state=HIDDEN)
            self.canvas.itemconfig(self.ground, state=HIDDEN)

            average_time_in_percentage = 0
            if len(self.remaining_time_history) > 0:
                average_time_in_percentage = round(
                    sum(self.remaining_time_history) / len(self.remaining_time_history))

            total_attempts = self.score + self.miss

            accuracy_rate = 0
            if total_attempts > 0:
                accuracy_rate = round(self.score / total_attempts * 100)

            self.canvas.itemconfig(self.score_label,
                                   text="Caught targets: " + str(self.score) + "/" + str(total_attempts),
                                   state=NORMAL)
            self.canvas.itemconfig(self.score_per_label,
                                   text="Caught targets in Percentage: " + str(accuracy_rate) + "%",
                                   state=NORMAL)
            self.canvas.itemconfig(self.average_time_label,
                                   text="Average time left for a caught Target in percentage: " + str(
                                       average_time_in_percentage) + "%", state=NORMAL)

        # Repeat
        self.after(5, self.update)

    def handle_time(self):
        """
        Handles the time and returns a delta for correction
        :return: delta: delta for correction
        :rtype: int
        """

        # Time control
        self.update_counter = self.update_counter + 1
        now = round(time.time() * 1000)

        if self.last_update == 0:
            self.last_update = now

        delta = now - self.last_update
        self.passed_time = self.passed_time + delta

        if self.passed_time > 1000:
            # print("FPS: ", self.updateCounter)
            self.update_counter = 0
            self.passed_time = 0
        self.last_update = now
        return delta

    def clear(self):
        """
        Clears the canvas background. Very important function to avoid flickering and artifacts
        :return: None
        """

        self.canvas.configure(bg="white")

    def change(self, state):
        """
        Changes the internal state to state if possible
        :return: None
        """

        self.state.switch(state)

    def init_labels(self):
        """
        Init Labels
        :return: None
        """

        self.score_label = self.canvas.create_text(self.width / 2, self.height * 0.43,
                                                   anchor=CENTER, text="", font=('Helvetica', '20', 'bold'))
        self.canvas.itemconfig(self.score_label, state=HIDDEN)

        self.score_per_label = self.canvas.create_text(self.width / 2, self.height * 0.5,
                                                       anchor=CENTER, text="", font=('Helvetica', '20', 'bold'))
        self.canvas.itemconfig(self.score_per_label, state=HIDDEN)

        self.average_time_label = self.canvas.create_text(self.width / 2, self.height * 0.57,
                                                          anchor=CENTER, text="",
                                                          font=('Helvetica', '20', 'bold'))
        self.canvas.itemconfig(self.average_time_label, state=HIDDEN)

        self.time_label = self.canvas.create_text(self.width / 2, self.score_y_pos, anchor=CENTER, text="",
                                                  font=('Helvetica', '15', 'bold'))
        self.canvas.itemconfig(self.time_label, state=HIDDEN)
