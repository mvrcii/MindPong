import scripts.pong.strategy as strategy

# Game
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
TARGET_RESPAWN_TIME = 2000
MIN_DISTANCE_TARGET = 400
TIME_TO_STOP_PLAYER = 2000
TIME_TO_CATCH_PER_PIXEL = 10
SHOW_SCORE = True
USED_STRATEGY_CLASS = strategy.KeyStrategy
MIN_DURATION_OF_TRIAL = 1
OBJECT_SIZE = 14


# Calibration
CALIBRATION_TIME = 10  # in seconds

# Loader
NOTCH_FILTER_FREQ: float = 50
NOTCH_FILTER = True

# Read Data
SESSION_RECORDING = True

# Algorithm
WEIGHT = 2

# channel configuration of the headset we use
# BCI_CHANNELS = ['C3', 'Cz', 'C4', 'P3', 'Pz', 'P4', 'O1', 'O2', 'FC5', 'FC1', 'FC2', 'FC6', 'CP5', 'CP1', 'CP2',
#                 'CP6']

BCI_CHANNELS = ['C3', 'Cz', 'C4', 'P3', '?', 'P4', 'T3', '?', '?', 'F3', 'F4', '?', '?', '?', '?',
                'T4']  # large laplacian


# small laplacian
#                 'C3', 'Cz', 'C4', 'P3', 'Pz', 'P4', 'O1', 'O2', 'FC5', 'FC1', 'FC2', 'FC6', 'CP5', 'CP1', 'CP2', 'CP6'
#CH_NAMES_WEIGHT = [1,    0,    1,    0,    0,    0,    0,    0,     1,     1,     1,     1,     1,     1,     1,     1]

# large laplacian
#                 'C3', 'Cz', 'C4', 'P3', '?', 'P4', 'T3', '?', '?', 'F3', 'F4', '?', '?', '?', '?', 'T4'
CH_NAMES_WEIGHT = [1,    1,    1,    1,    0,    1,    1,   0,   0,   1,    1,    0,   0,   0,   0,    1]




