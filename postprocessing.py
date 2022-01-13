import operator
import matplotlib.pyplot as plt
import numpy as np

import settings as st

runNum = 0      # Global variable used to denote runs and manage data across files


def writeRunToFile(generation, maxTotalScoreSoFar, maxDistanceScoreSoFar, maxTargetScoreSoFar,
                   maxTotalList, maxTotalSoFarList, maxDistanceList, maxDistanceSoFarList, maxTargetList,
                   maxTargetSoFarList, bestPlaneScoresList, activeNodes):
    """
    Write all the relevant information to a dataTraining file
    :param generation: Number of generations
    :param maxTotalScoreSoFar: Best total score for entire simulation
    :param maxDistanceScoreSoFar: Best distance score for entire simulation
    :param maxTargetScoreSoFar: Best target score for entire simulation
    :param maxTotalList: List of the best total score achieved for each generation
    :param maxTotalSoFarList: List of the best total score achieved to date per generation
    :param maxDistanceList: List of the best distance score achieved for each generation
    :param maxDistanceSoFarList: List of the best distance score achieved to date per generation
    :param maxTargetList: List of the best target score achieved for each generation
    :param maxTargetSoFarList: List of the best target score achieved to date per generation
    :param bestPlaneScoresList: List of the composite scores of the best drone for each generation
    :param activeNodes: List of the average number of active nodes per generation
    :return: none
    """

    content = open('./pp/numRuns.txt', 'r').readlines()

    # Collect what the current run number is and then increase it by one (dedicated file for this)
    global runNum
    runNum = int(content[0])
    content[0] = str(runNum + 1)
    out = open('./pp/numRuns.txt', 'w')
    out.writelines(content)
    out.close()

    sortedPlanes = sorted(bestPlaneScoresList, key=lambda score: score[0])
    averageActiveNodes = np.mean(activeNodes)

    text = f"--RUN {runNum}--\n" \
           f"Population Size: {sum(st.MU) + st.LAMBDA}\n" \
           f"Generations: {generation}\n" \
           f"Maximum Total Score: {maxTotalScoreSoFar} \n" \
           f"Maximum Distance Score: {maxDistanceScoreSoFar} \n" \
           f"Maximum Target Score: {maxTargetScoreSoFar} \n" \
           f"Best Overall Total Score: {sortedPlanes[-1][0]} \n" \
           f"Distance Score of Best Overall: {sortedPlanes[-1][1]} \n" \
           f"Target Score of Best Overall: {sortedPlanes[-1][2]} \n" \
           f"\nPARAMETERS:\n" \
           f"Random Seed: {st.RANDOM_SEED} \n" \
           f"Mu: {st.MU}   Mu Weights: {st.MU_WEIGHTS}    Lambda: {st.LAMBDA} \n" \
           f"Population Size: {sum(st.MU) + st.LAMBDA}\n" \
           f"Maximum Allowed Distance: {st.PLANE_MAX_DISTANCE_ALLOWED} \n" \
           f"Plane Y Speed: {st.PLANE_Y_SPEED}     Plane X Speed: {st.PLANE_X_SPEED}\n" \
           f"Multi-Objective Weight Function: distanceScore + ({st.WEIGHT_TARGETS} * targetScore)\n" \
           f"Range of Horizontal Space between Adjacent Radar Pairs: {st.MIN_RADAR_SPACE} - {st.MAX_RADAR_SPACE}\n" \
           f"Range of Gap (Vertical Space) between Pair of Radars:  {st.MIN_RADAR_GAP} - {st.MAX_RADAR_GAP}\n" \
           f"Minimum Length of Radar Beam: {st.MIN_RADAR_LENGTH}\n" \
           f"Mutation Probability: {st.MUT_PB*100}%\n" \
           f"Number of Columns (Nodes): {st.N_COLS}\n" \
           f"Overall Average Number of Active Nodes: {averageActiveNodes} ({round(100*averageActiveNodes/st.N_COLS, 2)}%)\n" \
           f"\nLISTS:\n" \
           f"List of Best in Generation for Total Score: {maxTotalList}, \n" \
           f"List of Best in All Previous Generations for Total Score: {maxTotalSoFarList}, \n" \
           f"List of Best in Generation for Distance Score: {maxDistanceList}, \n" \
           f"List of Best in All Previous Generations for Distance Score: {maxDistanceSoFarList}, \n" \
           f"List of Best in Generation for Target Score: {maxTargetList}, \n" \
           f"List of Best in All Previous Generations for Target Score: {maxTargetSoFarList}, \n" \
           f"List of Scores for the Best Overall Plane in Each Generation: {bestPlaneScoresList},\n"

    with open("./pp/trainingData.txt", "a+") as file:
        # Move read cursor to the start of file.
        file.seek(0)
        # If file is not empty then append '\n'
        data = file.read(100)
        if len(data) > 0:
            file.write("\n\n")
        # Append text at the end of file
        file.write(text)


