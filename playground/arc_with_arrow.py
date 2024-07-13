###
# adapted / translated from the answer at
# https://www.perlmonks.org/?node_id=800025
#

# use Tk;

import tkinter as tk
from math import pi, sin, cos

# my $top = MainWindow->new;
# my $can = $top->Canvas()->pack();

root = tk.Tk()
root.geometry("1280x720")
canvas = tk.Canvas(root)
canvas.pack(expand=True, fill=tk.BOTH)

# my @offset = (100, 100);

# my $PI = atans2(1,1) * 4;
# my $max = 100;
# my $radius = 20;
# my $start=35;
# my $end=$max-22;

max = 10
radius = 100
start = 1
end = max

# Generate list of line segments...
# my @coords;
coords = []

# foreach my $i (1..$end) {
#     my $radians = ($i+$start)*2*$PI/$max, $radius;
#     my @nextXY = (
#         $radius * sin($radians),    # X-val
#         $radius * cos($radians),    # Y-val
#     );
#     push(@coords, @nextXY);
# }

for i in range(1, end + 1):
    radians = (i + start) * 2 * pi / max
    next_xy = (
        radius * sin(radians),
        radius * cos(radians),
    )
    coords += next_xy

# Fix things for the arrowhead...
# $coords[-1] -= 2; # y
# $coords[-2] += 2; # x

# coords[-1] -= 2
# coords[-2] -= 2

# Draw the line (arrowed arc)...
# my $l = $can->create('line', \@coords, -arrow=>'last');
# $can->move($l, @offset);

arc = canvas.create_line(coords, arrow="last", smooth=1)
x1, y1, x2, y2 = canvas.bbox(arc)
# print(x1, y1)
canvas.move(arc, 10 - x1, 10 - y1)

root.mainloop()
