import tkinter as tk
from math import sqrt, pi, sin, cos

# def from_x_solutions(x1, y1, x2, y2, radius):
#     def a(x1, y1, x2, y2):
#         return 1 + (y2 - y1) ** 2 / (x2 - x1) ** 2

#     def b(x1, y1, x2, y2):
#         return 2 * (y2 - y1) * (x1 * y1 - x1 * y2) / (x2 - x1) ** 2 - 2 * x1

#     def c(x1, y1, x2, y2, radius):
#         return x1**2 + (x1 * y1 - x1 * y2) ** 2 / (x2 - x1) ** 2 - radius**2

#     a_ans = a(x1, y1, x2, y2)
#     b_ans = b(x1, y1, x2, y2)
#     c_ans = c(x1, y1, x2, y2, radius)

#     return (
#         (-b_ans + (b_ans**2 - 4 * a_ans * c_ans) ** 0.5 / 2 * a_ans),
#         (-b_ans - (b_ans**2 - 4 * a_ans * c_ans) ** 0.5 / 2 * a_ans),
#     )


# def from_y_solution(x, x1, y1, x2, y2):
#     return ((y2 - y1) / (x2 - x1)) * (x - x1) + y1


# def x_solutions(x1, y1, x2, y2, radius):
#     def a(x1, y1, x2, y2):
#         return 1 + (y2 - y1) ** 2 / (x2 - x1) ** 2

#     def b(x1, y1, x2, y2):
#         return 2 * (y2 - y1) * (x2 * y1 - x2 * y2) / (x2 - x1) ** 2 - 2 * x2

#     def c(x1, y1, x2, y2, radius):
#         return x2**2 + (x2 * y1 - x2 * y2) ** 2 / (x2 - x1) ** 2 - radius**2

#     a_ans = a(x1, y1, x2, y2)
#     b_ans = b(x1, y1, x2, y2)
#     c_ans = c(x1, y1, x2, y2, radius)

#     return (
#         (-b_ans + (b_ans**2 - 4 * a_ans * c_ans) ** 0.5 / 2 * a_ans),
#         (-b_ans - (b_ans**2 - 4 * a_ans * c_ans) ** 0.5 / 2 * a_ans),
#     )


def x_solutions(x1, y1, x2, y2, radius):
    def a(x1, y1, x2, y2):
        return 1 + y1**2 - 2 * y1 * y2**2

    def b(x1, y1, x2, y2):
        return 2 * x1 * y1 * y2 - 2 * x1 * y2**2 - x2 * y1**2 - 2 * x1

    def c(x1, y1, x2, y2, radius):
        return x1**2 + x2**2 * y1**2 + x1 * x2 * y1 * y2 - radius**2

    a_ans = a(x1, y1, x2, y2)
    b_ans = b(x1, y1, x2, y2)
    c_ans = c(x1, y1, x2, y2, radius)

    return (
        (-b_ans + (b_ans**2 - 4 * a_ans * c_ans) ** 0.5 / 2 * a_ans),
        (-b_ans - (b_ans**2 - 4 * a_ans * c_ans) ** 0.5 / 2 * a_ans),
    )


# def x_solutions(x1, x2, y1, y2, r):
#     """
#     According to sympy, for a radius of 50...
#     [
#         {
#             x: x1 - 50*(x1 - x2)/sqrt(x1**2 - 2*x1*x2 + x2**2 + y1**2 - 2*y1*y2 + y2**2)
#         },
#         {
#             x: x1 + 50*(x1 - x2)/sqrt(x1**2 - 2*x1*x2 + x2**2 + y1**2 - 2*y1*y2 + y2**2)
#         }
#     ]
#     """
#     return (
#         (
#             x1
#             - 50
#             * (x1 - x2)
#             / max(1, sqrt(x1**2 - 2 * x1 * x2 + x2**2 + y1**2 - 2 * y1 * y2 + y2**2))
#         ),
#         (
#             x1
#             + 50
#             * (x1 - x2)
#             / max(1, sqrt(x1**2 - 2 * x1 * x2 + x2**2 + y1**2 - 2 * y1 * y2 + y2**2))
#         ),
#     )


def y_solution(x, x1, y1, x2, y2):
    return ((y2 - y1) / (x2 - x1)) * (x - x2) + y2


RADIUS = 50

tl_n1 = 60 - RADIUS
br_n1 = 60 + RADIUS

tl_n2 = 600 - RADIUS
br_n2 = 600 + RADIUS

root = tk.Tk()
root.geometry("1280x720")

canvas = tk.Canvas(root)
canvas.pack(fill=tk.BOTH, expand=True)

canvas.create_oval(
    tl_n1,
    tl_n1,
    br_n1,
    br_n1,
    fill="black",
    width=0,
    tags=("node1"),
)

canvas.create_oval(
    tl_n2,
    tl_n2,
    br_n2,
    br_n2,
    fill="black",
    width=0,
    tags=("node2"),
)

cx1 = (tl_n1 + br_n1) / 2
cy1 = (tl_n1 + br_n1) / 2

cx2 = (tl_n2 + br_n2) / 2
cy2 = (tl_n2 + br_n2) / 2

print(cx1, cy1, cx2, cy2)

# x1s = x_solutions(cx1, cy1, cx2, cy2, RADIUS)
# y1 = y_solution(x1s[0], cx1, cy1, cx2, cy2)

# x2s = x_solutions(cx2, cy2, cx1, cy1, RADIUS)
# y2 = y_solution(x2s[0], cx2, cy2, cx1, cy1)

# print(x1s, y1, x2s, y2)

# for x1 in x1s:
#     for x2 in x2s:
#         canvas.create_line(x1, y1, x2, y2, arrow=tk.BOTH)

# canvas.line(ax1, ay1, ax2, ay2, arrow=tk.BOTH, width=2)

point1 = cx1 + (RADIUS * cos(pi / 4))
point2 = cy1 + (RADIUS * sin(pi / 4))

canvas.create_oval(
    point1 - 5, point2 - 5, point1 + 5, point2 + 5, fill="white", width=0
)

root.mainloop()
