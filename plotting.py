import matplotlib.pyplot as plt
import numpy as np
import listOfLists as lol
import moreLists as ml
from mpl_toolkits import mplot3d
from matplotlib import cm


def plotComparisons(totalData, distanceData, targetData, labels, title):
    """
    Plot parameter sweeps of total scores, distance scores,
    and target scores for various scenarios (i.e. changing node #s)
    :param totalData: List of lists of total fitness values per generation per scenario
    :param distanceData: List of lists of distance fitness values per generation per scenario
    :param targetData: List of lists of target fitness values per generation per scenario
    :param labels: List of strings that match length of other data for data labeling
    :param title: Title of chart
    :return: none
    """
    plt.figure()
    fig, axs = plt.subplots(3)
    fig.suptitle(f'Comparison of Values for Changing {title}')

    for i in range(len(labels)):
        x = np.arange(0, len(totalData[i]), 1)
        axs[0].plot(x, totalData[i], label=labels[i])
        axs[1].plot(x, distanceData[i], label=labels[i])
        axs[2].plot(x, targetData[i], label=labels[i])
        print(totalData[i][-1])

    axs[0].set_ylabel("Max Total\nScore Overall")
    axs[1].set_ylabel("Max Distance\nScore Overall")
    axs[2].set_ylabel("Max Target\nScore Overall")
    axs[2].set_xlabel("Generation Number")

    plt.legend()
    plt.show()


def plot3D(data):
    """
    Plot a 3D plot of the composite scores
    of the best drone from every generation
    :param data: List of lists containing composite scores [total, distance fitness] for best plane per generation
    :return: none
    """
    w = np.arange(0, len(data), 1)      # Create an array of values representing the number of generations in the data
    x = [item[0] for item in data]      # Parse list of total score values per generation
    y = [item[1] for item in data]      # Parse list of distance score values per generation
    z = [item[2] for item in data]      # Parse list of target score values per generation

    # Create the figure
    fig = plt.figure()
    ax = plt.axes(projection="3d")

    # Add x, y gridlines
    ax.grid(visible=True, color='grey', linestyle='-.', linewidth=0.3, alpha=0.2)

    # Create color map
    my_cmap = plt.get_cmap('hsv')

    # Color map is the distance scores, three axes are total score, generation, and target score
    sctt = ax.scatter3D(x, w, z, alpha=0.8, c=y, cmap=my_cmap, marker='^', depthshade=True)

    plt.title("Composite Scores of Best Plane Per Generation")
    ax.set_xlabel('Total Score', fontweight='bold')
    ax.set_ylabel('Generation', fontweight='bold')
    ax.set_zlabel('Target Score', fontweight='bold')
    fig.colorbar(sctt, ax=ax, shrink=0.5, aspect=5)

    plt.show()


def plotDataBestPlane(data):
    """
    Plot the composite scores for the best plane
    in each generation on three separate plots
    :param data: List of lists containing composite scores [total, distance fitness] for best plane per generation
    :return: none
    """

    totals = [item[0] for item in data]         # Parse list of total score values per generation
    distance = [item[1] for item in data]       # Parse list of distance score values per generation
    targets = [item[2] for item in data]        # Parse list of target score values per generation

    generationNum = np.arange(0, len(data), 1)

    fig, axs = plt.subplots(3)
    fig.suptitle(f'Composite Scores for Best Plane, Each Generation')
    axs[0].scatter(generationNum, totals, s=5)
    axs[1].scatter(generationNum, distance, s=5)
    axs[2].scatter(generationNum, targets, s=5)
    axs[0].set_ylabel("Total Score")
    axs[1].set_ylabel("Distance Score")
    axs[2].set_ylabel("Target Score")

    plt.show()


