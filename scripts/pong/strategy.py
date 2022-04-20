from abc import ABCMeta, abstractmethod
import scripts.pong.player as player
from scripts.utils.event_listener import subscribe


class IStrategy(metaclass=ABCMeta):
    """
    Abstract Control Strategy Class for the player
    """

    @staticmethod
    @abstractmethod
    def __str__(player: player.Player):
        """
        Abstract method
        :param player: player object
        :return: None
        """


class KeyStrategy(IStrategy):
    """
    Control strategy to control the player with Keys
    """

    @staticmethod
    def __str__(player: player.Player):
        """
        Binds the keys with the move methods of the player
        :param player: player object
        :return: None
        """
        player.canvas.bind_all('<KeyPress-Left>', player.move_left)
        player.canvas.bind_all('<KeyPress-Right>', player.move_right)


class AlgorithmsStrategy(IStrategy):
    """
    Control Strategy to control the player with Algorithm
    """

    @staticmethod
    def __str__(player: player.Player):
        """
        Binds events posted by the algorithm with the move methods of the player
        :param player: player object
        :return: None
        """
        subscribe("move_left_direction", player.move_left)
        subscribe("move_right_direction", player.move_right)
