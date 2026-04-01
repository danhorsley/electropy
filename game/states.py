from enum import Enum


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"
