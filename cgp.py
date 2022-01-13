import copy
import operator as op
import random
import settings as st
import numpy as np


# Class for possible mathematical functions that are mapped to nodes
class Function:

    def __init__(self, action, arity):
        """
        Constructor method
        :param action: mathematical operator (add, subtract, etc.)
        :param arity: rank (i.e., number of inputs allowed)
        """
        self.action = action
        self.arity = arity
        self.name = action.__name__

    def __call__(self, *args, **kwargs):
        """
        Used to allow the class to be called like a function
        (i.e., call the add operator and give it the required inputs)
        :param args: arguments of unknown length
        :param kwargs: key word arguments of unknown length
        :return: output of mathematical operator
        """
        return self.action(*args, **kwargs)


def div(a, b):
    """
    Prevent node outputs from accidentally getting
     too large by dividing by a super tiny number
    :param a: number
    :param b: number
    :return: result of division (or just a if b is too small)
    """
    #
    if abs(b) < 1e-6:
        return a
    else:
        return a / b


# Create the table of functions that will be used as the nodes of the graph
# Contains add, subtract, multiply, divide, and negate
functionTable = [Function(op.add, 2), Function(op.sub, 2), Function(op.mul, 2), Function(div, 2), Function(op.neg, 1)]


# Class for each node in the CGP
class Node:

    def __init__(self):
        self.functionIndex = None       # Index of the mathematical function of the node (from functionTable)
        self.inputIndices = []          # The node indices of the input values for the given node
        self.inputWeights = []          # The weights of the inputs (randomly chosen)
        self.output = None              # Output value of node
        self.active = False             # Whether node is active i.e., connected to a final output


