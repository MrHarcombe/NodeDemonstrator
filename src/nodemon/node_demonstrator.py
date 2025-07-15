import ttkbootstrap as ttk
import ttkbootstrap.constants as tk
import ttkbootstrap.dialogs as dialogs

from .canvas_frame import CanvasFrame
from .tool_frame import ToolFrame
from .state_model import StateModel

# screen dimensions
WIDTH = 1280
HEIGHT = 720


class NodeApplication(ttk.Window):
    """
    Specialisation of the standard Tk application to provide the
    NodeDemonstrator.
    """

    def __init__(self):
        super().__init__(themename="journal")
        self.title("Node Demonstrator")
        self.geometry(f"{WIDTH}x{HEIGHT}+10+10")

        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.grid(sticky=tk.NSEW)

        self.canvas = CanvasFrame(pane)
        pane.add(self.canvas, weight=14)

        self.tools = ToolFrame(pane, self.canvas)
        pane.add(self.tools, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def destroy(self):
        if (
            StateModel().is_changed()
            and dialogs.Messagebox.yesno(
                message="Graph has changes. Continue and lose all changes?"
            )
            != "Yes"
        ):
            return False

        super().destroy()


def main():
    app = NodeApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
