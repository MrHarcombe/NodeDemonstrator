import ttkbootstrap as ttk
import ttkbootstrap.constants as tk
import ttkbootstrap.tableview as tableview

from .state_model import StateModel


class RepresentationFrame(ttk.Frame):
    def __init__(self, parent, canvas_frame):
        super().__init__(parent)
        self.__canvas_frame = canvas_frame

        self.bind(
            "<Expose>",
            lambda event: StateModel().set_current_tab(self.__class__.__name__),
        )
