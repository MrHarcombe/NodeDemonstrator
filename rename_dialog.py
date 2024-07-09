import tkinter as tk
from tkinter import ttk

###
#
# from https://stackoverflow.com/questions/29619418/how-to-create-a-custom-messagebox-using-tkinter-in-python-with-changing-message
#


class RenameDialog(tk.Toplevel):
    def __init__(self, root, title, text_var):
        super().__init__(root)
        self.title(title)

        ttk.Label(self, text=f"Enter the new value for '{text_var.get()}'").grid(
            row=0, column=0, columnspan=2, sticky=tk.EW
        )
        entry = ttk.Entry(self, textvariable=text_var)
        entry.grid(row=1, column=0, columnspan=2, sticky=tk.EW)
        entry.focus()
        ttk.Button(self, text="Cancel", command=self.cancel).grid(
            row=2, column=0, sticky=tk.EW
        )
        ttk.Button(self, text="Ok", command=self.okay).grid(
            row=2, column=1, sticky=tk.EW
        )
        self.bind("<Return>", self.okay)
        self.bind("<Escape>", self.cancel)

    def okay(self, *args):
        self.__response = True
        self.destroy()

    def cancel(self, *args):
        self.__response = False
        self.destroy()

    def show(self):
        self.deiconify()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
        return self.__response


def rename_dialog(root, title, current_value):
    text = tk.StringVar(value=current_value)
    dialog = RenameDialog(root, title, text)
    response = dialog.show()

    if response:
        return text.get()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    new_name = rename_dialog(root, "Test Rename Dialog", "Value")
    if new_name != None:
        print("Chose to rename to:", new_name)
