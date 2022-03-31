from tkinter import *
import time

import scripts.pong.ball as ball
import scripts.pong.paddle as paddle


RESTART_TIME = 3


class GameState(object):
    name = "state"
    allowed = []

    def switch(self, state):
        """ Switch to new state
        Use this method and do not set the state attribute manually! """
        if state.name in self.allowed:
            print('Current State:', self, ' => switched to new state', state.name)
            self.__class__ = state
        else:
            print('Current State:', self, ' => switching to', state.name, 'not possible.')

    def __str__(self):
        return self.name


class Playing(GameState):
    """ State of actively playing the game """
    name = "playing"
    allowed = ['idle', 'restart']


class Idle(GameState):
    """ State of being in idle mode to pause the game """
    name = "idle"
    allowed = ['playing']


class Restart(GameState):
    """ State of restarting the game after a loose """
    name = "restart"
    allowed = ['playing']


class MindPong(Tk):
    """ A class representing the game """

    def __init__(self):
        Tk.__init__(self)

        self.WIDTH = 800
        self.HEIGHT = 600

        # State of the game - default is idle
        self.state = Idle()
        self.score = 0

        self.curr_restart_time = 0

        self.updateCounter = 0
        self.lastUpdate = 0
        self.passedTime = 0

        self.title("MindPong Game")
        self.canvas = Canvas(self, width=self.WIDTH, height=self.HEIGHT, bd=0, highlightthickness=0, relief='ridge')
        self.score_label, self.timer_label = None, None
        self.init_labels()
        self.canvas.pack()

        self.paddle = paddle.Paddle(self, self.canvas, 100, 10, 'blue')
        self.ball = ball.Ball(self, self.canvas, 'red', 15, paddle=self.paddle)

        self.change(Playing)
        self.bindings()
        self.update()  # trigger initial update
        self.mainloop()

    def update(self):
        delta = self.handle_time()

        curr_state = self.state.name
        if curr_state is Idle.name:
            pass

        elif curr_state is Playing.name:
            # Clear
            self.clear()
            # Update
            self.paddle.update(delta_time=delta / 4)
            self.ball.update(delta_time=delta / 4)
            # Draw
            self.paddle.draw()
            self.ball.draw()

        elif curr_state is Restart.name:
            if self.curr_restart_time == 0:
                self.curr_restart_time = time.time()
                self.canvas.itemconfig(self.score_label, text="Score: " + str(self.score), state=NORMAL)
                self.canvas.itemconfig(self.timer_label, state=NORMAL)
                self.canvas.itemconfig(self.paddle.id, state=HIDDEN)
                self.canvas.itemconfig(self.ball.id, state=HIDDEN)
                self.score = 0

            curr_time = time.time()
            if curr_time - self.curr_restart_time > RESTART_TIME:
                self.curr_restart_time = 0
                self.change(Playing)
                self.canvas.itemconfig(self.score_label, state=HIDDEN)
                self.canvas.itemconfig(self.timer_label, state=HIDDEN)
                self.canvas.itemconfig(self.paddle.id, state=NORMAL)
                self.canvas.itemconfig(self.ball.id, state=NORMAL)
            else:
                seconds_until_restart = round(3 - (curr_time - self.curr_restart_time), 1)
                self.canvas.itemconfig(self.timer_label, text="Restarting in " + str(seconds_until_restart),
                                       state=NORMAL)

        # Repeat
        self.after(5, self.update)

    def handle_time(self):
        # Time control
        self.updateCounter = self.updateCounter + 1
        now = round(time.time() * 1000)

        if self.lastUpdate == 0:
            self.lastUpdate = now

        delta = now - self.lastUpdate

        self.passedTime = self.passedTime + delta

        if self.passedTime > 1000:
            print("FPS: ", self.updateCounter)
            self.updateCounter = 0
            self.passedTime = 0
        self.lastUpdate = now
        return delta

    def clear(self):
        self.canvas.configure(bg="white")

    def change(self, state):
        """ Change the game state """
        self.state.switch(state)

    def bindings(self):
        self.canvas.bind_all("<space>",
                             lambda event: self.change(Playing) if self.state.name is Idle.name else self.change(Idle))

    def init_labels(self):
        self.score_label = self.canvas.create_text(self.WIDTH / 2, self.HEIGHT * 0.5,
                                                   anchor=CENTER, text="Score: 0", font=('Helvetica', '20', 'bold'))
        self.canvas.itemconfig(self.score_label, state=HIDDEN)

        self.timer_label = self.canvas.create_text(self.WIDTH / 2, self.HEIGHT * 0.6,
                                                   anchor=CENTER, text="Restarting in 3",
                                                   font=('Helvetica', '20', 'bold'))
        self.canvas.itemconfig(self.timer_label, state=HIDDEN)


def main():
    MindPong()


if __name__ == "__main__":
    main()
