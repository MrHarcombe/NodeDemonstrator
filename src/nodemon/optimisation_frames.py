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
            lambda master: CustomScrollableFrame(
                master
            ),  # Processed Node / Cost from Start / Previous
            lambda master: CustomScrollableFrame(master),  # Queued Node / Step Cost
        )

    def display_processed(self):
        for child in self._processed.winfo_children():
            child.grid_remove()

        if len(self._processed_value) == 0:
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

            for row, node in enumerate(
                sorted(
                    self._processed_value,
                    key=lambda node: self._canvas_frame.get_label_from_node(node),
                )
            ):
                cost, previous = self._processed_value[node]
                self._canvas_frame.highlight_processed_node(node)

                sub = ttk.Frame(self._processed, borderwidth=2)
                sub.grid(sticky=tk.NSEW)
                sub.columnconfigure((0, 1, 2), weight=1)

                ttk.Label(
                    sub,
                    text=self._canvas_frame.get_label_from_node(node),
                    anchor=tk.CENTER,
                    bootstyle="inverse-info",
                ).grid(
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

                ttk.Label(
                    sub,
                    text=(
                        self._canvas_frame.get_label_from_node(previous)
                        if previous is not None
                        else "-"
                    ),
                    anchor=tk.CENTER,
                    bootstyle="inverse-info",
                ).grid(
                    sticky=tk.NSEW,
                    padx=(2, 8),
                    pady=3,
                    row=row,
                    column=2,
                )

    def display_other(self):
        for child in self._other.winfo_children():
            child.grid_remove()

        if len(self._other_value) == 0:
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
            if type(self._other_value[0]) is tuple:
                for row, (cost, node) in enumerate(sorted(self._other_value)):
                    self._canvas_frame.highlight_pending_node(node)
                    sub = ttk.Frame(self._other, borderwidth=2)
                    sub.grid(sticky=tk.NSEW, row=row)
                    sub.columnconfigure((0, 1), weight=1)

                    ttk.Label(
                        sub,
                        text=self._canvas_frame.get_label_from_node(node),
                        anchor=tk.CENTER,
                        bootstyle="inverse-info",
                    ).grid(
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

                for node in self._other_value:
                    sub = ttk.Frame(self._other, borderwidth=2)
                    sub.grid(sticky=tk.NSEW, row=row, column=column)
                    sub.columnconfigure(0, weight=1)

                    ttk.Label(
                        sub,
                        text=self._canvas_frame.get_label_from_node(node),
                        anchor=tk.CENTER,
                        bootstyle="inverse-info",
                    ).grid(
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
        self._iterator = iter(
            StateModel().a_star(self._from, self._to, self.manhattan_distance)
        )
        self.initial_setup(
            lambda master: CustomScrollableFrame(
                master
            ),  # Processed Node / F-Score / G-Score / Previous
            lambda master: CustomScrollableFrame(master),  # Queued Node / Estimated Total Cost
        )

    def manhattan_distance(self, node_from, node_to):
        return sum(
            (
                abs(val1 - val2)
                for val1, val2 in zip(
                    self._canvas_frame.get_node_coordinates(self._from),
                    self._canvas_frame.get_node_coordinates(self._to),
                )
            )
        )

    def display_processed(self):
        """
        Called to display the processing data of an in-process A* path-finding algorithm. This will consist of the
        f-scores, g-scores and previous nodes for each processed node.

        Args:
            processed (tuple): Comprised as described above - f-scores, g-scores and previous nodes.
        """
        for child in self._processed.winfo_children():
            child.grid_remove()

        if len(self._processed_value) == 0:
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

            f_scores, g_scores, came_from = self._processed_value
            for row, node in enumerate(
                sorted(
                    came_from.keys(),
                    key=lambda node: self._canvas_frame.get_label_from_node(node),
                )
            ):
                self._canvas_frame.highlight_processed_node(node)

                sub = ttk.Frame(self._processed, borderwidth=2)
                sub.grid(sticky=tk.NSEW)
                sub.columnconfigure((0, 1, 2, 3), weight=1)

                ttk.Label(
                    sub,
                    text=self._canvas_frame.get_label_from_node(node),
                    anchor=tk.CENTER,
                    bootstyle="inverse-info",
                ).grid(
                    sticky=tk.NSEW,
                    padx=(8, 2),
                    pady=3,
                    row=row,
                    column=0,
                )

                ttk.Label(
                    sub,
                    text=f_scores[node] if node in f_scores else "-",
                    anchor=tk.CENTER,
                    bootstyle="inverse-info",
                ).grid(
                    sticky=tk.NSEW,
                    padx=(2, 2),
                    pady=3,
                    row=row,
                    column=1,
                )

                ttk.Label(
                    sub,
                    text=g_scores[node] if node in g_scores else "-",
                    anchor=tk.CENTER,
                    bootstyle="inverse-info",
                ).grid(
                    sticky=tk.NSEW,
                    padx=(2, 8),
                    pady=3,
                    row=row,
                    column=2,
                )

                ttk.Label(
                    sub,
                    text=self._canvas_frame.get_label_from_node(came_from[node]),
                    anchor=tk.CENTER,
                    bootstyle="inverse-info",
                ).grid(
                    sticky=tk.NSEW,
                    padx=(2, 8),
                    pady=3,
                    row=row,
                    column=3,
                )

    def display_other(self):
        for child in self._other.winfo_children():
            child.grid_remove()

        if len(self._other_value) == 0:
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
            if type(self._other_value[0]) is tuple:
                for row, (cost, node) in enumerate(sorted(self._other_value)):
                    self._canvas_frame.highlight_pending_node(node)
                    sub = ttk.Frame(self._other, borderwidth=2)
                    sub.grid(sticky=tk.NSEW, row=row)
                    sub.columnconfigure((0, 1), weight=1)

                    ttk.Label(
                        sub,
                        text=self._canvas_frame.get_label_from_node(node),
                        anchor=tk.CENTER,
                        bootstyle="inverse-info",
                    ).grid(
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

                for node in self._other_value:
                    sub = ttk.Frame(self._other, borderwidth=2)
                    sub.grid(sticky=tk.NSEW, row=row, column=column)
                    sub.columnconfigure(0, weight=1)

                    ttk.Label(
                        sub,
                        text=self._canvas_frame.get_label_from_node(node),
                        anchor=tk.CENTER,
                        bootstyle="inverse-info",
                    ).grid(
                        sticky=tk.NSEW,
                        padx=8,
                        pady=3,
                    )

                    column += 1
                    if column > 2:
                        row += 1
                        column = 0


class BellmanFordShortestPathFrame(TraceFrame):
    def __init__(self, master, canvas_frame, from_node, to_node):
        if to_node is None or len(to_node.strip()) == 0:
            title = f"Bellman-Ford Shortest Path from {from_node}"
        else:
            title = f"Bellman-Ford Shortest Path from {from_node} to {to_node}"

        super().__init__(master, canvas_frame, title, from_node, to_node)
        self._iterator = iter(StateModel().bellman_ford(self._from, self._to))
        self.initial_setup(
            lambda master: CustomScrollableFrame(master),  # Distances / Predecessors
            lambda master: ttk.Label(master),
        )

    def display_processed(self):
        """
        Called to display the processing data of an in-process Bellman-Ford path-finding
        algorithm. This will consist of the current distances to each node, and predecessors.

        Args:
             (tuple): Comprised as described above - distances and predecessors to each node.
        """
        for child in self._processed.winfo_children():
            child.grid_remove()

        if len(self._processed_value) == 0:
            self._processed.columnconfigure(0, weight=1)

            sub = ttk.Frame(self._processed, borderwidth=2)
            sub.grid(sticky=tk.NSEW)
            sub.columnconfigure(0, weight=1)

            ttk.Label(sub, text="Empty", anchor=tk.CENTER, bootstyle="inverse-info").grid(
                sticky=tk.NSEW,
                padx=8,
                pady=3,
            )

            self._other.config(text="", width=0)

        else:
            self._processed.columnconfigure(0, weight=1)

            if isinstance(self._processed_value, tuple):
                distances, predecessors = self._processed_value
                for row, node in enumerate(
                    sorted(
                        distances.keys(),
                        key=lambda node: self._canvas_frame.get_label_from_node(node),
                    )
                ):
                    self._canvas_frame.highlight_processed_node(node)

                    sub = ttk.Frame(self._processed, borderwidth=2)
                    sub.grid(sticky=tk.NSEW)
                    sub.columnconfigure((0, 1, 2), weight=1)

                    ttk.Label(
                        sub,
                        text=self._canvas_frame.get_label_from_node(node),
                        anchor=tk.CENTER,
                        bootstyle="inverse-info",
                    ).grid(
                        sticky=tk.NSEW,
                        padx=(8, 2),
                        pady=3,
                        row=row,
                        column=0,
                    )

                    ttk.Label(
                        sub,
                        text=distances[node] if node in distances else "-",
                        anchor=tk.CENTER,
                        bootstyle="inverse-info",
                    ).grid(
                        sticky=tk.NSEW,
                        padx=(2, 2),
                        pady=3,
                        row=row,
                        column=1,
                    )

                    ttk.Label(
                        sub,
                        text=predecessors[node] if node in predecessors else "-",
                        anchor=tk.CENTER,
                        bootstyle="inverse-info",
                    ).grid(
                        sticky=tk.NSEW,
                        padx=(2, 8),
                        pady=3,
                        row=row,
                        column=2,
                    )

                if self._other_value is not None:
                    value = f"Step: {self._other_value}"
                    self._other.config(text=value, width=len(value))

            else:
                sub = ttk.Frame(self._processed, borderwidth=2)
                sub.grid(sticky=tk.NSEW)
                sub.columnconfigure((0, 1), weight=1)

                ttk.Label(sub, text="Path", anchor=tk.CENTER, bootstyle="inverse-info").grid(
                    sticky=tk.NSEW,
                    padx=(8, 2),
                    pady=3,
                    row=0,
                    column=0,
                )

                path = ", ".join(
                    self._canvas_frame.get_label_from_node(node)
                    for node in self._processed_value
                )
                ttk.Label(sub, text=path, anchor=tk.CENTER, bootstyle="inverse-info").grid(
                    sticky=tk.NSEW,
                    padx=(2, 2),
                    pady=3,
                    row=0,
                    column=1,
                )

                if self._other_value is not None:
                    if isinstance(self._other_value, int):
                        value = f"Shortest path length: {self._other_value}"
                    elif isinstance(self._other_value, str):
                        value = f"{self._other_value}"
                    self._other.config(text=value, width=len(value))

    def display_other(self):
        pass
