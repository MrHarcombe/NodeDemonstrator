import ttkbootstrap as ttk
import ttkbootstrap.constants as tk


class AmendEdgeDialog(ttk.Toplevel):
    def __init__(self, root, title, from_node, to_node, values):
        super().__init__(root)
        self.title(title)
        self.resizable(False, False)
        self.__response = False

        ttk.Label(
            self,
            text=f"Enter the new weights for edge between '{from_node}' and '{to_node}': ",
        ).grid(row=0, column=0, columnspan=2, sticky=tk.EW)

        if len(values) == 1:
            self.__weight_var = ttk.StringVar(value=values[0])

            ttk.Label(self, text="Edge weight").grid(row=1, column=0, sticky=tk.EW)
            ttk.Entry(self, textvariable=self.__weight_var).grid(row=1, column=1, sticky=tk.NSEW)

        else:
            self.__from_to_var = ttk.StringVar(value=values[0])
            self.__to_from_var = ttk.StringVar(value=values[1])

            ttk.Label(self, text=f"From '{from_node}' to '{to_node}'").grid(row=1, column=0, sticky=tk.EW)
            ttk.Entry(self, textvariable=self.__from_to_var).grid(row=1, column=1, sticky=tk.NSEW)
            ttk.Label(self, text=f"From '{to_node}' to '{from_node}'").grid(row=2, column=0, sticky=tk.EW)
            ttk.Entry(self, textvariable=self.__to_from_var).grid(row=2, column=1, sticky=tk.NSEW)

        ttk.Button(self, text="Cancel", command=self.cancel).grid(row=3, column=0, sticky=tk.EW)
        ttk.Button(self, text="Ok", command=self.okay).grid(row=3, column=1, sticky=tk.EW)

        self.rowconfigure((0, 1), weight=1)
        self.columnconfigure((0, 1), weight=1)

        self.bind("<Return>", self.okay)
        self.bind("<Escape>", self.cancel)

    def get_values(self):
        try:
            weight = None

            try:
                weight = int(self.__weight_var.get())
                if weight < 1:
                    weight = None
            except ValueError:
                pass

            return (weight,)

        # EAFP
        except AttributeError:
            from_to = None
            to_from = None

            try:
                from_to = int(self.__from_to_var.get())
                if from_to < 1:
                    from_to = None
            except ValueError:
                pass

            try:
                to_from = int(self.__to_from_var.get())
                if to_from < 1:
                    to_from = None
            except ValueError:
                pass

            return (from_to, to_from)

    def okay(self, *args):
        self.__response = True
        self.destroy()

    def cancel(self, *args):
        self.destroy()

    def show(self):
        self.deiconify()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
        return self.__response


def amend_edge_dialog(root, title, from_node, to_node, weight_list):
    dialog = AmendEdgeDialog(root, title, from_node, to_node, weight_list)
    dialog.grab_set()
    response = dialog.show()

    if response:
        return dialog.get_values()


if __name__ == "__main__":
    root = ttk.Window()
    root.withdraw()
    new_weights = amend_edge_dialog(root, "Test Amend Edge Dialog", "A", "B", [1])
    if new_weights is not None:
        print("Chose to amend to:", new_weights)
    new_weights = amend_edge_dialog(root, "Test Amend Edge Dialog", "A", "B", [1, 1])
    if new_weights is not None:
        print("Chose to amend to:", new_weights)
