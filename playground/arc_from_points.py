import tkinter as tk
import math


class SampleApp(tk.Tk):
    """
    Code taken from the author's own answer at
    https://stackoverflow.com/questions/36958438/draw-an-arc-between-two-points-on-a-tkinter-canvas
    """

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.canvas = tk.Canvas(width=400, height=400)
        self.canvas.pack(fill="both", expand=True)

    def _create_token(self, coord, color):
        """Create a token at the given coordinate in the given color"""
        (x, y) = coord
        self.canvas.create_oval(
            x - 5, y - 5, x + 5, y + 5, outline=color, fill=color, tags="token"
        )

    def create(self, xA, yA, xB, yB, d=10):
        self._create_token((xA, yA), "white")
        self._create_token((xB, yB), "pink")

        t = math.atan2(yB - yA, xB - xA)
        xC = (xA + xB) / 2 + d * math.sin(t)
        yC = (yA + yB) / 2 - d * math.cos(t)
        xD = (xA + xB) / 2 - d * math.sin(t)
        yD = (yA + yB) / 2 + d * math.cos(t)

        self.canvas.create_line(
            (xA, yA), (xC, yC), (xB, yB), arrow=tk.LAST, smooth=True
        )
        self.canvas.create_line(
            (xA, yA), (xD, yD), (xB, yB), arrow=tk.FIRST, smooth=True, fill="red"
        )
        self.canvas.create_line((xA, yA), (xB, yB), fill="blue")


if __name__ == "__main__":
    app = SampleApp()
    app.create(100, 100, 300, 280, 40)
    app.mainloop()
