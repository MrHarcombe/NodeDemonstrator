import tkinter as tk
from tkinter import messagebox

from itertools import chain, product
from string import ascii_uppercase
from structures import MatrixGraph, WeightedMatrixGraph


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
            cls.__instance.__graph = WeightedMatrixGraph()
            cls.__instance.__filename = None
            cls.__instance.__operation = "Nodes"
            cls.__instance.__changed = True
            cls.__instance.__generator = StateModel.__next_node_name_generator()

        return cls.__instance

    def __next_node_name_generator():
        """
        Based on an answer from one of the answers at
        https://stackoverflow.com/questions/42176498/repeating-letters-like-excel-columns
        generates the next node name in an Excel-like sequence of letters (up to a finite, if improbably large, limit
        of 1000 uppercase characters).
        """
        yield from chain(*[product(ascii_uppercase, repeat=i) for i in range(1, 1_000)])

    def create_new(self):
        # need to check if changed, and if so save the current
        if self.__changed:
            pass

        # ask if the graph is to be weighted
        if messagebox.askyesno(message="Will the graph be weighted?") == tk.YES:
            self.__graph = WeightedMatrixGraph()
        else:
            self.__graph = MatrixGraph()

        # whatever was created, has now been changed (so need this to think
        # about saving later)
        self.__changed = True

    def load_existing(self):
        pass

    def save_current(self):
        pass

    def set_operation(self, operation):
        self.__operation = operation

    def get_operation(self):
        return self.__operation

    def get_next_node_name(self):
        return "".join(next(self.__generator))

    def add_node(self, node_name):
        self.__graph.add_node(node_name)

    def add_edge(self, from_node, to_node, undirected=False, weight=1):
        if isinstance(self.__graph, WeightedMatrixGraph):
            self.__graph.add_edge(from_node, to_node, weight, undirected)
        else:
            self.__graph.add_edge(from_node, to_node, undirected)