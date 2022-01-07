"""
Define some constant parameters and program settings.
"""
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 500
TITLE = 'Basic AI Drone via Evolutionary Cartesian Genetic Programming'
FPS = 600
IMG_DIR = './img'
FONT_NAME = 'Arial'
FONT_SIZE = 20
WHITE = (255, 255, 255)

JUMP_SPEED = -3.5       # once the plane turns, its speed becomes this value
GRAVITY_ACC = 0         #0.35
PLANE_X_SPEED = 3       # the const horizontal speed of the plane
PLANE_MAX_Y_SPEED = 5   # the maximum downward speed

# horizontal space between two adjacent pairs of radars
MIN_RADAR_SPACE = 175
MAX_RADAR_SPACE = 320
# gap (vertical space) between a pair of radars
MIN_RADAR_GAP = 100
MAX_RADAR_GAP = 150
# minimum length of a radar beam
MIN_RADAR_LENGTH = 100

# parameters of cartesian genetic programming
MUT_PB = 0.015  # mutate probability
N_COLS = 100  # number of cols (nodes) in a single-row CGP
LEVEL_BACK = 80  # how many levels back are allowed for inputs in CGP

# parameters of evolutionary strategy: MU+LAMBDA
# List for Mu is # of parents kept for total fitness, distance fitness, and target fitness, respectively
MU = [3, 2, 2]
MU_WEIGHTS = [15, 30, 44, 58, 72, 86, 100]
LAMBDA = 23
N_GEN = 50  # max number of generations

# if True, then additional information will be printed
VERBOSE = True

# Postprocessing
# if True, then the evolved math formula will be simplified and the corresponding
# computational graph will be visualized into files under the `pp` directory
PP_FORMULA = False
PP_FORMULA_NUM_DIGITS = 5
PP_FORMULA_SIMPLIFICATION = True
PP_GRAPH_VISUALIZATION = False
PP_WRITE_TO_TEXT = True

# for reproduction by setting an integer value; otherwise, set `None`
RANDOM_SEED = random.randint(1, 100000)      # None  # 26  # 265  # 14256
