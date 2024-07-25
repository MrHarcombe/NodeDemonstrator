import customtkinter as ctk

from traversal_frames import BreadthFirstFrame, DepthFirstFrame
from optimisation_frames import DijkstraShortestPathFrame, AStarShortestPathFrame


class UsageControlsFrame(ctk.CTkFrame):
    """
    Class for working with the drawn graph - algorithms such as standard traversals like BFS, DFS as well as
    path-finding using Dijkstra or A*, and other algorithms will be triggered (and the results displayed) here.
    """

    ALGOCHOICES = [
        "Breadth First",
        "Depth First",
        "Dijkstra's Shortest Path",
        "A* Shortest Path",
    ]

    def __init__(self, parent, canvas_frame):
        super().__init__(parent)
        self.__canvas_frame = canvas_frame
        self.__algochoice = ctk.StringVar(value=UsageControlsFrame.ALGOCHOICES[0])
        self.__from = ctk.StringVar()
        self.__to = ctk.StringVar()
        self.__speed = ctk.IntVar()
        self.__trace_frame = None

        ctk.CTkComboBox(
            self,
            values=UsageControlsFrame.ALGOCHOICES,
            variable=self.__algochoice,
            state="readonly",
        ).grid(
            sticky=ctk.NSEW,
            pady=(0, 15),
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

        self.__action_button = ctk.CTkButton(
            self,
            text="Start",
            bg_color=self.cget("bg_color"),
            command=self.__trace_step,
        )
        self.__action_button.grid(sticky=ctk.NSEW, pady=(15, 15))
        # ctk.CTkSlider(
        #     self,
        #     from_=1,
        #     to=5,
        #     number_of_steps=4,
        #     bg_color=self.cget("bg_color"),
        #     variable=self.__speed,
        # ).grid(sticky=ctk.NSEW, pady=(0, 15))

        self.columnconfigure(0, weight=1)

    def end_trace(self):
        self.__action_button.configure(text="Stop")
        self.__action_button.configure(command=self.__reset_trace)

    def __reset_trace(self):
        self.__canvas_frame.unhighlight_all_nodes()
        self.__trace_frame.grid_remove()
        self.__action_button.configure(text="Start")
        self.__action_button.configure(command=self.__trace_step)

    def __trace_step(self):
        match self.__algochoice.get():
            case "Breadth First":
                self.__trace_frame = BreadthFirstFrame(
                    self,
                    self.__canvas_frame,
                    self.__from.get(),
                    self.__to.get(),
                )
            case "Depth First":
                self.__trace_frame = DepthFirstFrame(
                    self,
                    self.__canvas_frame,
                    self.__from.get(),
                    self.__to.get(),
                )
            case "Dijkstra's Shortest Path":
                self.__trace_frame = DijkstraShortestPathFrame(
                    self,
                    self.__canvas_frame,
                    self.__from.get(),
                    self.__to.get(),
                )
            case "A* Shortest Path":
                self.__trace_frame = AStarShortestPathFrame(
                    self,
                    self.__canvas_frame,
                    self.__from.get(),
                    self.__to.get(),
                )

        self.__action_button.configure(text="Step")
        self.__action_button.configure(command=self.__trace_frame.step)

        self.__trace_frame.grid(
            sticky=ctk.NSEW,
            pady=(15, 0),
        )
        self.rowconfigure(3, weight=1)
