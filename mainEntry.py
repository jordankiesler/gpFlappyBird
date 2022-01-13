import random

import game as gm
from postprocessing import *
import plotting
import settings as st


def main():
    """
    Main entrance of program and calls
    post-processing activities
    :return: none
    """
    st.N_COLS = 1000
    st.RANDOM_SEED = 4701
    random.seed(st.RANDOM_SEED)
    game = gm.Game()
    while game.running and game.currentGeneration < st.N_GEN:
        game.reset()
        game.run()

    # All post-processing can be turned on/off in settings at the bottom

    # Provide the values needed to write the simulation to a training data file
    if st.PP_WRITE_TO_TEXT:
        writeRunToFile(game.currentGeneration, game.maxTotalScoreSoFar, game.maxDistanceScoreSoFar,
                       game.maxTargetScoreSoFar, game.maxTotalList, game.maxTotalSoFarList,
                       game.maxDistanceList, game.maxDistanceSoFarList, game.maxTargetList, game.maxTargetSoFarList,
                       game.bestPlaneScoresList, game.avgNumActiveNodes)

    # Provide the values needed to generate the plots of best in generation and overall for each score category
    if st.PP_PLOT_DATA:
        plotData(game.currentGeneration, game.maxTotalList, game.maxTotalSoFarList, game.maxDistanceList,
                 game.maxDistanceSoFarList, game.maxTargetList, game.maxTargetSoFarList)

    # Provide the values needed to plot the total score for all planes in all generations, the target score for all
    # planes in all generations, and the number of planes to reach the max distance each time
    # NOTE: Incredibly slow for large data sets (we're talking like, 4+ hours)
    if st.PP_PLOT_ALL:
        collateAllScores(st.allPlanes, st.all4ks, st.RANDOM_SEED)
        plotting.plotTargetScores(st.all4ks)
        plotting.plotNumReachMax(st.all4ks)


if __name__ == '__main__':
    main()