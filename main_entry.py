"""
Entrance of the program.
"""
import game as gm
from postprocessing import *
import random
import settings as st


def main():

    for numNodes in range(25, 1026, 50):
        for _ in range(3):
            st.N_COLS = numNodes
            random.seed(st.RANDOM_SEED)
            game = gm.Game()
            while game.running and game.currentGeneration < st.N_GEN:
                game.reset()
                game.run()

            if st.PP_PLOT_DATA:
                plotData(game.currentGeneration, game.maxTotalList, game.maxTotalSoFarList, game.maxDistanceList,
                         game.maxDistanceSoFarList, game.maxTargetList, game.maxTargetSoFarList)

            if st.PP_WRITE_TO_TEXT:
                writeRunToFile(game.currentGeneration, game.maxTotalScoreSoFar, game.maxDistanceScoreSoFar,
                               game.maxTargetScoreSoFar, game.maxTotalList, game.maxTotalSoFarList,
                               game.maxDistanceList, game.maxDistanceSoFarList, game.maxTargetList, game.maxTargetSoFarList,
                               game.bestPlaneScoresList, game.numTargets)

    st.N_COLS = 250
    for mutationProbability in range(1, 10002, 500):    # 20 runs
        for _ in range(3):
            st.MUT_PB = (mutationProbability / 1000)    # Gives range of 0.001% to 10%
            random.seed(st.RANDOM_SEED)
            game = gm.Game()
            while game.running and game.currentGeneration < st.N_GEN:
                game.reset()
                game.run()

            if st.PP_PLOT_DATA:
                plotData(game.currentGeneration, game.maxTotalList, game.maxTotalSoFarList, game.maxDistanceList,
                         game.maxDistanceSoFarList, game.maxTargetList, game.maxTargetSoFarList)

            if st.PP_WRITE_TO_TEXT:
                writeRunToFile(game.currentGeneration, game.maxTotalScoreSoFar, game.maxDistanceScoreSoFar,
                               game.maxTargetScoreSoFar, game.maxTotalList, game.maxTotalSoFarList,
                               game.maxDistanceList, game.maxDistanceSoFarList, game.maxTargetList,
                               game.maxTargetSoFarList,
                               game.bestPlaneScoresList, game.numTargets)

    st.MUT_PB = 0.015
    st.MU_WEIGHTS = None
    for popSize in range(103, 2, 10):       # 10 runs
        for _ in range(3):
            if popSize > 80:
                st.MU = [8, 4, 4]
            elif popSize > 50:
                st.MU = [6, 3, 3]
            elif popSize > 30:
                st.MU = [4, 2, 2]
            elif popSize > 10:
                st.MU = [2, 1, 1]
            elif popSize > 0:
                st.MU = [1]
            st.LAMBDA = popSize - sum(st.MU)

            random.seed(st.RANDOM_SEED)
            game = gm.Game()
            while game.running and game.currentGeneration < st.N_GEN:
                game.reset()
                game.run()

            if st.PP_PLOT_DATA:
                plotData(game.currentGeneration, game.maxTotalList, game.maxTotalSoFarList, game.maxDistanceList,
                         game.maxDistanceSoFarList, game.maxTargetList, game.maxTargetSoFarList)

            if st.PP_WRITE_TO_TEXT:
                writeRunToFile(game.currentGeneration, game.maxTotalScoreSoFar, game.maxDistanceScoreSoFar,
                               game.maxTargetScoreSoFar, game.maxTotalList, game.maxTotalSoFarList,
                               game.maxDistanceList, game.maxDistanceSoFarList, game.maxTargetList,
                               game.maxTargetSoFarList,
                               game.bestPlaneScoresList, game.numTargets)


if __name__ == '__main__':
    main()

# if PP_FORMULA or PP_GRAPH_VISUALIZATION:
#     gs = [extract_computational_subgraph(ind) for ind in game.pop]
#     # note that only the MU parents have been evaluated and have totalFitness values
#     if PP_FORMULA:
#         print("Writing formula to ./pp/formula.txt ...")
#         with open("./pp/formula.txt", 'w') as f:
#             for i, g in enumerate(gs):
#                 formula = simplify(g, ['v', 'h', 'g', 'vr', 'hr'])
#                 formula = round_expr(formula, PP_FORMULA_NUM_DIGITS)
#                 print(
#                     f"{i}\n score: {game.pop[i].totalFitness}\n formula: {formula}")
#                 f.write(
#                     f"{i}\n score: {game.pop[i].totalFitness}\n formula: {formula}\n")