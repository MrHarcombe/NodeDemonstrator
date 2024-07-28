# Python program to trace variable in tkinter
# from https://www.geeksforgeeks.org/tracing-tkinter-variables-in-python/

import tkinter as tk


root = tk.Tk()

my_var = tk.StringVar(name="VAR")
my_var2 = tk.StringVar(name="VAR2")


# defining the callback function (observer)
def my_callback(var, index, mode):
    print(f"Traced variable {var}, {index}, {mode}")
    if var == "VAR":
        my_var.set(my_var.get().upper())
    elif var == "VAR2":
        my_var2.set(my_var2.get().upper())


# registering the observer
my_var.trace_add("write", my_callback)
my_var2.trace_add("write", my_callback)

tk.Label(root, textvariable=my_var).pack(padx=5, pady=5)
tk.Entry(root, textvariable=my_var).pack(padx=5, pady=5)
tk.Entry(root, textvariable=my_var2).pack(padx=5, pady=5)

root.mainloop()
