import tkinter as tk
from tkinter import ttk

from draw_controls_frame import DrawControlsFrame
from usage_controls_frame import UsageControlsFrame


class ToolFrame(ttk.Notebook):
    """
    Class to handle setting up the Notebook which holds all the control frames apart from the actual Canvas.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.__tabs = [DrawControlsFrame(self), UsageControlsFrame(self)]

        self.add(self.__tabs[0], text="Draw")
        self.add(self.__tabs[1], text="Algorithms")