def plotTargetRegression(data):
    """
    Plot the target scores for a given simulation along with a
    nonlinear regression through those scores achieved by drones
    who flew the full 4000 points (easily modified to do other regressions)
    :param data: List of lists of best plane scores (i.e., 3 values per generation)
    :return: none
    """
    plt.figure()
    x = []
    y = []
    # Plot points depending on whether they're from planes that flew the full 4000 frames or not
    for i in range(len(data)):
        if data[i][1] == 4000:
            plt.scatter(i, data[i][2], color='red', s=2)
            x.append(i)
            y.append(data[i][2])
        else:
            plt.scatter(i, data[i][2], color='black', s=2)

    plt.xlim(0)
    # These are just here to get the labels - otherwise it adds a label for every single black/red point
    plt.scatter(-50, 0, color='red', label="Drones Reaching Max Distance", s=2)
    plt.scatter(-50, 0, color='black', label="Drones Not Reaching Max Distance", s=2)
    # Create a polynomial fit line through the points of drones that flew the max distance
    plt.plot(x, np.poly1d(np.polyfit(x, y, 3))(x), c='blue', label="3° Polynomial Fit thru Max Distance Drones")

    plt.xlabel("Generations")
    plt.ylabel("Target Score")
    plt.title("Nonlinear Regression Fit of Target Scores\n"
              "for Drones with Maximum Distance Fitness")
    plt.legend()
    plt.show()


def plotNumReachMax(data):
    """
    Plot the number of drones in a given simulation
    to reach the maximum distance score
    :param data: List of lists containing the target scores of all those drones reaching max distance per generation
    (List is just already made for other data, so this is a convenient recycling of it)
    :return: none
    """

    plt.figure()
    for i in range(len(data)):
        if data[i]:
            plt.bar(i, len(data[i]), color='black', s=5)
        else:
            plt.scatter(i, 0, color='black', s=5)

    plt.title("Number of Drones Reaching Maximum Distance")
    plt.xlabel('Generation')
    plt.ylabel("Number of Drones to Reach Maximum Distance")
    plt.show()


def plotTargetScores(data):
    """
    Plots the target scores of all drones reaching the maximum distance
    :param data: List of lists containing the target scores of all those drones reaching max distance per generation
    :return: none
    """

    plt.figure()
    for i in range(len(data)):
        if data[i]:     # Some lists are empty, so check for that
            yVals = [item[1] for item in data[i]]
            xVals = np.ones(len(data[i])) * i
            plt.scatter(xVals, yVals, c='black', alpha=0.1)

    plt.xlabel("Generation")
    plt.ylabel("Target Score")
    plt.title("Target Score of Drones Reaching Maximum Distance")
    plt.show()


if __name__ == '__main__':
    # plotComparisons(lol.meanNodeTotals, lol.meanNodeDistance, lol.meanNodeTargets, lol.nodeLabels, "Number of Nodes")
    # plotComparisons(lol.changingNodeTotals2, lol.changingNodeDistance2, lol.changingNodeTargets2, lol.nodeLabels, "Number of Nodes")

    # plotComparisons(lol.meanMutationTotals, lol.meanMutationDistance, lol.meanMutationTargets, lol.mutationLabels, "Mutation Rates")
    # plotComparisons(lol.changingMutationTotals, lol.changingMutationDistance, lol.changingMutationTargets, lol.mutationLabels, "Mutation Rates")

    plotComparisons(lol.meanPopTotals, lol.meanPopDistance, lol.meanPopTargets, lol.popSizeLabels, "Population Size")
    # plotComparisons(lol.changingPopTotals, lol.changingPopDistance, lol.changingPopTargets, lol.popSizeLabels, "Population Size")

    # plot3D(lol.thousandGens60)
    # plot3D(lol.example3D2)

    # plotTargetRegression(lol.example3D2)

    # plotDataBestPlane(ml.fixOverfitted_119)

    # plotTargetScores(ml.fourk_101)
    # plotNumReachMax(ml.fourk_101)
    # plotNumReachMax(ml.fourk_107)
