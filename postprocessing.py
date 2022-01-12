"""Postprocess the graph evolved by CGP.

- Simplify the obtained math formula.
- Visualize the expression tree corresponding to the formula that is embedded in the CGP graph.

Reference
1. [`geppy.support.simplification`](https://geppy.readthedocs.io/en/latest/geppy.support.html#module-geppy.support.simplification).
2. [Binary expression tree](https://en.wikipedia.org/wiki/Binary_expression_tree). Note that the operators are not required
to be binary though.
"""
import sympy as sp
import operator
import math
from typing import Dict, Sequence
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

import cgp
import settings as st

runNum = 0


# Map Python functions to sympy counterparts for symbolic simplification.
DEFAULT_SYMBOLIC_FUNCTION_MAP = {
    operator.add.__name__: operator.add,
    operator.sub.__name__: operator.sub,
    operator.mul.__name__: operator.mul,
    operator.neg.__name__: operator.neg,
    'div': operator.truediv,
}


def writeRunToFile(generation, maxTotalScoreSoFar, maxDistanceScoreSoFar, maxTargetScoreSoFar,
                   maxTotalList, maxTotalSoFarList, maxDistanceList, maxDistanceSoFarList, maxTargetList,
                   maxTargetSoFarList, bestPlaneScoresList, numTargets):

    content = open('./pp/numRuns.txt', 'r').readlines()
    global runNum
    runNum = int(content[0])
    content[0] = str(runNum + 1)
    out = open('./pp/numRuns.txt', 'w')
    out.writelines(content)
    out.close()

    sortedPlanes = sorted(bestPlaneScoresList, key=lambda score: score[0])

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
           f"Number of Columns: {st.N_COLS}\n" \
           f"Number of Levels Back: {st.LEVEL_BACK}\n" \
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


def plotAll(data, fourK, title):

    plt.figure()
    for i in range(len(data)):
        for j in range(len(data[i])):
        # x = np.ones(len(data[i]))
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

    # Open the file in append & read mode ('a+')
    with open("./pp/allScores.txt", "a+") as file:
    # with open("./pp/trainingDataChangedBullets.txt", "a+") as file:
        # Get what run number it is

        # Move read cursor to the start of file.
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

    # Open the file in append & read mode ('a+')
    with open("./pp/4kAverages.txt", "a+") as file:
    # with open("./pp/trainingDataChangedBullets.txt", "a+") as file:
        # Get what run number it is

        # Move read cursor to the start of file.
        file.seek(0)
        # If file is not empty then append '\n'
        data = file.read(100)
        if len(data) > 0:
            file.write("\n\n")
        # Append text at the end of file
        file.write(text2)

    plt.show()


def extract_computational_subgraph(ind: cgp.Individual) -> nx.MultiDiGraph:
    """Extract a computational subgraph of the CGP graph `ind`, which only contains active nodes.

    Args:
        ind (cgp.Individual): an individual in CGP  

    Returns:
        nx.DiGraph: a acyclic directed graph denoting a computational graph

    See https://www.deepideas.net/deep-learning-from-scratch-i-computational-graphs/ and 
    http://www.cs.columbia.edu/~mcollins/ff2.pdf for knowledge of computational graphs.
    """
    # make sure that active nodes have been confirmed
    if not ind.activeNodesDetermined:
        ind.determineActiveNodes()
        ind.activeNodesDetermined = True
    # in the digraph, each node is identified by its index in `ind.nodes`
    # if node i depends on node j, then there is an edge j->i
    g = nx.MultiDiGraph()  # possibly duplicated edges
    for i, node in enumerate(ind.nodes):
        if node.active:
            f = ind.functionTable[node.functionIndex]
            g.add_node(i, func=f.name)
            order = 1
            for j in range(f.arity):
                i_input = node.inputIndices[j]
                w = node.inputWeights[j]
                g.add_edge(i_input, i, weight=w, order=order)
                order += 1

    return g


def simplify(g: nx.MultiDiGraph, input_names: Sequence = None, symbolic_function_map: Dict = None):
    """Compile computational graph `g` into a (possibly simplified) symbolic expression.

    Args:
        g (nx.MultiDiGraph): a computational graph
        symbolic_function_map ([Dict], optional): Map each function to a symbolic one in `sympy`. Defaults to None.
            If `None`, then the `DEFAULT_SYMBOLIC_FUNCTION_MAP` is used.
        input_names (Sequence): a list of names, each for one input. If `None`, then a default name "vi" is used
            for the i-th input.
    
    Return:
        a (simplified) symbol expression
    
    For example, `add(sub(3, 3), x)` may be simplified to `x`. Note that this method is used to simplify the 
    **final** solution rather than during evolution. 
    """
    if symbolic_function_map is None:
        symbolic_function_map = DEFAULT_SYMBOLIC_FUNCTION_MAP

    # toplogical sort such that i appears before j if there is an edge i->j
    ts = list(nx.topological_sort(g))
    d = dict()
    for node_id in ts:
        if node_id < 0:  # inputs in CGP
            d[node_id] = sp.Symbol(
                f"v{-node_id}" if input_names is None else input_names[-node_id - 1])
        else:  # a function node
            inputs = []
            # print(g.in_edges(node_id))
            for input_node_id in g.predecessors(node_id):
                # possibly parallel edges
                for attr in g.get_edge_data(input_node_id, node_id).values():
                    inputs.append(
                        (input_node_id, attr["weight"], attr["order"]))
            inputs.sort(key=operator.itemgetter(2))
            args = (ip[1] * d[ip[0]] for ip in inputs)
            func = g.nodes[node_id]["func"]
            sym_func = symbolic_function_map[func]
            r = sym_func(*args)
            d[node_id] = sp.simplify(r) if st.PP_FORMULA_SIMPLIFICATION else r
    # the unique output is the last node
    return d[ts[-1]]


def round_expr(expr, num_digits):
    # https://stackoverflow.com/questions/48491577/printing-the-output-rounded-to-3-decimals-in-sympy
    return expr.xreplace({n: round(n, num_digits) for n in expr.atoms(sp.Number)})

