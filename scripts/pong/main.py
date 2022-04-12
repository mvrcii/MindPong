from tkinter import *
import tkinter as tk
import time

import scripts.pong.player as player
import scripts.pong.target as target
from scripts.config import *


class GameState(object):
    """
    A class used to handle the state management in the Game

    Attribute:
    ----------
    name : str
        the name of the state
    allowed : [str]
        a list of the allowed state names to switch to

    Methods
    -------
    switch(state)
        Switches the current state to the passed state if it is listed in the allowed states
    """

    name = "state"
    allowed = []

    def switch(self, state):
        """Switches to the given state.

        If the argument `state` is not listed in the allowed attribute, the state will not switch.
        Use this method and do not set the state attribute manually!

        Parameters
        ----------
            state : GameState
                the state to switch to

        Returns
        -------
        None
        """

        if state.name in self.allowed:
            print('Current State:', self, ' => switched to new state', state.name)
            self.__class__ = state
            print(self.__class__)
        else:
            print('Current State:', self, ' => switching to', state.name, 'not possible.')

    def __str__(self):
        return self.name


class Playing(GameState):
    """A child of GameState defining the state playing"""
    name = "playing"
    allowed = ['idle', 'restart']


class Idle(GameState):
    """A child of GameState defining the state idle"""
    name = "idle"
    allowed = ['playing']


class Restart(GameState):
    """A child of GameState defining the state idle"""
    name = "restart"
    allowed = ['playing']


class MindPong(tk.Frame):
    """
    A class representing the pong game

    Attributes:
    ----------
        width : int
            the width of the pong window
        height : int
            the height of the pong window
        state : GameState
            the current game state
        score : int
            the current game score
        curr_restart_timer : float
            the current restart timer, which will be set to a value and then count down until it reaches zero.
            This variable is also displayed while the game is being restarted.
        update_counter : int
            the tick counter
        last_update : float
            the timestamp of the last update
        passed_time : float
            the time that has passed since last_update
        canvas : Canvas
            the canvas to draw on
        paddle : Paddle
            the paddle object
        ball : Ball
            the ball object

    Methods
    -------
    update()
        Calls the update methods of all objects and is responsible for the game loop and state handling
    handle_time()
        Handles the time and returns a delta for correction
    clear()
        Clears the canvas background. Very important function to avoid flickering and artifacts
    change(state)
        Changes the internal state to state if possible
    set_speed_factors(evt)
        Takes one of the key events from 1-9 and adapts the balls and paddles speed according to the pressed key.
        Whereas key 1 corresponds to the slowest and also standard game speed and key 9 to the highest game speed.

    -------
    A child of tk.Frame
    """

    def __init__(self, parent, controller):
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

        self.curr_restart_time = 0

        self.update_counter = 0
        self.last_update = 0
        self.passed_time = 0

        self.canvas = Canvas(self, width=self.width, height=self.height, bd=0, highlightthickness=0, relief='ridge')
        self.score_label, self.timer_label = None, None
        self.init_labels()
        self.canvas.pack()

        self.target = target.Target(self, self.canvas, 'red', 60)
        self.player = player.Player(self, self.canvas, 60, 60, 'blue', target=target)

        self.bind("<space>", lambda event: self.change(Playing) if self.state.name is Idle.name else self.change(Idle))

        self.update()

    def update(self):
        curr_state = self.state.name

        delta = self.handle_time()

        if curr_state is Idle.name:
            pass

        elif curr_state is Playing.name:
            # Clear
            self.clear()
            # Update
            self.player.update(delta_time=delta / 4)
            # Draw
            self.player.draw()

        elif curr_state is Restart.name:
            if self.curr_restart_time == 0:
                self.curr_restart_time = time.time()
                self.canvas.itemconfig(self.score_label, text="Score: " + str(self.score), state=NORMAL)
                self.canvas.itemconfig(self.timer_label, state=NORMAL)
                self.canvas.itemconfig(self.player.id, state=HIDDEN)
                self.score = 0

            curr_time = time.time()
            if curr_time - self.curr_restart_time > PONG_RESTART_TIME:
                self.curr_restart_time = 0
                self.change(Playing)
                self.canvas.itemconfig(self.score_label, state=HIDDEN)
                self.canvas.itemconfig(self.timer_label, state=HIDDEN)
                self.canvas.itemconfig(self.player.id, state=NORMAL)
            else:
                seconds_until_restart = round(3 - (curr_time - self.curr_restart_time), 1)
                self.canvas.itemconfig(self.timer_label, text="Restarting in " + str(seconds_until_restart),
                                       state=NORMAL)

        # Repeat
        self.after(5, self.update)

    def handle_time(self):
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
        self.canvas.configure(bg="white")

    def change(self, state):
        self.state.switch(state)

    def init_labels(self):
        self.score_label = self.canvas.create_text(self.width / 2, self.height * 0.5,
                                                   anchor=CENTER, text="Score: 0", font=('Helvetica', '20', 'bold'))
        self.canvas.itemconfig(self.score_label, state=HIDDEN)

        self.timer_label = self.canvas.create_text(self.width / 2, self.height * 0.6,
                                                   anchor=CENTER, text="Restarting in 3",
                                                   font=('Helvetica', '20', 'bold'))
        self.canvas.itemconfig(self.timer_label, state=HIDDEN)
