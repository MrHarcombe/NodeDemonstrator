# import tkinter as tk
# from tkinter import ttk
import customtkinter as ctk

from state_model import StateModel


class DrawControlsFrame(ctk.CTkFrame):
    """
    Class to control overall control of what is happening - provides load, save, etc as well as toggles for whether
    acting on nodes or edges.
    """

    def __init__(self, parent, canvas_frame):
        super().__init__(parent)
        self.__canvas_frame = canvas_frame
        self.__operation = ctk.StringVar(value="Nodes")
        self.__directed = ctk.BooleanVar(value=False)
        self.__weight = ctk.StringVar(
            value=("1" if StateModel().is_weighted() else "None")
        )

        upper = ctk.CTkFrame(self)
        ctk.CTkButton(upper, text="New", command=self.__create_new).grid(
            sticky=ctk.NSEW
        )
        ctk.CTkButton(
            upper, text="Load", command=lambda: StateModel().load_existing()
        ).grid(sticky=ctk.NSEW)
        ctk.CTkButton(
            upper, text="Save", command=lambda: StateModel().save_current()
        ).grid(sticky=ctk.NSEW)
        upper.grid(sticky=ctk.NSEW)
        upper.columnconfigure(0, weight=1)
        upper.rowconfigure((0, 1, 2), weight=1)

        lower = ctk.CTkFrame(self)
        label = ctk.CTkLabel(lower, text="Mode:")
        label.configure(justify=ctk.RIGHT)
        label.grid(row=0, column=0, sticky=ctk.NSEW)
        ctk.CTkSwitch(
            lower,
            text=None,
            variable=self.__operation,
            onvalue="Nodes",
            offvalue="Edges",
            command=self.__toggle_mode_switch,
        ).grid(row=0, column=1, sticky=ctk.NSEW)
        label = ctk.CTkEntry(lower, textvariable=self.__operation, state=ctk.DISABLED)
        label.grid(row=0, column=2, sticky=ctk.NSEW)
        label = ctk.CTkLabel(lower, text="Directed:")
        label.configure(justify=ctk.RIGHT)
        label.grid(row=1, column=0, sticky=ctk.NSEW)
        self.__directed_check = ctk.CTkCheckBox(
            lower,
            text=None,
            variable=self.__directed,
            command=self.__update_operation_parameters,
            state=ctk.DISABLED,
        )
        self.__directed_check.grid(row=1, column=1, columnspan=2, sticky=ctk.NSEW)
        label = ctk.CTkLabel(lower, text="Weight:")
        label.configure(justify=ctk.RIGHT)
        label.grid(row=2, column=0, sticky=ctk.NSEW)
        validation_callback = self.register(self.__validation_wrapper)
        self.__weight_entry = ctk.CTkEntry(
            lower,
            textvariable=self.__weight,
            placeholder_text="1",
            state=ctk.DISABLED,
            validate="key",
            validatecommand=(validation_callback, "%P"),
        )
        self.__weight_entry.grid(row=2, column=1, columnspan=2, sticky=ctk.NSEW)
        lower.grid(sticky=ctk.NSEW)
        lower.rowconfigure((0, 1, 2), weight=1)
        lower.columnconfigure((0, 1, 2), weight=1)

        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

    def __toggle_mode_switch(self):
        if self.__operation.get() == "Nodes":
            self.__directed_check.configure(state=ctk.DISABLED)
            self.__weight_entry.configure(state=ctk.DISABLED)
        else:
            self.__directed_check.configure(state=ctk.NORMAL)
            if StateModel().is_weighted():
                self.__weight_entry.configure(state=ctk.NORMAL)

        self.__update_operation_parameters()

    def __validation_wrapper(self, new_value):
        StateModel().set_operation_parameters(
            self.__operation.get(),
            self.__directed.get(),
            new_value,
        )
        return True

    def __update_operation_parameters(self):
        # print(
        #     "Updating operation parameters:",
        #     self.__operation.get(),
        #     self.__directed.get(),
        #     self.__weight.get(),
        # )
        StateModel().set_operation_parameters(
            self.__operation.get(),
            self.__directed.get(),
            self.__weight.get(),
        )

    def __create_new(self):
        StateModel().create_new()
        self.__canvas_frame.empty()
        self.__operation.set("Nodes")
        self.__directed.set(False)
        self.__weight.set("1" if StateModel().is_weighted() else "None")
