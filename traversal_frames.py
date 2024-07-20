import customtkinter as ctk

from state_model import StateModel
from trace_frame import TraceFrame


class ProcessedScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, label_text="Processed Nodes", label_anchor=ctk.CENTER)


class PendingQueueScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, label_text="Pending Queue", label_anchor=ctk.CENTER)


class PendingStackScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, label_text="Pending Stack", label_anchor=ctk.CENTER)


class BreadthFirstFrame(TraceFrame):
    def __init__(self, master, canvas_frame, from_node, to_node):
        if to_node is None or len(to_node.strip()) == 0:
            title = f"Breadth First Traversal from {from_node}"
        else:
            title = f"Breadth First Search from {from_node} to {to_node}"

        super().__init__(master, canvas_frame, title)
        self.__from = from_node
        self.__to = to_node
        self._iterator = iter(StateModel().breadth_first(self.__from, self.__to))

        self.__processed = ProcessedScrollableFrame(self)
        self.__processed.grid(sticky=ctk.NSEW, pady=(0, 15))

        self.__other = PendingQueueScrollableFrame(self)
        self.__other.grid(sticky=ctk.NSEW, pady=(0, 15))

        self.columnconfigure(0, weight=1)

    def display_current(self, current):
        pass

    def display_processed(self, processed):
        pass

    def display_other(self, other):
        pass


class DepthFirstFrame(TraceFrame):
    def __init__(self, master, canvas_frame, from_node, to_node):
        super().__init__(master, canvas_frame)
        self.__from = from_node
        self.__to = to_node
