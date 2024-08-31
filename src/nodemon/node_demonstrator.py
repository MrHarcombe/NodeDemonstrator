import customtkinter as ctk
import tkinter.messagebox as messagebox

from .canvas_frame import CanvasFrame
from .tool_frame import ToolFrame
from .state_model import StateModel

# screen dimensions
WIDTH = 1280
HEIGHT = 720


class NodeApplication(ctk.CTk):
    """
    Specialisation of the standard Tk application to provide the
    NodeDemonstrator.
    """

    def __init__(self):
        super().__init__()
        self.title("Node Demonstrator")
        self.geometry(f"{WIDTH}x{HEIGHT}+10+10")

        self.canvas = CanvasFrame(self)
        self.canvas.grid(column=0, row=0, sticky=ctk.NSEW)

        self.tools = ToolFrame(self, self.canvas)
        self.tools.grid(column=1, row=0, sticky=ctk.NSEW)

        self.columnconfigure(0, weight=1)
        # self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

    def destroy(self):
        if (
            StateModel().is_changed()
            and messagebox.askyesno(
                message="Graph has changes. Continue and lose all changes?"
            )
            != ctk.YES
        ):
            return False

        self.quit()


def main():
    app = NodeApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
