import tkinter as tk
from math import radians, cos, sin

current_x = None


###
# Rotation script adapted from
# https://wiki.tcl-lang.org/page/Canvas+Rotation
#
def rotate_object(canvas, tagOrId, origin, angle):
    ox, oy = origin
    rangle = radians(angle)

    for id in canvas.find_withtag(tagOrId):  # process each component separately
        new_xy = []

        for x, y in zip(*[iter(canvas.coords(id))] * 2):
            # rotates vector (ox,oy)->(x,y) by angle clockwise
            x -= ox  # shift to origin
            y -= oy
            xx = x * cos(rangle) - y * sin(rangle) + ox  # rotate and shift back
            yy = x * sin(rangle) + y * cos(rangle) + oy
            new_xy += (xx, yy)

        canvas.coords(id, new_xy)


def click(event):
    global current_x
    current_x = event.x


def drag(event):
    global current_x
    diff = event.x - current_x
    rotate_object(canvas, p_id, (400, 400), -diff)
    current_x = event.x


root = tk.Tk()
root.title("Canvas Playground")
root.geometry("1000x720")

canvas = tk.Canvas(root, width=100, height=100, scrollregion=(0, 0, 10000, 10000))
canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

canvas.bind("<Button-1>", click)
canvas.bind("<B1-Motion>", drag)

canvas.create_arc(100, 100, 200, 200, style=tk.ARC, start=170, extent=300, width=2)
canvas.create_text(150, 150, text="Drawn as an arc")

###
# from the answer at
# https://stackoverflow.com/questions/14829621/formula-to-find-points-on-the-circumference-of-a-circle-given-the-center-of-the
#

radius = 50
cx, cy = 450, 450

points = []
for t in range(-100, 200, 4):
    x = radius * cos(radians(t)) + cx
    y = radius * sin(radians(t)) + cy
    points.append((x, y))

p_id = canvas.create_polygon(points, width=2, fill="", outline="black", smooth=True)
# print(canvas.coords(p_id))
canvas.create_text(450, 450, text="Drawn as a polygon")

root.mainloop()
