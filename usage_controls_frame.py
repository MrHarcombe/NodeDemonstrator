import customtkinter as ctk

from traversal_frames import BreadthFirstFrame, DepthFirstFrame


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
            # columnspan=2,
            sticky=ctk.NSEW,
            pady=(0, 15),
        )

        nodes = ctk.CTkFrame(self, fg_color="transparent", bg_color="transparent")
        nodes.grid(sticky=ctk.NSEW)
        nodes.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            nodes,
            text="From:",
            anchor=ctk.E,
            bg_color=self.cget("bg_color"),
        ).grid(
            row=2,
            column=0,
            padx=(0, 3),
        )
        ctk.CTkEntry(
            nodes,
            textvariable=self.__from,
            bg_color=self.cget("bg_color"),
        ).grid(
            row=2,
            column=1,
            sticky=ctk.NSEW,
        )

        ctk.CTkLabel(
            nodes,
            text="To:",
            anchor=ctk.E,
            bg_color=self.cget("bg_color"),
        ).grid(
            row=3,
            column=0,
            padx=(0, 3),
        )
        ctk.CTkEntry(
            nodes,
            textvariable=self.__to,
            bg_color=self.cget("bg_color"),
        ).grid(
            row=3,
            column=1,
            sticky=ctk.NSEW,
            pady=(0, 15),
        )

        ctk.CTkButton(
            self,
            text="Start",
            bg_color=self.cget("bg_color"),
            command=self.__trace_step,
        ).grid(sticky=ctk.NSEW, pady=(0, 3))
        ctk.CTkSlider(
            self,
            from_=1,
            to=5,
            number_of_steps=4,
            bg_color=self.cget("bg_color"),
            variable=self.__speed,
        ).grid(sticky=ctk.NSEW, pady=(0, 15))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

    def __trace_step(self):
        match self.__algochoice.get():
            case "Breadth First":
                self.__trace_frame = BreadthFirstFrame(
                    self, self.__canvas_frame, self.__from.get(), self.__to.get()
                )
            case "Depth First":
                self.__trace_frame = DepthFirstFrame(
                    self, self.__canvas_frame, self.__from.get(), self.__to.get()
                )

        self.__trace_frame.grid(
            sticky=ctk.NSEW,
            # columnspan=2,
        )
