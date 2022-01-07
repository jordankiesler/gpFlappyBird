"""
There need to be functions represented as nodes
There need to be genotypes, which are individuals in the population
There need to be nodes, which include the inputs (?)
There need to be outputs - are these also nodes?
"""
import copy
import operator as op
import random


class Function:

    def __init__(self, action, arity):
        self.action = action
        self.arity = arity
        self.name = action.__name__

    # Used to allow the class to be called like a function (i.e., call the add operator and give it the required inputs)
    def __call__(self, *args, **kwargs):
        return self.action(*args, **kwargs)


def div(a, b):
    # Prevent number from getting too large by dividing by a super tiny number
    if abs(b) < 1e-6:
        return a
    else:
        return a/b


# Create the table of functions that will be used as the nodes of the graph
# Contains add, subtract, multiply, divide, and negate
functionTable = [Function(op.add, 2), Function(op.sub, 2), Function(op.mul, 2), Function(div, 2), Function(op.neg, 1)]


class Node:

    def __init__(self):
        self.functionIndex = None
        self.inputIndices = []
        self.inputWeights = []
        self.outputIndex = None
        self.output = None
        self.active = False


class Genotype:
    """
    A single genotype - takes 3 inputs, has a bunch of nodes connected up, then gives an output
    """

    def __init__(self):
        self.functionTable = functionTable  # Table of functions that can be set for each node
        self.weightMin = -1                 # Min weight for each input
        self.weightMax = 1                  # Max weight for each input
        self.numInputs = 3                  # Set the number of inputs - currently 3 - v, g, and h
        self.numOutputs = 1                 # Set the number of outputs for the graph (currently 1 - flap or not)
        self.numNodes = 100                 # Set the number of nodes for each genotype
        self.nodes = []                     # Initialize empty list to hold all the node objects
        self.fitness = 0                    # Initialize totalFitness value of the genotype to 0
        self.levelsBack = self.numNodes     # Set levels back equivalent to the total number of nodes
        self.activeNodesDetermined = False  # Tells whether the active nodes have been found
        self.createNodes()                  # Call function to create all the nodes and link them

    def createNodes(self):
        # Create and connect each node
        for nodeIndex in range(self.numNodes):
            # Create an instance of the node class
            node = Node()
            # Append the new node to the list of nodes
            self.nodes.append(node)
            node.outputIndex = nodeIndex
            # Randomly choose what function the node is (i.e., addition, multiplication, etc.)
            node.functionIndex = random.randint(0, len(self.functionTable) - 1)
            # Randomly set weights and input nodes for this node (iterates through each input)
            for y in range(self.functionTable[node.functionIndex].arity):
                # TODO: Make sure this is okay compared to how he does it with initializing length of input lists 1st
                # Note, this line would need to be changed if self.levelsBack != self.numNodes
                node.inputIndices.append(random.randint(0-self.numInputs, nodeIndex - 1))
                node.inputWeights.append(random.uniform(self.weightMin, self.weightMax))

        # Set all the output nodes (last x number in the list of nodes) to active
        for x in range(1, self.numOutputs + 1):
            self.nodes[-x].active = True

    # Determines which nodes are actually connected - used to evaluate total expression
    def determineActiveNodes(self):
        activeNodes = 0
        # Reverse the list so we can work backward from the outputs
        for node in reversed(self.nodes):
            # If the present node is active (if it isn't, then the ones its connected to aren't either - they dead end)
            # First node in reversed list is always active, because it's the output
            if node.active:
                activeNodes += 1
                # For every index value of the given node's input nodes...
                for i in range(0, len(node.inputIndices)):
                    # Set the node that provided the inputs to active
                    self.nodes[node.inputIndices[i]].active = True

    # Provided args are the values to go into the evaluation - in this case, v, h, and g
    def calculateOutput(self, *args):
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
                    # If input index is >=0 (i.e., a node in the graph), then append it's output to the list of inputs
                    if inputIndex >= 0:
                        inputs.append(self.nodes[inputIndex].output)
                    # If input index is less than 0 (i.e., not in the node list), then it is an original input
                    # i.e., v, g, or h and should be added as appropriately
                    # That awful weights part is making sure the weight with the same index as the input is applied
                    elif inputIndex < 0:
                        inputs.append(args[-inputIndex - 1] * node.inputWeights[node.inputIndices.index(inputIndex)])
                # After all the appropriate inputs have been collected, do the appropriate math on them
                node.output = self.functionTable[node.functionIndex](*inputs)
        # Return the final output value
        # TODO: This will have to be updated if there are multiple output values
        return self.nodes[-1].output

    def mutate(self, mutRate):

        # Creates a child genotype to be mutated, leaving the parent genotype untouched
        child = copy.deepcopy(self)

        for node in child.nodes:
            # If randomly chosen to mutate, randomly choose a new function (math operator) for the node
            if random.random() < mutRate:
                node.functionIndex = random.randint(0, len(child.functionTable) - 1)
            # Iterate through every input to see if it will mutate
            oldInputIndices = node.inputIndices
            for inputIndex in reversed(range(child.functionTable[node.functionIndex].arity)):
                node.inputIndices = []
                # If randomly chosen to mutate, remove the existing value at that index and update it to the new node
                if random.random() < mutRate:
                    node.inputIndices.append(random.randint(0-child.numInputs, child.nodes.index(node) - 1))
                # If the new function takes more inputs than the old function
                elif inputIndex > len(node.inputIndices):
                    node.inputIndices.append(random.randint(0-child.numInputs, child.nodes.index(node) - 1))
                # If the input index isn't mutated and an input already exists, put it back where it was
                else:
                    node.inputIndices.append(oldInputIndices[inputIndex])
            # Reset all the nodes back to inactive as a default
            node.active = False

        # Set all the output nodes (last x number in the list of nodes) to active
        for x in range(1, child.numOutputs + 1):
            child.nodes[-x].active = True

        # Reset default values
        child.fitness = 0
        child.activeNodesDetermined = False

        return child

def evolvePop(pop, numChildren, numParents, mutRate):

    # Sort population to find the ones with highest totalFitness
    pop = sorted(pop, key=lambda genotype: genotype.totalFitness)

    # Slice off the fittest numParents to be parents of the next generation
    parents = pop[-numParents:]

    # Initialize an empty list to hold the kiddos
    children = []
    # Pick a parent at random and add their mutated genotype to the list of lil kids
    for _ in range(numChildren):
        parent = random.choice(parents)
        children.append(parent.mutate(mutRate))

    return parents + children


def createPopulation(popSize):
    return [Genotype() for _ in range(popSize)]
