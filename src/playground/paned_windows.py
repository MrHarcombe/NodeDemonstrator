import ttkbootstrap as ttk
import ttkbootstrap.constants as tk

root = ttk.Window()

pane_bed = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
pane_bed.pack(expand=True, fill=tk.BOTH)

b1 = ttk.Button(pane_bed, text="Button 1", bootstyle=tk.SUCCESS)
# b1.pack(side=tk.LEFT, padx=5, pady=10)
pane_bed.add(b1)

b2 = ttk.Button(pane_bed, text="Button 2", bootstyle=(tk.INFO, tk.OUTLINE))
# b2.pack(side=tk.LEFT, padx=5, pady=10)
pane_bed.add(b2)

root.mainloop()