import customtkinter as ctk

from .draw_controls_frame import DrawControlsFrame
from .usage_controls_frame import UsageControlsFrame


class ToolFrame(ctk.CTkTabview):
    """
    Class to handle setting up the Notebook which holds all the control frames apart from the actual Canvas.
    """

    def __init__(self, parent, canvas_frame):
        super().__init__(parent)
        self.__tabs = [
            DrawControlsFrame(
                self.add("Draw"),
                canvas_frame,
            ).pack(expand=True, fill=ctk.BOTH),
            UsageControlsFrame(
                self.add("Algorithms"),
                canvas_frame,
            ).pack(expand=True, fill=ctk.BOTH),
            RepresentationFrame(
                self.add("Representation"),
                canvas_frame,
            ).pack(expand=True, fill=ctk.BOTH),
        ]
