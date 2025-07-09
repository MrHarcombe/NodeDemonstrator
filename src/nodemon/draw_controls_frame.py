import ttkbootstrap as ttk
import ttkbootstrap.constants as tk
import ttkbootstrap.dialogs as dialogs
import tkinter.filedialog as filedialogs

# from pickle import dump, load, HIGHEST_PROTOCOL
from json import dump, load
from os.path import basename, dirname

from .state_model import StateModel


class DrawControlsFrame(ttk.Frame):
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
        self.__operation = ttk.StringVar(value="Nodes")
        self.__directed = ttk.BooleanVar(value=False)
        self.__weight = ttk.StringVar(value=("1" if StateModel().is_weighted() else "None"))

        ###
        # upper frame just has the new / load / save buttons
        #
        upper = ttk.Frame(self)
        ttk.Button(upper, text="New", command=self.__create_new).grid(row=0, column=0, sticky=tk.NSEW, pady=(0, 3))
        ttk.Button(upper, text="Load", command=self.__load_file).grid(row=1, column=0, sticky=tk.NSEW, pady=(0, 3))
        ttk.Button(upper, text="Save", command=self.__save_file).grid(row=2, column=0, sticky=tk.NSEW, pady=(0, 3))

        upper.grid(sticky=tk.NSEW, pady=(0, 15))
        upper.columnconfigure(0, weight=1)
        upper.rowconfigure((0, 1, 2), weight=1)

        ###
        # lower frame has the actual drawing controls
        #

        lower = ttk.Frame(self)
        ttk.Label(lower, text="Mode:", anchor=tk.E).grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 3))
        # ttk.Checkbutton(lower, text=None, variable=self.__operation, onvalue="Nodes", offvalue="Edges", command=self.__toggle_mode_switch).grid(row=0, column=1, sticky=tk.NSEW)
        # ttk.Entry(lower, textvariable=self.__operation, justify=tk.CENTER, state=tk.DISABLED).grid(row=0, column=2, sticky=tk.NSEW)
        ttk.Radiobutton(lower, text="Nodes", variable=self.__operation, value="Nodes", bootstyle="toolbutton", command=self.__toggle_mode_switch).grid(row=0, column=1, sticky=tk.NSEW)
        ttk.Radiobutton(lower, text="Edges", variable=self.__operation, value="Edges", bootstyle="toolbutton", command=self.__toggle_mode_switch).grid(row=0, column=2, sticky=tk.NSEW)
        ttk.Label(lower, text="Directed:", anchor=tk.E).grid(row=1, column=0, sticky=tk.NSEW, padx=(0, 3))
        self.__directed_check = ttk.Checkbutton(lower, text=None, variable=self.__directed, command=self.__update_operation_parameters, state=tk.DISABLED)
        self.__directed_check.grid(row=1, column=1, columnspan=2, sticky=tk.NSEW)
        ttk.Label(lower, text="Weight:", anchor=tk.E).grid(row=2, column=0, sticky=tk.NSEW, padx=(0, 3))
        validation_callback = self.register(self.__validation_wrapper)
        self.__weight_entry = ttk.Entry(lower, textvariable=self.__weight, state=tk.DISABLED, validate="key", validatecommand=(validation_callback, "%P"))
        self.__weight_entry.grid(row=2, column=1, columnspan=2, sticky=tk.NSEW)

        lower.grid(sticky=tk.NSEW, pady=(0, 50))
        lower.rowconfigure((0, 1, 2), weight=1)
        lower.columnconfigure((0, 1, 2), weight=1)

        ###
        # don't want any of the heights to change, just the widths of the frames, which can then decide which other
        # controls can be resized, accordingly
        #

        self.columnconfigure(0, weight=1)

    def __toggle_mode_switch(self):
        if self.__operation.get() == "Nodes":
            self.__directed_check.configure(state=tk.DISABLED)
            self.__weight_entry.configure(state=tk.DISABLED)
        else:
            self.__directed_check.configure(state=tk.NORMAL)
            if StateModel().is_weighted():
                self.__weight_entry.configure(state=tk.NORMAL)

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
            if (dialogs.Messagebox.yesno(message="Graph has changes. Do you wish to save, before starting over?") == "Yes"):
                if not self.__save_file():
                    return False

        weighted = dialogs.Messagebox.yesno(message="Will the graph be weighted?") == "Yes"
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

            filename = filedialogs.asksaveasfilename(
                parent=self,
                title="Save Graph",
                defaultextension=".nd",
                initialdir=directory,
                initialfile=filename,
                filetypes=[("Node Demonstrator", ".nd")],
                confirmoverwrite=True,
            )

        else:
            filename = filedialogs.asksaveasfilename(
                parent=self,
                title="Save Graph",
                defaultextension=".nd",
                filetypes=[("Node Demonstrator", ".nd")],
                confirmoverwrite=True,
            )

        if filename is not None and len(filename) > 0:
            with open(filename, "w") as file:
                dump(file_contents, file)  # , protocol=HIGHEST_PROTOCOL)
            StateModel().set_changed(False)
            return True

        return False

    def __load_file(self):
        if StateModel().is_changed():
            if (dialogs.Messagebox.yesno(message="Graph has changes. Do you wish to save, before starting over?") == "Yes"):
                if not self.__save_file():
                    return False

        filename = filedialogs.askopenfilename(
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
