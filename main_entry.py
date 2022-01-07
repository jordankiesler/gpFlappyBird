"""
Entrance of the program.
"""
from game import *
from postprocessing import *
import random


def main():
    random.seed(RANDOM_SEED)
    game = Game()
    while game.running and game.currentGeneration < N_GEN:
        game.reset()
        game.run()

    plotData(game.currentGeneration, game.maxTotalList, game.maxTotalSoFarList, game.maxDistanceList,
             game.maxDistanceSoFarList, game.maxTargetList, game.maxTargetSoFarList)

    if PP_WRITE_TO_TEXT:
        writeRunToFile(game.currentGeneration, game.maxTotalScoreSoFar, game.maxDistanceScoreSoFar,
                       game.maxTargetScoreSoFar, game.maxTotalScore, game.maxDistanceScore, game.maxTargetScore,
                       game.maxTotalList, game.maxTotalSoFarList, game.maxDistanceList, game.maxDistanceSoFarList,
                       game.maxTargetList, game.maxTargetSoFarList)

    if PP_FORMULA or PP_GRAPH_VISUALIZATION:
        gs = [extract_computational_subgraph(ind) for ind in game.pop]
        # note that only the MU parents have been evaluated and have totalFitness values
        if PP_FORMULA:
            print("Writing formula to ./pp/formula.txt ...")
            with open("./pp/formula.txt", 'w') as f:
                for i, g in enumerate(gs):
                    formula = simplify(g, ['v', 'h', 'g', 'vr', 'hr'])
                    formula = round_expr(formula, PP_FORMULA_NUM_DIGITS)
                    print(
                        f"{i}\n score: {game.pop[i].totalFitness}\n formula: {formula}")
                    f.write(
                        f"{i}\n score: {game.pop[i].totalFitness}\n formula: {formula}\n")


if __name__ == '__main__':
    main()
