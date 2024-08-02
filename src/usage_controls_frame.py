import customtkinter as ctk
from tkinter import messagebox

from state_model import StateModel
from traversal_frames import BreadthFirstFrame, DepthFirstFrame
from optimisation_frames import DijkstraShortestPathFrame, AStarShortestPathFrame


class UsageControlsFrame(ctk.CTkFrame):
    """
    Class for working with the drawn graph - algorithms such as standard traversals like BFS, DFS as well as
    path-finding using Dijkstra or A*, and other algorithms will be triggered (and the results displayed) here.
    """

    UNWEIGHTED_ALGOCHOICES = [
        "Breadth First",
        "Depth First",
    ]

    WEIGHTED_ALGOCHOICES = UNWEIGHTED_ALGOCHOICES + [
        "Dijkstra's Shortest Path",
        "A* Shortest Path",
    ]

    def __init__(self, parent, canvas_frame):
        super().__init__(parent)
        self.bind(
            "<Expose>",
            lambda event: StateModel().set_current_tab(self.__class__.__name__),
        )

        self.__canvas_frame = canvas_frame
        self.__algochoice = ctk.StringVar(
            value=UsageControlsFrame.UNWEIGHTED_ALGOCHOICES[0]
        )
        self.__from = ctk.StringVar(name="FROM_VAR")
        self.__to = ctk.StringVar(name="TO_VAR")
        self.__speed = ctk.IntVar(value=5)
        self.__timer_token = None
        self.__trace_frame = None

        # self.__from.trace_add("write", self.__capitalise_combo)
        # self.__to.trace_add("write", self.__capitalise_combo)

        algo_combo = ctk.CTkComboBox(
            self,
            values=(
                UsageControlsFrame.WEIGHTED_ALGOCHOICES
                if StateModel().is_weighted()
                else UsageControlsFrame.UNWEIGHTED_ALGOCHOICES
            ),
            variable=self.__algochoice,
            state="readonly",
        )
        algo_combo.grid(
            sticky=ctk.NSEW,
            pady=(0, 15),
        )
        algo_combo.bind(
            "<Expose>",
            lambda event: algo_combo.configure(
                values=(
                    UsageControlsFrame.WEIGHTED_ALGOCHOICES
                    if StateModel().is_weighted()
                    else UsageControlsFrame.UNWEIGHTED_ALGOCHOICES
                )
            ),
        )

        nodes_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            bg_color="transparent",
        )
        nodes_frame.grid(sticky=ctk.NSEW)
        nodes_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            nodes_frame,
            text="From:",
            anchor=ctk.E,
            bg_color=self.cget("bg_color"),
        ).grid(
            row=2,
            column=0,
            padx=(0, 3),
        )
        from_combo = ctk.CTkComboBox(
            nodes_frame,
            variable=self.__from,
            values=self.__canvas_frame.get_node_labels(),
            bg_color=self.cget("bg_color"),
        )
        from_combo.grid(row=2, column=1, sticky=ctk.NSEW, pady=(0, 3))
        from_combo.bind(
            "<Expose>",
            lambda event: from_combo.configure(
                values=self.__canvas_frame.get_node_labels()
            ),
        )

        ctk.CTkLabel(
            nodes_frame,
            text="To:",
            anchor=ctk.E,
            bg_color=self.cget("bg_color"),
        ).grid(
            row=3,
            column=0,
            padx=(0, 3),
        )
        to_combo = ctk.CTkComboBox(
            nodes_frame,
            variable=self.__to,
            values=self.__canvas_frame.get_node_labels(),
            bg_color=self.cget("bg_color"),
        )
        to_combo.grid(
            row=3,
            column=1,
            sticky=ctk.NSEW,
        )
        to_combo.bind(
            "<Expose>",
            lambda event: to_combo.configure(
                values=self.__canvas_frame.get_node_labels()
            ),
        )

        self.__step_button = ctk.CTkButton(
            self,
            text="Step Trace",
            bg_color=self.cget("bg_color"),
            command=self.__trace_step,
        )
        self.__step_button.grid(sticky=ctk.NSEW, pady=(15, 3))
        self.__timed_button = ctk.CTkButton(
            self,
            text="Timed Trace",
            bg_color=self.cget("bg_color"),
            command=self.__trace_timed,
        )
        self.__timed_button.grid(sticky=ctk.NSEW, pady=(3, 3))
        self.__timed_speed = ctk.CTkSlider(
            self,
            from_=1,
            to=5,
            number_of_steps=4,
            bg_color=self.cget("bg_color"),
            variable=self.__speed,
        )
        self.__timed_speed.grid(sticky=ctk.NSEW, pady=(3, 15))

        self.columnconfigure(0, weight=1)

    def __create_trace_frame(self):
        graph_nodes = self.__canvas_frame.get_node_labels()
        from_node = self.__from.get().strip()
        to_node = self.__to.get().strip()

        from_given = from_node is not None and len(from_node) > 0
        from_good = from_given and from_node in graph_nodes
        to_given = to_node is not None and len(to_node) > 0
        to_good = to_given and to_node in graph_nodes

        if not all((from_good, to_good)):
            message = None

            if from_given and not from_good and to_given and not to_good:
                message = (
                    '"From" and "To" nodes not taken from the graph drawn on screen'
                )

            elif from_given and not from_good:
                message = '"From" node not taken from the graph drawn on screen'

            elif to_given and not to_good:
                message = '"To" node not taken from the graph drawn on screen'

            if message is not None:
                messagebox.showerror(
                    title="Unknown Node",
                    message=message,
                )
                return

        match self.__algochoice.get():
            case "Breadth First":
                if from_given:
                    self.__trace_frame = BreadthFirstFrame(
                        self,
                        self.__canvas_frame,
                        from_node,
                        to_node,
                    )
                else:
                    messagebox.showerror(
                        title="Required Node",
                        message=f'At least the "From" node is required to trace breadth first '
                        f'{"search" if to_given else "traversal"}',
                    )

            case "Depth First":
                if from_given:
                    self.__trace_frame = DepthFirstFrame(
                        self,
                        self.__canvas_frame,
                        from_node,
                        to_node,
                    )
                else:
                    messagebox.showerror(
                        title="Required Node",
                        message=f'At least the "From" node is required to trace depth first '
                        f'{"search" if to_given else "traversal"}',
                    )

            case "Dijkstra's Shortest Path":
                if from_given:
                    self.__trace_frame = DijkstraShortestPathFrame(
                        self,
                        self.__canvas_frame,
                        from_node,
                        to_node,
                    )
                else:
                    messagebox.showerror(
                        title="Required Node",
                        message='At least the "From" node is required to trace Dijkstra\'s shortest path',
                    )

            case "A* Shortest Path":
                if from_given and to_given:
                    self.__trace_frame = AStarShortestPathFrame(
                        self,
                        self.__canvas_frame,
                        from_node,
                        to_node,
                    )
                else:
                    messagebox.showerror(
                        title="Required Nodes",
                        message='Both "From" and "To" nodes are required to trace A* shortest path',
                    )

        if self.__trace_frame is not None:
            self.__trace_frame.grid(
                sticky=ctk.NSEW,
                pady=(15, 0),
            )
            self.rowconfigure(5, weight=1)
            return True

        return False

    def __trace_step(self):
        if self.__create_trace_frame():
            self.__step_button.configure(text="Step")
            self.__step_button.configure(command=self.__trace_frame.step)
            self.__timed_button.configure(state=ctk.DISABLED)
            self.__timed_speed.configure(state=ctk.DISABLED)

    def __trace_timed(self):
        def pause_step():
            if self.__timer_token is not None:
                self.__timed_button.after_cancel(self.__timer_token)
                self.__timed_button.configure(text="Resume")
                self.__timed_button.configure(command=resume_step)

        def resume_step():
            interval = self.__speed.get() * 0.5  # half a second per blip
            self.__timer_token = self.__timed_button.after(
                int(interval * 1000), setup_next_step
            )
            self.__timed_button.configure(text="Pause")
            self.__timed_button.configure(command=pause_step)

        def setup_next_step():
            if self.__trace_frame.step():
                interval = self.__speed.get() * 0.5  # half a second per blip
                self.__timer_token = self.__timed_button.after(
                    int(interval * 1000), setup_next_step
                )

        if self.__create_trace_frame():
            self.__step_button.configure(state=ctk.DISABLED)
            self.__timed_button.configure(text="Pause")
            self.__timed_button.configure(command=pause_step)
            interval = self.__speed.get() * 0.5  # half a second per blip
            self.__timed_button.after(int(interval * 1000), setup_next_step)

    def end_trace(self):
        if self.__step_button.cget("text") == "Step":
            self.__step_button.configure(text="Reset")
            self.__step_button.configure(command=self.__reset_trace)
        else:
            self.__timed_button.configure(state=ctk.NORMAL)
            self.__timed_button.configure(text="Reset")
            self.__timed_button.configure(command=self.__reset_trace)

    def __reset_trace(self):
        self.__canvas_frame.unhighlight_all_nodes()
        self.__trace_frame.grid_remove()
        self.__step_button.configure(state=ctk.NORMAL)
        self.__step_button.configure(text="Step Trace")
        self.__step_button.configure(command=self.__trace_step)
        self.__timed_button.configure(state=ctk.NORMAL)
        self.__timed_button.configure(text="Timed Trace")
        self.__timed_button.configure(command=self.__trace_timed)
        self.__timed_speed.configure(state=ctk.NORMAL)

    # def __capitalise_combo(self, variable, index, mode):
    #     if variable == "FROM_VAR":
    #         self.__from.set(self.__from.get().upper())
    #     elif variable == "TO_VAR":
    #         self.__to.set(self.__to.get().upper())
