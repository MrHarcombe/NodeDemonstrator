import tkinter as tk
from tkinter import ttk


class UsageControlsFrame(ttk.Frame):
    """
    Class for working with the drawn graph - algorithms such as standard
     traversals like BFS, DFS as well as path-finding using Dijkstra or
     A*, and other algorithms will be triggered (and the results displayed)
     here.
    """

    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="This will be the graph usage frame").grid()
