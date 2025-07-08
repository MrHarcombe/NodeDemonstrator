import ttkbootstrap as ttk
import ttkbootstrap.constants as tk

from .state_model import StateModel
from .trace_frame import TraceFrame, CustomScrollableFrame


class DijkstraShortestPathFrame(TraceFrame):
    def __init__(self, master, canvas_frame, from_node, to_node):
        if to_node is None or len(to_node.strip()) == 0:
            title = f"Dijkstra's Shortest Path from {from_node}"
        else:
            title = f"Dijkstra's Shortest Path from {from_node} to {to_node}"

        super().__init__(master, canvas_frame, title, from_node, to_node)
        self._iterator = iter(StateModel().dijkstra(self._from, self._to))
        self.initial_setup(
            lambda master: CustomScrollableFrame(master, "Current Data"),
            lambda master: CustomScrollableFrame(master, "Current Queue"),
        )

    
    def display_processed(self, processed):
        for child in self._processed.winfo_children():
            child.grid_remove()

        if len(processed) == 0:
            sub = ttk.Frame(self._processed, borderwidth=2)
            sub.grid(sticky=tk.NSEW)

            ttk.Label(sub, text="Empty", anchor=tk.CENTER, bootstyle="inverse-info").grid(
                sticky=tk.NSEW,
                padx=8,
                pady=3,
            )

            sub.columnconfigure(0, weight=1)
            self._processed.columnconfigure(0, weight=1)

        else:
            self._processed.columnconfigure(0, weight=1)

            for row, node in enumerate(sorted(processed, key=lambda node: self._canvas_frame.get_label_from_node(node))):
                cost, previous = processed[node]
                self._canvas_frame.highlight_processed_node(node)

                sub = ttk.Frame(self._processed, borderwidth=2)
                sub.grid(sticky=tk.NSEW)
                sub.columnconfigure((0, 1, 2), weight=1)

                ttk.Label(sub, text=self._canvas_frame.get_label_from_node(node), anchor=tk.CENTER, bootstyle="inverse-info").grid(
                    sticky=tk.NSEW,
                    padx=(8, 2),
                    pady=3,
                    row=row,
                    column=0,
                )

                ttk.Label(sub, text=cost, anchor=tk.CENTER, bootstyle="inverse-info").grid(
                    sticky=tk.NSEW,
                    padx=(2, 2),
                    pady=3,
                    row=row,
                    column=1,
                )

                ttk.Label(sub, text=(self._canvas_frame.get_label_from_node(previous) if previous is not None else "-"), anchor=tk.CENTER, bootstyle="inverse-info").grid(
                    sticky=tk.NSEW,
                    padx=(2, 8),
                    pady=3,
                    row=row,
                    column=2,
                )

    
    def display_other(self, other):
        for child in self._other.winfo_children():
            child.grid_remove()

        if len(other) == 0:
            sub = ttk.Frame(self._other, borderwidth=2)
            sub.grid(sticky=tk.NSEW)

            ttk.Label(sub, text="Empty", anchor=tk.CENTER, bootstyle="inverse-info").grid(
                sticky=tk.NSEW,
                padx=8,
                pady=3,
            )

            sub.columnconfigure(0, weight=1)
            self._other.columnconfigure(0, weight=1)

        else:
            self._other.columnconfigure(0, weight=1)

            # incoming tuples mean algorithm is still on-going
            if type(other[0]) is tuple:
                for row, (cost, node) in enumerate(sorted(other)):
                    self._canvas_frame.highlight_pending_node(node)
                    sub = ttk.Frame(self._other, borderwidth=2)
                    sub.grid(sticky=tk.NSEW, row=row)
                    sub.columnconfigure((0, 1), weight=1)

                    ttk.Label(sub, text=self._canvas_frame.get_label_from_node(node), anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=(8, 2),
                        pady=3,
                        row=row,
                        column=0,
                    )

                    ttk.Label(sub, text=cost, anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=(2, 8),
                        pady=3,
                        row=row,
                        column=1,
                    )

            # if it's not a tuple, it should be a string, which we'd get for an end point
            else:
                row = 0
                column = 0
                self._other.columnconfigure((0, 1, 2), weight=1)

                for node in other:
                    sub = ttk.Frame(self._other, borderwidth=2)
                    sub.grid(sticky=tk.NSEW, row=row, column=column)
                    sub.columnconfigure(0, weight=1)

                    ttk.Label(sub, text=self._canvas_frame.get_label_from_node(node), anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=8,
                        pady=3,
                    )

                    column += 1
                    if column > 2:
                        row += 1
                        column = 0


