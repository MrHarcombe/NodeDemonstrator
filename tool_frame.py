# import tkinter as tk
# from tkinter import ttk
import customtkinter as ctk

from draw_controls_frame import DrawControlsFrame
from usage_controls_frame import UsageControlsFrame


class ToolFrame(ctk.CTkTabview):
    """
    Class to handle setting up the Notebook which holds all the control frames apart from the actual Canvas.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.__tabs = [
            DrawControlsFrame(self.add("Draw")).pack(expand=True, fill=ctk.BOTH),
            UsageControlsFrame(self.add("Algorithms")).pack(expand=True, fill=ctk.BOTH),
        ]
