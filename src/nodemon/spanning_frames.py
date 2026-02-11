import ttkbootstrap as ttk
import ttkbootstrap.constants as tk

from .state_model import StateModel
from .trace_frame import TraceFrame, CustomScrollableFrame


class PrimsSpanningFrame(TraceFrame):
    def __init__(self, master, canvas_frame, from_node):
        if from_node is None or len(from_node.strip()) == 0:
            title = "Prim's Minimum Spanning Tree"
        else:
            title = "Prim's Minimum Spanning Tree from {from_node}"

        super().__init__(master, canvas_frame, title, from_node)
        self._iterator = iter(StateModel().prims_mst(from_node))
        self.initial_setup(
            lambda master: CustomScrollableFrame(master), # Nodes in MST / Shortest External Edge / Parent
            lambda master: ttk.Label(master),
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
            # incoming tuples mean algorithm is still on-going
            if type(processed) is tuple:
                in_mst, key_values, parents = processed

                sub = ttk.Frame(self._processed, borderwidth=2)
                sub.grid(sticky=tk.NSEW, row=0)

                for row, node in enumerate(filter(lambda node: in_mst[node], sorted(in_mst, key=lambda node:self._canvas_frame.get_label_from_node(node)))):
                    if key_values[node] != float("inf"):
                        self._canvas_frame.highlight_pending_node(node)
                    
                    ttk.Label(sub, text=self._canvas_frame.get_label_from_node(node), anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=(8, 2),
                        pady=3,
                        row=row,
                        column=0,
                    )

                    ttk.Label(sub, text=key_values[node], anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=(2, 8),
                        pady=3,
                        row=row,
                        column=1,
                    )


                    ttk.Label(sub, text=parents[node], anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=(2, 8),
                        pady=3,
                        row=row,
                        column=2,
                    )

                sub.columnconfigure((0, 1, 2), weight=1)
                self._processed.columnconfigure(0, weight=1)

            # if it's not a tuple, it should be a list, which we'd get on completion
            else:
                sub = ttk.Frame(self._processed, borderwidth=2)
                sub.grid(sticky=tk.NSEW, row=0, column=0)
                sub.columnconfigure(0, weight=1)

                for row, ((from_node, to_node), weight) in enumerate(processed):
                    self._canvas_frame.highlight_processed_edge(from_node, to_node)
                    
                    ttk.Label(
                        sub,
                        text=f"{self._canvas_frame.get_label_from_node(from_node)} - {self._canvas_frame.get_label_from_node(to_node)}",
                        anchor=tk.CENTER,
                        bootstyle="inverse-info"
                    ).grid(
                        sticky=tk.NSEW,
                        padx=8,
                        pady=3,
                        column=0,
                        row=row,
                    )

                    ttk.Label(sub, text=weight, anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=8,
                        pady=3,
                        column=1,
                        row=row,
                    )

                self._processed.columnconfigure(0, weight=1)
                sub.columnconfigure((0, 1), weight=1)


    def display_other(self, other):
        pass

class KruskalsSpanningFrame(TraceFrame):
    def __init__(self, master, canvas_frame):
        title = f"Kruskal's Minimum Spanning Tree"

        super().__init__(master, canvas_frame, title, None, None)
        self._iterator = iter(StateModel().kruskals_mst())
        self.initial_setup(
            lambda master: CustomScrollableFrame(master), # Parents / Ranks
            lambda master: CustomScrollableFrame(master), # All Edges
        )

    ###
    # overridden here as self._current will not be a simple node
    # it will be a tuple containing a tuple (the edge) and a weight
    #
    def highlight_anchor_points(self):
        if self._from is not None:
            self._canvas_frame.highlight_start_node(self._from)
        if self._to is not None:
            self._canvas_frame.highlight_end_node(self._to)
        if self._current is not None:
            # specialist case
            (from_node, to_node), weight = self._current
            self._canvas_frame.highlight_current_edge(from_node, to_node)

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
            # incoming tuples mean algorithm is still on-going
            if type(processed) is tuple:
                parents, ranks = processed

                sub = ttk.Frame(self._processed, borderwidth=2)
                sub.grid(sticky=tk.NSEW, row=0)

                for row, node in enumerate(sorted(parents, key=lambda node:self._canvas_frame.get_label_from_node(node))):
                    ttk.Label(
                        sub,
                        text=self._canvas_frame.get_label_from_node(node),
                        anchor=tk.CENTER,
                        bootstyle="inverse-info"
                    ).grid(
                        sticky=tk.NSEW,
                        padx=(8, 2),
                        pady=3,
                        row=row,
                        column=0,
                    )

                    ttk.Label(
                        sub,
                        text="-" if parents[node] is None else self._canvas_frame.get_label_from_node(parents[node]),
                        anchor=tk.CENTER,
                        bootstyle="inverse-info"
                    ).grid(
                        sticky=tk.NSEW,
                        padx=(8, 2),
                        pady=3,
                        row=row,
                        column=1,
                    )

                    ttk.Label(sub, text=ranks[node], anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=(2, 8),
                        pady=3,
                        row=row,
                        column=2,
                    )

                sub.columnconfigure((0, 1, 2), weight=1)
                self._processed.columnconfigure(0, weight=1)

            # if it's not a tuple, it should be a list, which we'd get on completion
            else:
                self._canvas_frame.unhighlight_all_edges()
                
                sub = ttk.Frame(self._processed, borderwidth=2)
                sub.grid(sticky=tk.NSEW, row=0, column=0)
                sub.columnconfigure(0, weight=1)

                for row, ((from_node, to_node), weight) in enumerate(processed):
                    self._canvas_frame.highlight_processed_edge(from_node, to_node)
                    
                    ttk.Label(
                        sub,
                        text=f"{self._canvas_frame.get_label_from_node(from_node)} - {self._canvas_frame.get_label_from_node(to_node)}",
                        anchor=tk.CENTER,
                        bootstyle="inverse-info"
                    ).grid(
                        sticky=tk.NSEW,
                        padx=8,
                        pady=3,
                        column=0,
                        row=row,
                    )

                    ttk.Label(sub, text=weight, anchor=tk.CENTER, bootstyle="inverse-info").grid(
                        sticky=tk.NSEW,
                        padx=8,
                        pady=3,
                        column=1,
                        row=row,
                    )

                self._processed.columnconfigure(0, weight=1)
                sub.columnconfigure((0, 1), weight=1)

    
    def display_other(self, other):
        for child in self._other.winfo_children():
            child.grid_remove()

        if other is None:
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

            sub = ttk.Frame(self._other, borderwidth=2)
            sub.grid(sticky=tk.NSEW)
            sub.columnconfigure((0, 1), weight=1)

            # only ever expecting a dictionary of edges and weights
            for row, ((from_node, to_node), weight) in enumerate(sorted(other.items(), key=lambda item: item[1])):
                ttk.Label(
                    sub,
                    text=f"{self._canvas_frame.get_label_from_node(from_node)} - {self._canvas_frame.get_label_from_node(to_node)}",
                    anchor=tk.CENTER,
                    bootstyle="inverse-info"
                ).grid(
                    sticky=tk.NSEW,
                    padx=(8, 2),
                    pady=3,
                    row=row,
                    column=0,
                )

                ttk.Label(sub, text=other[(from_node, to_node)], anchor=tk.CENTER, bootstyle="inverse-info").grid(
                    sticky=tk.NSEW,
                    padx=(2, 8),
                    pady=3,
                    row=row,
                    column=1,
                )
