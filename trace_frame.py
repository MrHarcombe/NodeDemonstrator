import customtkinter as ctk

from abc import ABCMeta, abstractmethod


class TraceFrame(ctk.CTkScrollableFrame, metaclass=ABCMeta):
    def __init__(self, master, canvas_frame, title):
        super().__init__(master, label_text=title, label_anchor=ctk.CENTER)
        self._canvas_frame = canvas_frame
        self._iterator = None

    def step(self):
        try:
            current, processed, other = next(self._iterator)
            self.display_current(current)
            self.display_processed(processed)
            self.display_other(other)
        except StopIteration:
            print("Algorithm complete")

    @abstractmethod
    def display_current(self, current):
        pass

    @abstractmethod
    def display_processed(self, processed):
        pass

    @abstractmethod
    def display_other(self, other):
        pass
