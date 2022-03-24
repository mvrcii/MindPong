from tkinter import *
from Pong.ball import *
from Pong.paddle import *
import time

fps = 60


class MindPong(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.WIDTH = 800
        self.HEIGHT = 600

        self.updateCounter = 0
        self.lastUpdate = 0
        self.passedTime = 0

        self.title("MindPong Game")
        self.canvas = Canvas(self, width=self.WIDTH, height=self.HEIGHT, bd=0)
        self.canvas.pack()

        self.paddle = Paddle(self.canvas, 100, 10, 'blue')
        self.ball = Ball(self.canvas, 'red', 25, paddle=self.paddle)

        self.update()  # trigger initial update
        self.mainloop()

    def update(self):
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

        # Clear
        self.clear()

        # Update
        self.paddle.update(delta_time=delta / 4)
        self.ball.update(delta_time=delta / 4)

        # Draw
        self.paddle.draw()
        self.ball.draw()

        # Repeat
        self.after(5, self.update)

    def clear(self):
        self.canvas.configure(bg="white")


def main():
    MindPong()


if __name__ == "__main__":
    main()