class AStarShortestPathFrame(TraceFrame):
    def __init__(self, master, canvas_frame, from_node, to_node):
        title = f"A* Shortest Path from {from_node} to {to_node}"

        super().__init__(master, canvas_frame, title, from_node, to_node)
        self._iterator = iter(StateModel().a_star(self._from, self._to))
        self.initial_setup(
            lambda master: CustomScrollableFrame(master, "Current Data"),
            lambda master: CustomScrollableFrame(master, "Current Queue"),
        )

    
    def display_processed(self, processed):
        """
        Called to display the processing data of an in-process A* path-finding algorithm. This will consist of the
        f-scores, g-scores and previous nodes for each processed node.

        Args:
            processed (tuple): Comprised as described above - f-scores, g-scores and previous nodes.
        """
        for child in self._processed.winfo_children():
            child.grid_remove()

        if len(processed) == 0:
            self._processed.columnconfigure(0, weight=1)

            sub = ttk.Frame(self._processed, borderwidth=2)
            sub.grid(sticky=tk.NSEW)
            sub.columnconfigure(0, weight=1)

            ttk.Label(sub, text="Empty", anchor=tk.CENTER, bootstyle="inverse-info").grid(
                sticky=tk.NSEW,
                padx=8,
                pady=3,
            )

        else:
            self._processed.columnconfigure(0, weight=1)

            f_scores, g_scores, came_from = processed
            for row, node in enumerate(sorted(came_from.keys(), key=lambda node: self._canvas_frame.get_label_from_node(node))):
                self._canvas_frame.highlight_processed_node(node)

                sub = ttk.Frame(self._processed, borderwidth=2)
                sub.grid(sticky=tk.NSEW)
                sub.columnconfigure((0, 1, 2, 3), weight=1)

                ttk.Label(sub, text=self._canvas_frame.get_label_from_node(node), anchor=tk.CENTER, bootstyle="inverse-info").grid(
                    sticky=tk.NSEW,
                    padx=(8, 2),
                    pady=3,
                    row=row,
                    column=0,
                )

                ttk.Label(sub, text=f_scores[node] if node in f_scores else "-", anchor=tk.CENTER, bootstyle="inverse-info").grid(
                    sticky=tk.NSEW,
                    padx=(2, 2),
                    pady=3,
                    row=row,
                    column=1,
                )

                ttk.Label(sub, text=g_scores[node] if node in g_scores else "-", anchor=tk.CENTER, bootstyle="inverse-info").grid(
                    sticky=tk.NSEW,
                    padx=(2, 8),
                    pady=3,
                    row=row,
                    column=2,
                )

                ttk.Label(sub, text=self._canvas_frame.get_label_from_node(came_from[node]), anchor=tk.CENTER, bootstyle="inverse-info").grid(
                    sticky=tk.NSEW,
                    padx=(2, 8),
                    pady=3,
                    row=row,
                    column=3,
                )

    
    def display_other(self, other):
        for child in self._other.winfo_children():
            child.grid_remove()

        if len(other) == 0:
            self._other.columnconfigure(0, weight=1)

            sub = ttk.Frame(self._other, borderwidth=2)
            sub.grid(sticky=tk.NSEW)
            sub.columnconfigure(0, weight=1)

            ttk.Label(sub, text="Empty", anchor=tk.CENTER, bootstyle="inverse-info").grid(
                sticky=tk.NSEW,
                padx=8,
                pady=3,
            )

        else:
            self._other.columnconfigure(0, weight=1)

            # incoming tuples mean algorithm is still on-going
            if type(other[0]) is tuple:
                for row, (cost, node) in enumerate(sorted(other)):
                    self._canvas_frame.highlight_pending_node(node)
                    sub = ttk.Frame(self._other, borderwidth=2)
                    sub.grid(sticky=tk.NSEW, row=row)
                    sub.columnconfigure((0, 1), weight=1)

                    ttk.Label(sub, text=self._canvas_frame.get_label_from_node(node), anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=(8, 2),
                        pady=3,
                        row=row,
                        column=0,
                    )

                    ttk.Label(sub, text=cost, anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=(2, 8),
                        pady=3,
                        row=row,
                        column=1,
                    )

            # if it's not a tuple, it should be a string, which we'd get for an end point
            else:
                row = 0
                column = 0
                self._other.columnconfigure((0, 1, 2), weight=1)

                for node in other:
                    sub = ttk.Frame(self._other, borderwidth=2)
                    sub.grid(sticky=tk.NSEW, row=row, column=column)
                    sub.columnconfigure(0, weight=1)

                    ttk.Label(sub, text=self._canvas_frame.get_label_from_node(node), anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=8,
                        pady=3,
                    )

                    column += 1
                    if column > 2:
                        row += 1
                        column = 0
