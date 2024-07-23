import customtkinter as ctk

from abc import ABCMeta, abstractmethod


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
        except StopIteration:
            # print("Algorithm complete")
            self.master.end_trace()

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
