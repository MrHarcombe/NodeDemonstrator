import customtkinter as ctk
import tkinter.messagebox as messagebox

# from pickle import dump, load, HIGHEST_PROTOCOL
from json import dump, load
from os.path import basename, dirname
from state_model import StateModel


class DrawControlsFrame(ctk.CTkFrame):
    """
    Class to control overall control of what is happening - provides load, save, etc as well as toggles for whether
    acting on nodes or edges.
    """

    def __init__(self, parent, canvas_frame):
        super().__init__(parent)

        self.bind(
            "<Expose>",
            lambda event: StateModel().set_current_tab(self.__class__.__name__),
        )

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
            command=self.__create_new,
        ).grid(row=0, column=0, sticky=ctk.NSEW, pady=(0, 3))
        ctk.CTkButton(
            upper,
            text="Load",
            command=self.__load_file,
        ).grid(
            row=1,
            column=0,
            sticky=ctk.NSEW,
            pady=(0, 3),
        )
        ctk.CTkButton(
            upper,
            text="Save",
            command=self.__save_file,
        ).grid(
            row=2,
            column=0,
            sticky=ctk.NSEW,
            pady=(0, 3),
        )
        upper.grid(sticky=ctk.NSEW, pady=(0, 15))

        upper.columnconfigure(0, weight=1)
        upper.rowconfigure((0, 1, 2), weight=1)

        ###
        # lower frame has the actual drawing controls
        #

        lower = ctk.CTkFrame(self, fg_color="transparent", bg_color="transparent")
        ctk.CTkLabel(
            lower,
            text="Mode:",
            anchor=ctk.E,
            bg_color=self.cget("bg_color"),
        ).grid(
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
            bg_color=self.cget("bg_color"),
            command=self.__toggle_mode_switch,
        ).grid(row=0, column=1, sticky=ctk.NSEW)
        ctk.CTkEntry(
            lower,
            textvariable=self.__operation,
            fg_color="lightgreen",
            bg_color=self.cget("bg_color"),
            justify=ctk.CENTER,
            state=ctk.DISABLED,
        ).grid(row=0, column=2, sticky=ctk.NSEW)
        ctk.CTkLabel(
            lower,
            text="Directed:",
            anchor=ctk.E,
            bg_color=self.cget("bg_color"),
        ).grid(
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
            bg_color=self.cget("bg_color"),
        )
        self.__directed_check.grid(row=1, column=1, columnspan=2, sticky=ctk.NSEW)
        ctk.CTkLabel(
            lower,
            text="Weight:",
            anchor=ctk.E,
            bg_color=self.cget("bg_color"),
        ).grid(
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
            bg_color=self.cget("bg_color"),
            validate="key",
            validatecommand=(validation_callback, "%P"),
        )
        self.__weight_entry.grid(row=2, column=1, columnspan=2, sticky=ctk.NSEW)
        lower.grid(sticky=ctk.NSEW, pady=(0, 50))

        lower.rowconfigure((0, 1, 2), weight=1)
        lower.columnconfigure((0, 1, 2), weight=1)

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
        if StateModel().is_changed():
            if (
                messagebox.askyesno(
                    message="Graph has changes. Do you wish to save, before starting over?"
                )
                == ctk.YES
            ):
                self.__save_file()

        weighted = messagebox.askyesno(message="Will the graph be weighted?") == ctk.YES
        StateModel().create_new(weighted)
        self.__canvas_frame.empty()
        self.__operation.set("Nodes")
        self.__directed.set(False)
        self.__weight.set("1" if weighted else "None")

    def __save_file(self):
        file_contents = {
            "canvas": self.__canvas_frame.get_canvas_as_dict(),
            "graph": StateModel().get_graph_matrix(),
            "weighted": StateModel().is_weighted(),
        }

        current_filename = StateModel().get_filename()
        if current_filename is not None and len(current_filename) > 0:
            filename = basename(current_filename)
            directory = dirname(current_filename)

            filename = ctk.filedialog.asksaveasfilename(
                parent=self,
                title="Save Graph",
                defaultextension=".nd",
                initialdir=directory,
                initialfile=filename,
                filetypes=[("Node Demonstrator", ".nd")],
                confirmoverwrite=True,
            )

        else:
            filename = ctk.filedialog.asksaveasfilename(
                parent=self,
                title="Save Graph",
                defaultextension=".nd",
                filetypes=[("Node Demonstrator", ".nd")],
                confirmoverwrite=True,
            )

        if filename is not None and len(filename) > 0:
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
            StateModel().set_filename(filename)
            with open(filename, "r") as file:
                file_contents = load(file)
                self.__canvas_frame.set_canvas_from_dict(file_contents["canvas"])
                StateModel().set_graph_matrix(
                    file_contents["graph"],
                    file_contents["weighted"],
                )
        self.__weight.set("1" if StateModel().is_weighted() else "None")
        self.__toggle_mode_switch()
