# import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from state_model import StateModel


class DrawControlsFrame(ctk.CTkFrame):
    """
    Class to control overall control of what is happening - provides load, save, etc as well as toggles for whether
    acting on nodes or edges.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.__operation = ctk.StringVar(value="Nodes")

        glf = ttk.LabelFrame(self, text="Graph")
        ctk.CTkButton(glf, text="New", command=lambda: StateModel().create_new()).grid(
            sticky=ctk.NSEW
        )
        ctk.CTkButton(
            glf, text="Load", command=lambda: StateModel().load_existing()
        ).grid(sticky=ctk.NSEW)
        ctk.CTkButton(
            glf, text="Save", command=lambda: StateModel().save_current()
        ).grid(sticky=ctk.NSEW)
        glf.grid(sticky=ctk.NSEW)
        glf.columnconfigure(0, weight=1)
        for i in range(3):
            glf.rowconfigure(i, weight=1)

        nlf = ttk.LabelFrame(self)  # , text="Work On")
        ctk.CTkRadioButton(
            nlf,
            text="Nodes",
            variable=self.__operation,
            value="Nodes",
            # indicatoron=ctk.OFF,
            command=self.update_operation,
        ).grid(sticky=ctk.NSEW)
        ctk.CTkRadioButton(
            nlf,
            text="Edges",
            variable=self.__operation,
            value="Edges",
            # indicatoron=ctk.OFF,
            command=self.update_operation,
        ).grid(sticky=ctk.NSEW)
        nlf.grid(sticky=ctk.NSEW)
        nlf.columnconfigure(0, weight=1)
        for i in range(2):
            nlf.rowconfigure(i, weight=1)

        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=2)
        self.columnconfigure(0, weight=1)

    def update_operation(self):
        StateModel().set_operation(self.__operation.get())
