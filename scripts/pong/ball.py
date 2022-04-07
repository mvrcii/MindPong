import random
import math

from enum import *


class CollisionType(Enum):
    """Enumerate various collision types for the ball."""

    LEFT = auto()
    RIGHT = auto()
    BOTTOM = auto()
    TOP = auto()
    PADDLE = auto()
    NONE = auto()


class Ball:
    def __init__(self, root, canvas, color, size, paddle):
        from scripts.pong.main import MindPong
        self.root: MindPong = root

        self.canvas = canvas
        self.canvas_width = canvas.winfo_reqwidth()
        self.canvas_height = canvas.winfo_reqheight()
        self.color = color
        self.size = size
        self.speed_factor = 1
        self.pos = None
        self.v_x, self.v_y = 0, 0
        self.vec_x, self.vec_y = 0, 0
        self.angle = 0
        self.paddle = paddle
        self.id = None
        self.hit_bottom = False

        self.init()

    def update(self, delta_time):
        # Update velocity according to the time
        self.v_x = self.speed_factor * math.cos(math.radians(self.angle)) * delta_time
        self.v_y = self.speed_factor * math.sin(math.radians(self.angle)) * delta_time

        # Check if ball will collide in next tick
        collision_type = self.check_collision()

        if collision_type == CollisionType.BOTTOM:
            from scripts.pong.main import Restart
            self.root.change(Restart)
            self.hit_bottom = True
            self.reset()
            self.paddle.reset()

        self.update_angle(collision_type)

    def draw(self):
        self.canvas.move(self.id, self.v_x, self.v_y)
        self.pos = self.canvas.coords(self.id)

    def reset(self):
        self.canvas.delete(self.id)
        self.speed_factor = 1
        self.init()

    def init(self):
        """Initializes the ball object and its position."""
        self.id = self.canvas.create_oval(0, 0, self.size, self.size, fill=self.color)
        # Move to initial position
        self.canvas.move(self.id, (self.canvas_width - self.size) / 2, self.canvas_height/2)
        # Update position
        self.pos = self.canvas.coords(self.id)
        self.init_angle()

    def init_angle(self):
        """Initializes the balls angle."""
        self.vec_x = random.choice([round(random.uniform(-1, -0.1), 2), round(random.uniform(0.1, 1), 2)])
        self.vec_y = -1
        self.angle = get_angle_for_vector(vec_x=self.vec_x, vec_y=self.vec_y)

    def check_collision(self) -> CollisionType:
        """Checks if the ball will collide with any CollisionType in the next tick."""
        # TODO: Task MIN-32: Verbesserte Lösung für das Border Problem.
        #                    Derzeit Collision Check im nächsten Tick mit verdoppelter Geschwindigkeit.
        v_x = self.v_x * 2
        v_y = self.v_y * 2
        pos = self.pos
        if (pos[0] + v_x) <= 0:
            return CollisionType.LEFT
        elif (pos[1] + v_y) <= 0:
            return CollisionType.TOP
        elif (pos[2] + v_x) >= self.canvas_width:
            return CollisionType.RIGHT
        elif (pos[3] + v_y) >= self.canvas_height:
            return CollisionType.BOTTOM
        elif self.check_collision_with_paddle(pos, v_x, v_y):
            self.root.score += 1
            return CollisionType.PADDLE
        else:
            return CollisionType.NONE

    def update_angle(self, collision_type: CollisionType):
        """Updates the angle depending on the given CollisionType."""
        if collision_type == CollisionType.TOP or collision_type == CollisionType.PADDLE:
            self.angle = 360 - self.angle
        elif collision_type == CollisionType.LEFT or collision_type == CollisionType.RIGHT:
            if self.angle > 180:
                self.angle = 360 - (self.angle - 180)
            else:
                self.angle = 180 - self.angle
        elif collision_type == CollisionType.BOTTOM:
            self.hit_bottom = True

    def check_collision_with_paddle(self, pos, v_x, v_y):
        """Checks if the ball collides with the paddle."""
        paddle_pos = self.canvas.coords(self.paddle.id)
        if (pos[2] + v_x) >= paddle_pos[0] and (pos[0] + v_x) <= paddle_pos[2]:
            if paddle_pos[1] <= (pos[3] + v_y) <= paddle_pos[3]:
                return True
        return False


def get_angle_for_vector(vec_x, vec_y):
    angle = math.degrees(math.atan2(vec_y, vec_x))
    if angle < 0:
        angle += 360
    return angle
