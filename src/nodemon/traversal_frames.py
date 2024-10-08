import customtkinter as ctk

from .state_model import StateModel
from .trace_frame import TraceFrame, CustomScrollableFrame


class TraversalFrame(TraceFrame):
    def __init__(self, master, canvas_frame, title, from_node, to_node):
        super().__init__(master, canvas_frame, title, from_node, to_node)

    def display_processed(self, processed):
        for child in self._processed.winfo_children():
            child.grid_remove()

        if len(processed) == 0:
            self._processed.columnconfigure(0, weight=1)
            self._processed.columnconfigure((1, 2), weight=0)

            sub = ctk.CTkFrame(
                self._processed,
                border_width=2,
                border_color="black",
            )
            sub.grid(
                sticky=ctk.NSEW,
            )
            sub.columnconfigure(0, weight=1)

            ctk.CTkLabel(
                sub,
                text="Empty",
                anchor=ctk.CENTER,
            ).grid(
                sticky=ctk.NSEW,
                padx=8,
                pady=3,
            )

        else:
            row = 0
            column = 0
            self._processed.columnconfigure((0, 1, 2), weight=1)

            for p in processed:
                self._canvas_frame.highlight_processed_node(p)

                sub = ctk.CTkFrame(
                    self._processed,
                    border_width=2,
                    border_color="black",
                )
                sub.grid(
                    sticky=ctk.NSEW,
                    row=row,
                    column=column,
                )
                sub.columnconfigure(0, weight=1)

                ctk.CTkLabel(
                    sub,
                    text=p,
                    anchor=ctk.CENTER,
                ).grid(
                    sticky=ctk.NSEW,
                    padx=8,
                    pady=3,
                )

                column += 1
                if column > 2:
                    row += 1
                    column = 0

    def display_other(self, other):
        for child in self._other.winfo_children():
            child.grid_remove()

        if len(other) == 0:
            self._other.columnconfigure(0, weight=1)
            self._other.columnconfigure((1, 2), weight=0)

            sub = ctk.CTkFrame(
                self._other,
                border_width=2,
                border_color="black",
            )
            sub.grid(
                sticky=ctk.NSEW,
            )
            sub.columnconfigure(0, weight=1)

            ctk.CTkLabel(
                sub,
                text="Empty",
                anchor=ctk.CENTER,
            ).grid(
                sticky=ctk.NSEW,
                padx=8,
                pady=3,
            )

        else:
            row = 0
            column = 0
            self._other.columnconfigure((0, 1, 2), weight=1)

            for p in other:
                self._canvas_frame.highlight_pending_node(p)

                sub = ctk.CTkFrame(
                    self._other,
                    border_width=2,
                    border_color="black",
                )
                sub.grid(
                    sticky=ctk.NSEW,
                    row=row,
                    column=column,
                )
                sub.columnconfigure(0, weight=1)

                ctk.CTkLabel(
                    sub,
                    text=p,
                    anchor=ctk.CENTER,
                ).grid(
                    sticky=ctk.NSEW,
                    padx=8,
                    pady=3,
                )

                column += 1
                if column > 2:
                    row += 1
                    column = 0


class BreadthFirstFrame(TraversalFrame):
    def __init__(self, master, canvas_frame, from_node, to_node):
        if to_node is None or len(to_node.strip()) == 0:
            title = f"Breadth First Traversal from {from_node}"
        else:
            title = f"Breadth First Search from {from_node} to {to_node}"

        super().__init__(master, canvas_frame, title, from_node, to_node)
        self._iterator = iter(StateModel().breadth_first(self._from, self._to))
        self.initial_setup(
            lambda master: CustomScrollableFrame(master, "Processed Nodes"),
            lambda master: CustomScrollableFrame(master, "Pending Queue"),
        )


class DepthFirstFrame(TraversalFrame):
    def __init__(self, master, canvas_frame, from_node, to_node):
        if to_node is None or len(to_node.strip()) == 0:
            title = f"Depth First Traversal from {from_node}"
        else:
            title = f"Depth First Search from {from_node} to {to_node}"

        super().__init__(master, canvas_frame, title, from_node, to_node)
        self._iterator = iter(StateModel().depth_first(self._from, self._to))
        self.initial_setup(
            lambda master: CustomScrollableFrame(master, "Processed Nodes"),
            lambda master: CustomScrollableFrame(master, "Pending Stack"),
        )

class TreeTraversalFrame(TraversalFrame):
    def __init__(self, master, canvas_frame, traversal, from_node, to_node):
        if to_node is None or len(to_node.strip()) == 0:
            title = f"{traversal}-Order Tree Traversal from {from_node}"
        else:
            title = f"{traversal}-Order Tree Search from {from_node} to {to_node}"

        super().__init__(master, canvas_frame, title, from_node, to_node)
        match traversal:
            case "Pre":
                self._iterator = iter(StateModel().pre_order(self._from, self._to))
            case "In":
                self._iterator = iter(StateModel().in_order(self._from, self._to))
            case "Post":
                self._iterator = iter(StateModel().post_order(self._from, self._to))

        self.initial_setup(
            lambda master: CustomScrollableFrame(master, "Processed Nodes"),
            lambda master: CustomScrollableFrame(master, "Pending Stack"),
        )
