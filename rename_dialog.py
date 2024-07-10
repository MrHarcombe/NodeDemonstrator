# import tkinter as tk
# from tkinter import ttk
import customtkinter as ctk

###
#
# from the answers at
# https://stackoverflow.com/questions/29619418/how-to-create-a-custom-messagebox-using-tkinter-in-python-with-changing-message
#


class RenameDialog(ctk.CTkToplevel):
    def __init__(self, root, title, text_var):
        super().__init__(root)
        self.title(title)

        ctk.CTkLabel(self, text=f"Enter the new value for '{text_var.get()}'").grid(
            row=0, column=0, columnspan=2, sticky=ctk.EW
        )
        entry = ctk.CTkEntry(self, textvariable=text_var)
        entry.grid(row=1, column=0, columnspan=2, sticky=ctk.EW)
        entry.focus()
        ctk.CTkButton(self, text="Cancel", command=self.cancel).grid(
            row=2, column=0, sticky=ctk.EW
        )
        ctk.CTkButton(self, text="Ok", command=self.okay).grid(
            row=2, column=1, sticky=ctk.EW
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
    text = ctk.StringVar(value=current_value)
    dialog = RenameDialog(root, title, text)
    response = dialog.show()

    if response:
        return text.get()


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    new_name = rename_dialog(root, "Test Rename Dialog", "Value")
    if new_name is not None:
        print("Chose to rename to:", new_name)