class Individual:
    """
    A single genotype - takes 5 inputs, has a bunch of nodes connected up, then gives an output
    """
    def __init__(self):
        self.functionTable = functionTable      # Table of functions that can be set for each node
        self.weightMin = -1                     # Min weight for each input
        self.weightMax = 1                      # Max weight for each input
        self.numInputs = 5                      # Set the number of inputs - currently 5 - v, g, h, vr, and hr
        self.numOutputs = 2                     # Set the number of outputs for the graph
        self.numNodes = st.N_COLS               # Set the number of nodes for each genotype
        self.nodes = []                         # Initialize empty list to hold all the node objects
        self.totalFitness = 0                   # Initialize totalFitness value of the genotype to 0
        self.distanceFitness = 0                # Initialize distanceFitness value of the genotype to 0
        self.targetFitness = 0                  # Initialize targetFitness value of the genotype to 0
        self.levelsBack = self.numNodes         # Set levels back equivalent to the total number of nodes
        self.activeNodesDetermined = False      # Tells whether the active nodes have been found
        self.activeNodes = 0                    # Number of nodes active for individual
        self.createNodes()                      # Call function to create all the nodes and link them

    def createNodes(self):
        """
        Create each node and connect it to
        the required number of inputs
        :return: none
        """
        for nodeIndex in range(self.numNodes):
            node = Node()                   # Create an instance of the node class
            self.nodes.append(node)         # Append the new node to the list of nodes

            # Randomly choose what function the node is (i.e., addition, multiplication, etc.)
            node.functionIndex = random.randint(0, len(self.functionTable) - 1)

            # Randomly set weights and input nodes for this node (iterates through each input)
            for y in range(self.functionTable[node.functionIndex].arity):
                # Note, this line would need to be changed if self.levelsBack != self.numNodes
                node.inputIndices.append(random.randint(0 - self.numInputs, nodeIndex - 1))
                node.inputWeights.append(random.uniform(self.weightMin, self.weightMax))

        # Set all the output nodes (last x number in the list of nodes) to active
        for x in range(1, self.numOutputs + 1):
            self.nodes[-x].active = True

    def determineActiveNodes(self):
        """
        Determines which nodes are actually connected via boolean set for each node object -
        used to evaluate total expression
        :return: none
        """
        activeNodes = 0
        # Reverse the list so we can work backward from the outputs which are always active
        for node in reversed(self.nodes):
            # If the present node is active (if it isn't, then the ones its connected to aren't either - they dead end)
            # First node in reversed list is always active, because it's the final output
            if node.active:
                activeNodes += 1
                # For every index value of the given node's input nodes...
                for i in range(len(node.inputIndices)):
                    # If the input index is a real, non-zero number (i.e., not None, indicating no connection)
                    if node.inputIndices[i] >= 0:
                        # Set the node that provided the inputs to active
                        self.nodes[node.inputIndices[i]].active = True
        self.activeNodes = activeNodes

    def eval(self, *args):
        """
        Evaluate the genotype to determine outputs and govern behavior
        :param args: initial input values (in this case, v, h ,g , vr, and hr
        :return: final outputs of the CGP individual
        """
        # Check active nodes - has to be done after every mutation, but can be skipped for parent planes
        if not self.activeNodesDetermined:
            self.determineActiveNodes()
            self.activeNodesDetermined = True

        for node in self.nodes:
            # Only evaluate active nodes
            if node.active:
                inputs = []
                # For all the inputs to the given node
                for inputIndex in node.inputIndices:
                    # If input index is in the list, then append it's output to the list of inputs for the given node
                    if inputIndex >= 0:
                        inputs.append(self.nodes[inputIndex].output)
                    # If input index is less than 0 (i.e., not in the node list), then it is an original input
                    # i.e., v, g, h, vr, or hr and should be added to the list of inputs for the given node
                    # That awful weights part is making sure the weight with the same index as the input is applied
                    elif inputIndex < 0:
                        inputs.append(args[-inputIndex - 1] * node.inputWeights[node.inputIndices.index(inputIndex)])
                # After all the appropriate inputs have been collected, do the appropriate math operator on them
                # and save it as the node output for use by later nodes
                node.output = self.functionTable[node.functionIndex](*inputs)

        # Return the final output values
        return self.nodes[-1].output, self.nodes[-2].output

    def mutate(self, mutRate):
        """
        Create children from parents through mutation
        :param mutRate: Mutation rate (value from 0 to 1)
        :return: a new Individual object
        """
        # Creates a child genotype to be mutated, leaving the parent genotype untouched
        child = copy.deepcopy(self)

        # Iterates through every node
        for node in child.nodes:
            # If randomly chosen to mutate, randomly choose a new function (math operator) for the node
            if random.random() < mutRate:
                node.functionIndex = random.randint(0, len(child.functionTable) - 1)

            # Grab old weight/input values and then clear them - done to allow list re-sizing in case the new
            # function has a different arity than the old function
            oldInputIndices = node.inputIndices
            oldWeightIndices = node.inputWeights
            node.inputIndices = []
            node.inputWeights = []

            # Iterate through every input to see if it will mutate
            for inputIndex in reversed(range(child.functionTable[node.functionIndex].arity)):
                # If randomly chosen to mutate, append the new index value
                if random.random() < mutRate:
                    node.inputIndices.append(random.randint(0 - child.numInputs, child.nodes.index(node) - 1))
                    # Try except used to keep the same weights if possible, or add a new one if the previous
                    # arity was only one and a new function is chosen with an arity of two
                    try:
                        node.inputWeights.append(oldWeightIndices[inputIndex])
                    except IndexError:
                        node.inputWeights.append(random.uniform(self.weightMin, self.weightMax))
                # If the new function takes more inputs than the old function, append new random inputs/weights
                elif inputIndex > len(node.inputIndices):
                    node.inputIndices.append(random.randint(0 - child.numInputs, child.nodes.index(node) - 1))
                    node.inputWeights.append(random.uniform(child.weightMin, child.weightMax))
                # If the input index isn't mutated and an input already exists, put it and the weight back where it was
                else:
                    node.inputIndices.append(oldInputIndices[inputIndex])
                    node.inputWeights.append(oldWeightIndices[inputIndex])
            # Reset all the nodes back to inactive as a default
            node.active = False

        # Set all the final output nodes (last x number in the list of nodes) to active
        for x in range(1, child.numOutputs + 1):
            child.nodes[-x].active = True

        # Reset default values
        child.totalFitness = 0
        child.distanceFitness = 0
        child.targetFitness = 0
        child.activeNodesDetermined = False

        return child


