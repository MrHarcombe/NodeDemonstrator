import customtkinter as ctk

from abc import ABCMeta, abstractmethod


class CustomScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, title):
        super().__init__(master, label_text=title, label_anchor=ctk.CENTER)
        self._scrollbar.configure(height=0)


class TraceFrame(ctk.CTkFrame, metaclass=ABCMeta):
    def __init__(self, master, canvas_frame, title, from_node, to_node):
        super().__init__(master, fg_color="transparent", bg_color="transparent")
        self._canvas_frame = canvas_frame
        self._iterator = None

        self._from = from_node
        self._to = to_node if to_node is not None and len(to_node.strip()) > 0 else None
        self._current = None

        ctk.CTkLabel(
            self, text=title, anchor=ctk.CENTER, fg_color="darkgrey", corner_radius=6
        ).grid(
            sticky=ctk.NSEW,
            pady=(5, 5),
        )

        self.highlight_anchor_points()

    def initial_setup(self, upper_class, lower_class):
        self._processed = upper_class(self)
        self._processed.grid(sticky=ctk.NSEW, pady=(0, 15))
        self._processed.columnconfigure(0, weight=1)

        empty_frame = ctk.CTkFrame(
            self._processed,
            border_width=2,
            border_color="black",
        )
        empty_frame.grid(
            sticky=ctk.NSEW,
        )
        empty_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            empty_frame,
            text="Empty",
            anchor=ctk.CENTER,
        ).grid(
            sticky=ctk.NSEW,
            padx=8,
            pady=3,
        )

        self._other = lower_class(self)
        self._other.grid(sticky=ctk.NSEW)
        self._other.columnconfigure(0, weight=1)

        empty_frame = ctk.CTkFrame(
            self._other,
            border_width=2,
            border_color="black",
        )
        empty_frame.grid(
            sticky=ctk.NSEW,
        )
        empty_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            empty_frame,
            text="Empty",
            anchor=ctk.CENTER,
        ).grid(
            sticky=ctk.NSEW,
            padx=8,
            pady=3,
        )

        self.rowconfigure((1, 2), weight=1)
        self.columnconfigure(0, weight=1)

    def highlight_anchor_points(self):
        self._canvas_frame.highlight_start_node(self._from)
        if self._to is not None:
            self._canvas_frame.highlight_end_node(self._to)
        if self._current is not None:
            self._canvas_frame.highlight_current_node(self._current)

    def step(self):
        try:
            self._current, processed, other = next(self._iterator)
            self.display_processed(processed)
            self.display_other(other)
            self.highlight_anchor_points()
            return True
        except StopIteration:
            self.master.end_trace()
            return False

    def display_current(self):
        """
        Opportunity to do something more when displaying the current node - by default the node will be
        highlighted as the last thing done, after highlighting the processed and other nodes, so it isn't
        consumed as part of the mass highlighting.
        """
        pass

    @abstractmethod
    def display_processed(self, processed):
        pass

    @abstractmethod
    def display_other(self, other):
        pass
