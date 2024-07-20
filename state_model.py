from itertools import chain, product
from string import ascii_uppercase
from animated_structures import AnimatedMatrixGraph, AnimatedWeightedMatrixGraph


class StateModel:
    """
    Singleton object provided Pythonically by overriding __new__ to allow only only instance at a time. Current graph
    being worked on through the Canvas is held (and interacted upon) in here.
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(StateModel, cls).__new__(cls)

            # Put any initialization here.
            cls.__instance.__graph = AnimatedWeightedMatrixGraph()
            cls.__instance.__filename = None
            cls.__instance.__operation = "Nodes"
            cls.__instance.__directed = False
            cls.__instance.__weight = 1
            cls.__instance.__changed = False
            cls.__instance.__generator = StateModel.__next_node_name_generator()

        return cls.__instance

    def __next_node_name_generator():
        """
        Based on an answer from one of the answers at
        https://stackoverflow.com/questions/42176498/repeating-letters-like-excel-columns
        generates the next node name in an Excel-like sequence of letters (up to a finite, if improbably large, limit
        of 1,000 uppercase characters).
        """
        yield from chain(*[product(ascii_uppercase, repeat=i) for i in range(1, 1_000)])

    def create_new(self, weighted=True):
        # need to check if changed, and if so save the current
        if self.__changed:
            pass

        # ask if the graph is to be weighted
        if weighted:
            self.__graph = AnimatedWeightedMatrixGraph()
            self.__weight = 1
        else:
            self.__graph = AnimatedMatrixGraph()
            self.__weight = None

        # restart the node name generator
        self.__generator = StateModel.__next_node_name_generator()

        # whatever was created, nothing has yet been changed (but will need this to think about saving later)
        self.__changed = False

    def get_graph_matrix(self):
        return self.__graph.matrix

    def set_graph_matrix(self, saved_matrix):
        self.__graph.matrix = saved_matrix
        last_node = max(self.__graph.matrix[0])

        # restart the node name generator
        self.__generator = StateModel.__next_node_name_generator()

        while self.get_next_node_name() < last_node:
            pass

    def is_weighted(self):
        return isinstance(self.__graph, AnimatedWeightedMatrixGraph)

    def set_operation_parameters(self, mode, directed, cost):
        self.__operation = mode
        self.__directed = directed
        self.__weight = cost

    def get_operation(self):
        return self.__operation

    def get_directed(self):
        return self.__directed

    def get_weight(self):
        return self.__weight

    def get_next_node_name(self):
        return "".join(next(self.__generator))

    def add_node(self, node_name):
        self.__graph.add_node(node_name)
        print(self.__graph.matrix)

    def delete_node(self, node_name):
        self.__graph.delete_node(node_name)
        print(self.__graph.matrix)

    def has_edge(self, from_node, to_node):
        return self.__graph.is_connected(from_node, to_node)

    def add_edge(self, from_node, to_node, undirected=False, weight=1):
        if isinstance(self.__graph, AnimatedWeightedMatrixGraph):
            self.__graph.add_edge(from_node, to_node, weight, undirected)
        else:
            self.__graph.add_edge(from_node, to_node, undirected)
        print(self.__graph.matrix)

    def delete_edge(self, node_from, node_to):
        self.__graph.delete_edge(node_from, node_to)
        print(self.__graph.matrix)

    def breadth_first(self, start_node, end_node=None):
        yield from self.__graph.breadth_first(start_node, end_node)