def plotData(generation, maxTotalList, maxTotalSoFarList, maxDistanceList, maxDistanceSoFarList,
             maxTargetList, maxTargetSoFarList):
    """
    Plot the best overall and best in generation for each type of score
    :param generation: Number of generations
    :param maxTotalList: List of the best total score achieved for each generation
    :param maxTotalSoFarList: List of the best total score achieved to date per generation
    :param maxDistanceList: List of the best distance score achieved for each generation
    :param maxDistanceSoFarList: List of the best distance score achieved to date per generation
    :param maxTargetList: List of the best target score achieved for each generation
    :param maxTargetSoFarList: List of the best target score achieved to date per generation
    :return: none
    """

    global runNum

    generationNum = np.arange(0, generation, 1)

    fig, axs = plt.subplots(2)
    fig.suptitle(f'Total Score for Run Number {runNum}')
    axs[0].scatter(generationNum, maxTotalList, s=5)
    axs[1].plot(generationNum, maxTotalSoFarList)
    axs[0].set_ylabel("Generational Winner")
    axs[1].set_ylabel("Max Pop Fitness")
    axs[1].set_xlabel("Generation Number")

    fig, axs = plt.subplots(2)
    fig.suptitle(f'Distance Score for Run Number {runNum}')
    axs[0].scatter(generationNum, maxDistanceList, s=5)
    axs[1].plot(generationNum, maxDistanceSoFarList)
    axs[0].set_ylabel("Generational Winner")
    axs[1].set_ylabel("Max Pop Fitness")
    axs[1].set_xlabel("Generation Number")

    fig, axs = plt.subplots(2)
    fig.suptitle(f'Target Score for Run Number {runNum}')
    axs[0].scatter(generationNum, maxTargetList, s=5)
    axs[1].plot(generationNum, maxTargetSoFarList)
    axs[0].set_ylabel("Generational Winner")
    axs[1].set_ylabel("Max Pop Fitness")
    axs[1].set_xlabel("Generation Number")

    plt.show()


def collateAllScores(data, fourK, title):
    """
    Plot the scores of all planes for all generations
    and then write those scores to file
    :param data: List of all planes scores for all generations
    :param fourK: List of all planes scores that made it the max distance
    :param title: Title of the plot
    :return: none
    """

    plt.figure()
    for i in range(len(data)):
        for j in range(len(data[i])):
            x = len(data[i])
            x *= i
            plt.scatter(x, data[i][j], c='black', alpha=0.5)

    plt.title(f"Final {title} Score of All Planes")
    plt.xlabel("Generation Number")
    plt.ylabel("Total Score")
    plt.ylim(bottom=-100)

    global runNum
    text = f"Run {runNum}\n" \
           f"Parameter: {title}\n" \
           f"{data}"

    # Write the scores of all drones for all generations to the file
    with open("./pp/allScores.txt", "a+") as file:
        file.seek(0)
        # If file is not empty then append '\n'
        data = file.read(100)
        if len(data) > 0:
            file.write("\n\n")
        # Append text at the end of file
        file.write(text)

    text2 = f"Run {runNum}\n" \
            f"Pop Size: {sum(st.MU)+st.LAMBDA}\n" \
            f"{fourK}"

    # Write the scores of all the drones making it to 4000 points to the file
    with open("./pp/4kAverages.txt", "a+") as file:

        # Move read cursor to the start of file.
        file.seek(0)
        # If file is not empty then append '\n'
        data = file.read(100)
        if len(data) > 0:
            file.write("\n\n")
        # Append text at the end of file
        file.write(text2)

    plt.show()