"""This evolve was used for the bulk of modelling"""
def evolve(pop, mutRate, numParents, numChildren, parentWeights):
    """
    Evolve the entire population for a new generation
    :param pop: List of individuals from the previous generation
    :param mutRate: Mutation rate (float between 0 and 1)
    :param numParents: List of parents to spawn children (MU from settings)
    :param numChildren: How many children to spawn (LAMBDA from settings)
    :param parentWeights: A weight list for how to choose parents (i.e., to prefer parents that fly far)
    :return: list of new population
    """
    # Sort population by fitness for every category
    pop0 = sorted(pop, key=lambda genotype: genotype.totalFitness)
    pop1 = sorted(pop, key=lambda genotype: genotype.distanceFitness)
    pop2 = sorted(pop, key=lambda genotype: genotype.targetFitness)

    # Slice off the fittest numParents for each category to be parents of the next generation
    parents = pop0[-numParents[0]:] + pop1[-numParents[1]:] + pop2[-numParents[2]:]

    # If multiple individuals are the same (i.e. the same individual had highest total score and highest fitness), then
    # discard the repeats and choose the next fittest parent distance wise (didn't use a set b/c wanted to keep order)
    parentSet = list(dict.fromkeys(parents))        # Get set of parents (with order) without repeats
    sumParents = sum(numParents)                    # Sum how many unique parents there are
    newParent = numParents[1]             # Set newParent equal to the index of the numParents for distance fitness
    while len(parentSet) < sumParents:              # As long as the set of parents is less than the list of parents
        newParent += 1                              # Add one to newParent (iterates through pop list backwards)
        parentSet.append(pop1[-newParent])          # Add the new parent to the set
        parentSet = list(dict.fromkeys(parentSet))  # Check if the new parent is a repeat also by re-generating the list

    # Weigh the likelihood of which parents get chosen - i.e., parents with good distance can get chosen more often
    if parentWeights is None:
        weightedParents = random.choices(parentSet)
    else:
        weightedParents = random.choices(parentSet, cum_weights=parentWeights)

    # Initialize an empty list to hold the kiddos
    children = []

    # Pick a parent at random and add their mutated genotype to the list of children
    for _ in range(numChildren):
        parent = random.choice(weightedParents)
        children.append(parent.mutate(mutRate))

    return parents + children


"""This evolve was used to test an increase in genetic diversity by allowing the entire population to spawn"""
# def evolve(pop, mutRate, numParents, numChildren, parentWeights):
#     # Sort population to find the ones with highest fitness for all categories
#     pop0 = sorted(pop, key=lambda genotype: genotype.totalFitness)
#     pop1 = sorted(pop, key=lambda genotype: genotype.distanceFitness)
#     pop2 = sorted(pop, key=lambda genotype: genotype.targetFitness)
#
#     parents = pop0[-numParents[0]:] + pop1[-numParents[1]:] + pop2[-numParents[2]:]
#
#     # Slightly weight the fittest half of the population (increasingly) to be selected as parents more often,
#     weightList = np.ones(len(pop0))
#     for i in range(int(len(pop0)/1.5), len(pop0)):
#         weightList[i] *= (1+(i/10))
#
#     # Have parents be chosen from amongst the entire population to create more diversity
#     weightedParents = random.choices(pop0, cum_weights=weightList)
#
#     # Initialize an empty list to hold the kiddos
#     children = []
#
#     # Pick a parent at random and add their mutated genotype to the list of lil kids
#     for _ in range(numChildren):
#         parent = random.choice(weightedParents)
#         children.append(parent.mutate(mutRate))
#
#     return parents + children


def createPopulation(popSize):
    """
    Create a new population
    :param popSize: Number of individuals in the population
    :return: List of Individual objects
    """
    return [Individual() for _ in range(popSize)]


def calculateAvgActiveNodes(population):
    """
    Calculate the average number of active nodes
    for a given population of individuals
    :param population: list of Individual objects
    :return: average number of active nodes
    """
    listActiveNodes = [individual.activeNodes for individual in population]
    return np.mean(listActiveNodes)