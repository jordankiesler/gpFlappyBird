import random

import matplotlib.pyplot as plt
import numpy as np
import listOfLists as lol
import moreLists as ml
import postprocessing
from mpl_toolkits import mplot3d
from matplotlib import cm


# Plot comparisons of total scores, distance scores, and target scores for various scenarios (i.e. changing node #s)
def plotComparisons(totalData, distanceData, targetData, labels, title):
    plt.figure()
    fig, axs = plt.subplots(3)
    fig.suptitle(f'Comparison of Values for Changing {title}')

    for i in range(len(labels)):
        x = np.arange(0, len(totalData[i]), 1)
        axs[0].plot(x, totalData[i], label=labels[i])
        axs[1].plot(x, distanceData[i], label=labels[i])
        axs[2].plot(x, targetData[i], label=labels[i])

    axs[0].set_ylabel("Max Total\nScore Overall")
    axs[1].set_ylabel("Max Distance\nScore Overall")
    axs[2].set_ylabel("Max Target\nScore Overall")
    axs[2].set_xlabel("Generation Number")

    print(f"Pop 100: {totalData[5][-1]}, Total 100: {totalData[3][-1]}")
    # plt.legend()
    plt.show()

# Plot a 3D plot of the composite scores o the best drone from every generation
def plot3D(data):
    x = [item[0] for item in data]
    w = np.arange(0, len(data), 1)
    y = [item[1] for item in data]
    z = [item[2] for item in data]

    # Creating figure
    fig = plt.figure()
    ax = plt.axes(projection="3d")

    # Add x, y gridlines
    ax.grid(visible=True, color='grey', linestyle='-.', linewidth=0.3, alpha=0.2)

    # Creating color map
    my_cmap = plt.get_cmap('hsv')

    # Color map is the distance scores
    sctt = ax.scatter3D(x, w, z, alpha=0.8, c=y, cmap=my_cmap, marker='^')


    plt.title("simple 3D scatter plot")
    ax.set_xlabel('Total Score', fontweight='bold')
    ax.set_ylabel('Generation', fontweight='bold')
    ax.set_zlabel('Target Score', fontweight='bold')
    fig.colorbar(sctt, ax=ax, shrink=0.5, aspect=5)

    # show plot
    plt.show()


# Plot one value over time
def plotOneValue(data):
    plt.figure()
    x = np.arange(0, len(data), 1)
    plt.scatter(x, data)
    plt.xlabel("Generations")
    plt.show()


# Plot the composite scores for the best plane in each generation on three separate plots
def plotDataBestPlane(data):

    totals = [item[0] for item in data]
    distance = [item[1] for item in data]
    targets = [item[2] for item in data]

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

def plotNumReachMax(data):
    generations = len(data)

    plt.figure()
    for i in range(len(data)):
        if data[i]:
            plt.scatter(i, len(data[i]), color='black', s=5)
        else:
            plt.scatter(i, 0, color='black', s=5)

    plt.title("Number of Drones Reaching Maximum Distance, 250 Nodes")
    plt.xlabel('Generation')
    plt.ylabel("Number of Drones to Reach Maximum Distance")
    plt.show()

def plotTargetScores(data):
    generations = len(data)

    plt.figure()
    for i in range(len(data)):
        if data[i]:
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

    # plotComparisons(lol.meanPopTotals, lol.meanPopDistance, lol.meanPopTargets, lol.popSizeLabels, "Population Size")
    # plotComparisons(lol.changingPopTotals, lol.changingPopDistance, lol.changingPopTargets, lol.popSizeLabels, "Population Size")

    # postprocessing.plotAll(lol.thousandGens, "Thousand Generations")
    # plot3D(lol.thousandGens60)
    # y1 = [item for item in lol.run64 if item[1] == 4000]
    # y2 = [item[2] for item in y1]
    # plotOneValue(y2)
    # plotDataBestPlane(lol.example3D_run4)

    # plotTargetScores(ml.fourk_101)
    plotNumReachMax(ml.fourk_101)
    plotNumReachMax(ml.fourk_107)