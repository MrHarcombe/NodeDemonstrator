import tkinter as tk
from tkinter import ttk

from state_model import StateModel


class DrawControlsFrame(ttk.Frame):
    """
    Class to control overall control of what is happening - provides load,
     save, etc as well as toggles for whether acting on nodes or edges.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.__operation = tk.StringVar(value="Nodes")

        glf = ttk.LabelFrame(self, text="Graph")
        tk.Button(glf, text="New", command=lambda: StateModel().create_new()).grid(
            sticky=tk.NSEW
        )
        tk.Button(glf, text="Load", command=lambda: StateModel().load_existing()).grid(
            sticky=tk.NSEW
        )
        tk.Button(glf, text="Save", command=lambda: StateModel().save_current()).grid(
            sticky=tk.NSEW
        )
        glf.grid(sticky=tk.NSEW)
        glf.columnconfigure(0, weight=1)
        for i in range(3):
            glf.rowconfigure(i, weight=1)

        nlf = ttk.LabelFrame(self, text="Work On")
        tk.Radiobutton(
            nlf,
            text="Nodes",
            indicatoron=tk.OFF,
            variable=self.__operation,
            value="Nodes",
            command=self.update_operation,
        ).grid(sticky=tk.NSEW)
        tk.Radiobutton(
            nlf,
            text="Edges",
            indicatoron=tk.OFF,
            variable=self.__operation,
            value="Edges",
            command=self.update_operation,
        ).grid(sticky=tk.NSEW)
        nlf.grid(sticky=tk.NSEW)
        nlf.columnconfigure(0, weight=1)
        for i in range(2):
            nlf.rowconfigure(i, weight=1)

        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=2)
        self.columnconfigure(0, weight=1)

    def update_operation(self):
        StateModel().set_operation(self.__operation.get())
