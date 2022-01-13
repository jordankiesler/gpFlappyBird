"""
Define some constant parameters and program settings.
"""
import random

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
TITLE = 'Basic AI Drone via Evolutionary Cartesian Genetic Programming'
FPS = 600
IMG_DIR = './img'
FONT_NAME = 'Arial'
FONT_SIZE = 20
WHITE = (255, 255, 255)

PLANE_Y_SPEED = -3.5        # once the plane turns, its side to side speed becomes this value
PLANE_X_SPEED = 3           # the const forward speed of the plane

PLANE_MAX_DISTANCE_ALLOWED = 4000   # max distance plane allowed to fly before resetting
WEIGHT_TARGETS = 10                 # how heavily target points are weighted against distance pts


MIN_RADAR_SPACE = 175       # vertical space between two adjacent pairs of radars
MAX_RADAR_SPACE = 340
MIN_RADAR_GAP = 120         # gap (horizontal space) between a pair of radars
MAX_RADAR_GAP = 180
MIN_RADAR_LENGTH = 80       # minimum length of a radar beam

MUT_PB = 0.010              # mutate probability (weighted in the game depending on score)
N_COLS = 250                # number of cols (nodes) in a single-row CGP
LEVEL_BACK = N_COLS         # how many levels back are allowed for inputs in CGP

RANDOM_SEED = random.randint(1, 100000)     # Allows reproducibility

MU = [3, 2, 2]             # List for Mu is number of parents kept for total, distance, and target fitness, respectively
MU_WEIGHTS = [15, 30, 44, 58, 72, 86, 100]   # List of weights for probability of choosing each parent - begins evenly
LAMBDA = 30-sum(MU)                          # Number of children
N_GEN = 100                                  # max number of generations

VERBOSE = False              # if True, then additional information will be printed

# Postprocessing
PP_WRITE_TO_TEXT = True
PP_PLOT_DATA = False
PP_PLOT_ALL = False

allPlanes = []
all4ks = []
