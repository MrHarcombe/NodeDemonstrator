import ttkbootstrap as ttk
import ttkbootstrap.constants as tk

from .draw_controls_frame import DrawControlsFrame
from .usage_controls_frame import UsageControlsFrame


class ToolFrame(ttk.Notebook):
    """
    Class to handle setting up the Notebook which holds all the control frames apart from the actual Canvas.
    """

    def __init__(self, parent, canvas_frame):
        super().__init__(parent, bootstyle="secondary")
        self.__tabs = [
            DrawControlsFrame(
                self,
                canvas_frame,
            ),
            UsageControlsFrame(
                self,
                canvas_frame,
            )
        ]

        self.add(self.__tabs[0], text="Draw")
        self.add(self.__tabs[1], text="Algorithms")
