import tkinter as tk

from canvas_frame import CanvasFrame
from tool_frame import ToolFrame

# screen dimensions
WIDTH = 1280
HEIGHT = 720


class NodeApplication(tk.Tk):
    """
    Specialisation of the standard Tk application to provide the
    NodeDemonstrator.
    """

    def __init__(self):
        super().__init__()
        self.title("Node Demonstrator")
        self.geometry(f"{WIDTH}x{HEIGHT}+10+10")

        self.canvas = CanvasFrame(self).grid(column=0, row=0, sticky=tk.NSEW)
        self.tools = ToolFrame(self).grid(column=1, row=0, sticky=tk.NSEW)

        self.columnconfigure(0, weight=85)
        self.columnconfigure(1, weight=15)
        self.rowconfigure(0, weight=1)


if __name__ == "__main__":
    app = NodeApplication()
    app.mainloop()
