# import tkinter as tk
# from tkinter import ttk
import customtkinter as ctk

# from pickle import dump, load, HIGHEST_PROTOCOL
from json import dump, load
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

        ###
        # upper frame just has the new / load / save buttons
        #
        upper = ctk.CTkFrame(self)
        ctk.CTkButton(
            upper,
            text="New",
            border_width=2,
            border_color="",
            command=self.__create_new,
        ).grid(
            row=0,
            column=0,
            sticky=ctk.NSEW,
        )
        ctk.CTkButton(
            upper,
            text="Load",
            border_width=2,
            border_color="",
            command=self.__load_file,
        ).grid(
            row=1,
            column=0,
            sticky=ctk.NSEW,
        )
        ctk.CTkButton(
            upper,
            text="Save",
            border_width=2,
            border_color="",
            command=self.__save_file,
        ).grid(
            row=2,
            column=0,
            sticky=ctk.NSEW,
        )
        upper.grid(sticky=ctk.NSEW)

        upper.columnconfigure(0, weight=1)
        upper.rowconfigure((0, 1, 2), weight=1)

        ###
        # middle frame has an empty label for spacing
        #

        middle = ctk.CTkFrame(self)
        ctk.CTkLabel(middle, text=" ").grid(sticky=ctk.NSEW)
        middle.grid(sticky=ctk.NSEW)

        middle.columnconfigure(0, weight=1)
        middle.rowconfigure(0, weight=1)

        ###
        # lower frame has the actual drawing controls
        #

        lower = ctk.CTkFrame(self)
        ctk.CTkLabel(lower, text="Mode:", anchor=ctk.E).grid(
            row=0,
            column=0,
            sticky=ctk.NSEW,
            padx=(0, 3),
        )
        ctk.CTkSwitch(
            lower,
            text=None,
            variable=self.__operation,
            onvalue="Nodes",
            offvalue="Edges",
            command=self.__toggle_mode_switch,
        ).grid(row=0, column=1, sticky=ctk.NSEW)
        ctk.CTkEntry(
            lower,
            textvariable=self.__operation,
            fg_color="lightgreen",
            justify=ctk.CENTER,
            state=ctk.DISABLED,
        ).grid(row=0, column=2, sticky=ctk.NSEW)
        ctk.CTkLabel(lower, text="Directed:", anchor=ctk.E).grid(
            row=1,
            column=0,
            sticky=ctk.NSEW,
            padx=(0, 3),
        )
        self.__directed_check = ctk.CTkCheckBox(
            lower,
            text=None,
            variable=self.__directed,
            command=self.__update_operation_parameters,
            state=ctk.DISABLED,
        )
        self.__directed_check.grid(row=1, column=1, columnspan=2, sticky=ctk.NSEW)
        ctk.CTkLabel(lower, text="Weight:", anchor=ctk.E).grid(
            row=2,
            column=0,
            sticky=ctk.NSEW,
            padx=(0, 3),
        )
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

        ###
        # footer frame has an empty label for spacing, and to absorb the space
        #

        footer = ctk.CTkFrame(self)
        ctk.CTkLabel(footer, text=" ").grid(sticky=ctk.NSEW)
        footer.grid(sticky=ctk.NSEW)

        footer.columnconfigure(0, weight=1)
        footer.rowconfigure(0, weight=1)

        ###
        # don't want any of the heights to change, just the widths of the frames, which can then decide which other
        # controls can be resized, accordingly
        #

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

    def __save_file(self):
        file_contents = {
            "canvas": self.__canvas_frame.get_canvas_as_dict(),
            "graph": StateModel().get_graph_matrix(),
        }

        filename = ctk.filedialog.asksaveasfilename(
            parent=self,
            title="Save Graph",
            defaultextension=".nd",
            filetypes=[("Node Demonstrator", ".nd")],
            confirmoverwrite=True,
        )
        if filename is not None:
            with open(filename, "w") as file:
                dump(file_contents, file)  # , protocol=HIGHEST_PROTOCOL)

    def __load_file(self):
        filename = ctk.filedialog.askopenfilename(
            parent=self,
            title="Load Graph",
            defaultextension=".nd",
            filetypes=[("Node Demonstrator", ".nd")],
        )
        if filename is not None:
            with open(filename, "r") as file:
                file_contents = load(file)
                self.__canvas_frame.set_canvas_from_dict(file_contents["canvas"])
                StateModel().set_graph_matrix(file_contents["graph"])
