import ttkbootstrap as ttk
import ttkbootstrap.constants as tk
import ttkbootstrap.dialogs as dialogs

from collections import namedtuple
from math import radians, sin, cos, atan2, sqrt

from .rename_dialog import rename_dialog
from .amend_dialog import amend_edge_dialog
from .state_model import StateModel

# Standard conversion type
Canvas_XY = namedtuple("Canvas_XY", "x,y")

# drawing dimensions
NODE_RADIUS = 50
ARC_BULGE = 40


class CanvasFrame(ttk.Frame):
    """
    Class to be in charge of interacting with the Canvas - handles clicks, drags, etc and translates those into actions
    depending on the current toggles as set by the user.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.__canvas = ttk.Canvas(
            self, width=100, height=100, scrollregion=(0, 0, 10000, 10000)
        )
        hs = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        hs.pack(side=tk.BOTTOM, fill=tk.X)
        hs.configure(command=self.__canvas.xview)
        vs = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        vs.configure(command=self.__canvas.yview)
        self.__canvas.configure(xscrollcommand=hs.set, yscrollcommand=vs.set)
        self.__canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.__canvas.bind("<Button-1>", self.__click)
        self.__canvas.bind("<ButtonRelease-1>", self.__release)
        self.__canvas.bind("<B1-Motion>", self.__drag)
        self.__canvas.bind("<Double-Button-1>", self.__double_click)
        self.__canvas.bind("<Double-Button-3>", self.__double_right_click)

        ###
        # Mouse wheel scrolling taken from the answer at
        # https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
        #
        self.__canvas.bind(
            "<MouseWheel>",
            lambda event: self.__canvas.yview_scroll(-1 * event.delta // 120, "units"),
        )
        self.__canvas.bind(
            "<Shift-MouseWheel>",
            lambda event: self.__canvas.xview_scroll(-1 * event.delta // 120, "units"),
        )

        self.__selected = None
        self.__current = None

    def empty(self):
        """
        Called from outside, to clear down the Canvas
        """
        for id in self.__canvas.find_all():
            self.__canvas.delete(id)

    def get_canvas_as_dict(self):
        return {
            id: (
                self.__canvas.type(id),
                self.__canvas.coords(id),
                self.__canvas.gettags(id),
            )
            for id in self.__canvas.find_all()
        }

    def set_canvas_from_dict(self, saved_canvas):
        self.empty()
        # Order really matters - so need to sort as integer, but then key back into dict as string
        for id in list(map(str, sorted(map(int, saved_canvas.keys())))):
            type, coords, tags = saved_canvas[id]
            # print(type, tags)

            if type == "oval":
                x1, y1, x2, y2 = coords
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                self.__canvas.create_oval(
                    cx - NODE_RADIUS,
                    cy - NODE_RADIUS,
                    cx + NODE_RADIUS,
                    cy + NODE_RADIUS,
                    fill="black",
                    width=0,
                    tags=tags,
                )

            elif type == "text":
                if "node" in tags:
                    node_name = None
                    node_label = None
                    for tag in tags:
                        if tag.startswith("nodename_"):
                            node_name = tag[9:]

                        if tag.startswith("nodelabel_"):
                            node_label = tag[10:]

                    # print(
                    #     f"Creating text for node {node_name if node_label is None else node_label} at coords {coords}"
                    # )
                    self.__canvas.tag_raise(
                        self.__canvas.create_text(
                            *coords,
                            fill="white",
                            text=node_name if node_label is None else node_label,
                            tags=tags,
                        ),
                        "node",
                    )

                elif "cost" in tags:
                    weight = 1
                    for tag in tags:
                        if tag.startswith("costvalue_"):
                            weight = tag[10:]

                    self.__canvas.tag_lower(
                        self.__canvas.create_text(
                            *coords,
                            fill="black",
                            text=weight,
                            tags=tags,
                        )
                    )

            elif type == "line":
                # True (ie non-zero) if there is a tag containing "tofrom" thus the edge was undirected
                if len([tag for tag in tags if "tofrom" in tag]):
                    self.__canvas.tag_lower(
                        self.__canvas.create_line(
                            *coords,
                            width=2,
                            tags=tags,
                        ),
                        "node",
                    )
                else:
                    fcx, fcy, tcx, tcy = self.__calculate_edge_boundaries(
                        *(coords[:2] + coords[-2:])
                    )
                    self.__canvas.tag_lower(
                        self.__create_arc_with_arrow(fcx, fcy, tcx, tcy, tags),
                        "node",
                    )

            elif type == "polygon":
                self.__canvas.create_polygon(
                    coords,
                    width=2,
                    fill="",
                    outline="black",
                    smooth=True,
                    tags=tags,
                )

    def get_node_labels(self):
        node_labels = []
        for node in StateModel().get_graph_matrix()[0]:
            node_label = None

            for id in self.__canvas.find_withtag(f"nodename_{node}"):
                for tag in self.__canvas.gettags(id):
                    if tag.startswith("nodelabel_"):
                        node_label = tag[10:]

            if node_label is None:
                node_label = node

            node_labels.append(node_label)

        return node_labels

    def get_node_from_label(self, name_or_label):
        id = self.__canvas.find_withtag(f"nodelabel_{name_or_label}")
        if id is None or len(id) == 0:
            id = self.__canvas.find_withtag(f"nodename_{name_or_label}")

        for tag in self.__canvas.gettags(id):
            if tag.startswith("nodename_"):
                return tag[9:]

    def get_label_from_node(self, name_or_label):
        id = self.__canvas.find_withtag(f"nodelabel_{name_or_label}")
        if id is None or len(id) == 0:
            id = self.__canvas.find_withtag(f"nodename_{name_or_label}")

        nodelabel = None
        for tag in self.__canvas.gettags(id):
            if tag.startswith("nodename_"):
                if nodelabel is None:
                    nodelabel = tag[9:]

            if tag.startswith("nodelabel_"):
                nodelabel = tag[10:]
        return nodelabel

    def highlight_start_node(self, node_name):
        self.__highlight_node(
            node_name,
            True,
            "#006400",  # dark green
            "#FFFF00",  # yellow
        )

    def highlight_end_node(self, node_name):
        self.__highlight_node(
            node_name,
            True,
            "#800000",  # maroon
            "#FFFF00",  # yellow
        )

    def highlight_current_node(self, node_name):
        self.__highlight_node(
            node_name,
            True,
            "#00FF00",  # lime
            "#000000",  # black
        )

    def highlight_processed_node(self, node_name):
        self.__highlight_node(
            node_name,
            True,
            "#CD5C5C",  # "indian red"
            "#FFFF00",  # yellow
        )

    def highlight_pending_node(self, node_name):
        self.__highlight_node(
            node_name,
            True,
            "#808000",  # olive
            "#FFFF00",  # yellow
        )

    def unhighlight_all_nodes(self):
        for node in self.get_node_labels():
            self.__highlight_node(node, False, "", "")

    def __highlight_node(self, node_name, highlight, shape_colour, text_colour):
        id = self.__canvas.find_withtag(f"nodelabel_{node_name}")
        if id is None or len(id) == 0:
            id = self.__canvas.find_withtag(f"nodename_{node_name}")

        associated = self.__find_associated_ids(id)
        for aid in associated:
            tags = self.__canvas.gettags(aid)
            # print(aid, self.__canvas.type(aid), "->", tags)
            for tag in tags:
                if tag.startswith("node_"):
                    if highlight:
                        # print("setting", aid, "fill red")
                        self.__canvas.itemconfig(aid, fill=shape_colour)
                    else:
                        self.__canvas.itemconfig(aid, fill="black")
                elif tag.startswith("nodename_") or tag.startswith("nodelabel_"):
                    if highlight:
                        # print("setting", aid, "fill", text_colour)
                        self.__canvas.itemconfig(aid, fill=text_colour)
                    else:
                        self.__canvas.itemconfig(aid, fill="white")

    def __click(self, event):
        """
        On a mouse down event, if the user is currently operating on "Nodes" then this will either be the start of a
        move (if on a current Node) or a create (if not).

        If moving an existing node, then use the helper function to find the associated ids for the first overlapping
        id clicked on.

        If creating, always create a circle and text node with associated tags.
        """

        # can only make changes if the DrawControlsFrame is showing
        if StateModel().get_current_tab() != "DrawControlsFrame":
            return

        canvas_xy = self.__event_to_canvas(event)
        operation = StateModel().get_operation()
        StateModel().set_changed()

        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(
                canvas_xy.x - NODE_RADIUS // 8,
                canvas_xy.y - NODE_RADIUS // 8,
                canvas_xy.x + NODE_RADIUS // 8,
                canvas_xy.y + NODE_RADIUS // 8,
            )

            if len(possible) != 0:
                self.__selected = self.__find_associated_ids(possible)
                self.__current = (canvas_xy.x, canvas_xy.y)

            else:
                self.__selected = None
                self.__current = None

                node_name = StateModel().get_next_node_name()
                StateModel().add_node(node_name)
                self.__canvas.create_oval(
                    canvas_xy.x - NODE_RADIUS,
                    canvas_xy.y - NODE_RADIUS,
                    canvas_xy.x + NODE_RADIUS,
                    canvas_xy.y + NODE_RADIUS,
                    fill="black",
                    width=0,
                    tags=("node", f"node_{node_name}"),
                )
                self.__canvas.create_text(
                    canvas_xy.x,
                    canvas_xy.y,
                    fill="white",
                    text=node_name,
                    tags=("node", f"nodename_{node_name}"),
                )

        elif operation == "Edges":
            possible = self.__canvas.find_overlapping(
                canvas_xy.x - NODE_RADIUS // 8,
                canvas_xy.y - NODE_RADIUS // 8,
                canvas_xy.x + NODE_RADIUS // 8,
                canvas_xy.y + NODE_RADIUS // 8,
            )

            if len(possible) != 0:
                self.__selected = self.__find_associated_ids(possible)
                self.__current = (canvas_xy.x, canvas_xy.y)

            # the user can only drag from one node to another to create a new edge, or to drag around a loopback for
            # visibility - anything should be ignored, even if it was a valid click
            if self.__selected is not None:
                self.__selected = list(
                    filter(
                        lambda tagOrId: any(
                            "node" == tag
                            or "edge_loopback" == tag
                            or "cost_loopback" == tag
                            for tag in self.__canvas.gettags(tagOrId)
                        ),
                        self.__selected,
                    )
                )
                if len(self.__selected) == 0:
                    self.__selected = None
                    self.__current = None

    def __drag(self, event):
        """
        This method is just a staging point for when the user is dragging something around, which is mostly only
        applicable for moving a node.

        So if the operation is "Nodes", stage each part as moving the selected ids to the current position and then
        storing the new current position. This needs to ensure that nodes are never allowed to overlap.

        But if the operation is "Edges", and something is selected, then the user must be rotating a loopback around...
        so behave accordingly.
        """

        # can only make changes if the DrawControlsFrame is showing
        if StateModel().get_current_tab() != "DrawControlsFrame":
            return

        if self.__selected is None:
            return

        canvas_xy = self.__event_to_canvas(event)
        operation = StateModel().get_operation()
        StateModel().set_changed()

        if operation == "Nodes":
            all_selected_rects = list(
                filter(
                    lambda r: len(r) == 4,
                    [
                        self.__canvas.coords(id)
                        for id in self.__selected
                        if "node" in self.__canvas.gettags(id)
                    ],
                )
            )
            biggest_rect = (
                min(r[0] for r in all_selected_rects),
                min(r[1] for r in all_selected_rects),
                max(r[2] for r in all_selected_rects),
                max(r[3] for r in all_selected_rects),
            )
            # print(f"{biggest_rect=}")
            centre = (
                (biggest_rect[0] + biggest_rect[2]) // 2,
                (biggest_rect[1] + biggest_rect[3]) // 2,
            )
            # print(f"{centre=}")

            distance_to_centre = min(
                NODE_RADIUS,
                int(
                    ((canvas_xy.x - centre[0]) ** 2 + (canvas_xy.y - centre[1]) ** 2)
                    ** 0.5
                ),
            )
            # print(f"{distance_to_centre=}")

            overlap_rect = [
                (
                    canvas_xy.x
                    - (
                        NODE_RADIUS * 4 / 3 - distance_to_centre
                        if canvas_xy.x < centre[0]
                        else NODE_RADIUS * 4 / 3 + distance_to_centre
                    )
                ),
                (
                    canvas_xy.y
                    - (
                        NODE_RADIUS * 4 / 3 - distance_to_centre
                        if canvas_xy.y < centre[1]
                        else NODE_RADIUS * 4 / 3 + distance_to_centre
                    )
                ),
                (
                    canvas_xy.x
                    + (
                        NODE_RADIUS * 4 / 3 - distance_to_centre
                        if canvas_xy.x > centre[0]
                        else NODE_RADIUS * 4 / 3 + distance_to_centre
                    )
                ),
                (
                    canvas_xy.y
                    + (
                        NODE_RADIUS * 4 / 3 - distance_to_centre
                        if canvas_xy.y > centre[1]
                        else NODE_RADIUS * 4 / 3 + distance_to_centre
                    )
                ),
            ]
            # print(f"{overlap_rect=}")

            allowed = "node" not in [
                tag
                for id in self.__canvas.find_overlapping(*overlap_rect)
                if id not in self.__selected
                for tag in self.__canvas.gettags(id)
            ]

            if allowed:
                # if allowed drag the node, along with any loopback edge and cost
                for id in self.__selected:
                    tags = self.__canvas.gettags(id)
                    if (
                        "node" in tags
                        or "edge_loopback" in tags
                        or "cost_loopback" in tags
                    ):
                        self.__canvas.move(
                            id,
                            canvas_xy.x - self.__current[0],
                            canvas_xy.y - self.__current[1],
                        )

                # then drag any other connected edges
                for id in self.__selected:
                    tags = self.__canvas.gettags(id)
                    if "edge" in tags and "edge_loopback" not in tags:
                        for tag in tags:
                            if tag.startswith("edge_fromto_"):
                                _, _, from_node, to_node = tag.split("_")

                        fx1, fy1, fx2, fy2 = self.__canvas.bbox(f"node_{from_node}")
                        fcx, fcy = (fx1 + fx2) / 2, (fy1 + fy2) / 2
                        tx1, ty1, tx2, ty2 = self.__canvas.bbox(f"node_{to_node}")
                        tcx, tcy = (tx1 + tx2) / 2, (ty1 + ty2) / 2

                        if f"edge_tofrom_{from_node}_{to_node}" in tags:
                            self.__canvas.coords(id, fcx, fcy, tcx, tcy)
                            # self.__canvas.tag_lower(id, "node")

                        else:
                            fcx, fcy, tcx, tcy = self.__calculate_edge_boundaries(
                                fcx, fcy, tcx, tcy
                            )
                            self.__redraw_arc_with_arrow(id, fcx, fcy, tcx, tcy)
                            # self.__canvas.tag_lower(id, "node")

                    elif "cost" in tags and "cost_loopback" not in tags:
                        for tag in tags:
                            if tag.startswith("cost_fromto_"):
                                _, _, from_node, to_node = tag.split("_")

                        ex1, ey1, ex2, ey2 = self.__canvas.bbox(
                            f"edge_fromto_{from_node}_{to_node}"
                        )
                        lcx = ((ex1 + ex2) / 2) + 10
                        lcy = ((ey1 + ey2) / 2) - 10
                        self.__canvas.coords(id, lcx, lcy)
                        # self.__canvas.tag_lower(id, "edge")

                self.__current = (canvas_xy.x, canvas_xy.y)

        elif operation == "Edges":
            # for sel in self.__selected:
            #   print(sel, self.__canvas.gettags(sel))

            loopback = -1
            cost_loopback = -1
            node = -1

            try:
                loopback = next(
                    tagOrId
                    for tagOrId in self.__selected
                    for tag in self.__canvas.gettags(tagOrId)
                    if tag == "edge_loopback"
                )

                try:
                    cost_loopback = next(
                        tagOrId
                        for tagOrId in self.__selected
                        for tag in self.__canvas.gettags(tagOrId)
                        if tag == "cost_loopback"
                    )
                except StopIteration:
                    # may not have a weighting
                    pass

                node = next(
                    tagOrId
                    for tagOrId in self.__selected
                    for tag in self.__canvas.gettags(tagOrId)
                    if tag == "node"
                )

                # print(loopback, cost_loopback, node)

                nx1, ny1, nx2, ny2 = self.__canvas.bbox(node)
                ncx, ncy = (nx1 + nx2) / 2, (ny1 + ny2) / 2

                rotation = canvas_xy.x - self.__current[0]
                self.__rotate_object(loopback, (ncx, ncy), -rotation)
                if cost_loopback != -1:
                    self.__rotate_object(cost_loopback, (ncx, ncy), -rotation)
                self.__current = (canvas_xy.x, canvas_xy.y)

            except StopIteration:
                # almost certainly means user is not dragging a loopback
                pass

    def __release(self, event):
        """
        When the mouse is released, assuming the user is trying to create a new edge; the program will need to
        determine which is the destination node and then create an edge from the starting node to this destination
        (note: loopbacks are allowed).
        """

        # can only make changes if the DrawControlsFrame is showing
        if StateModel().get_current_tab() != "DrawControlsFrame":
            return

        # don't try and do anything if there's nothing selected
        if self.__selected is None:
            return

        canvas_xy = self.__event_to_canvas(event)
        operation = StateModel().get_operation()
        directed = StateModel().get_directed()
        weight = StateModel().get_weight()
        StateModel().set_changed()

        if operation == "Edges":
            possible = self.__canvas.find_overlapping(
                canvas_xy.x - NODE_RADIUS // 8,
                canvas_xy.y - NODE_RADIUS // 8,
                canvas_xy.x + NODE_RADIUS // 8,
                canvas_xy.y + NODE_RADIUS // 8,
            )

            if len(possible) != 0:
                from_id = None
                from_node = None
                to_id = None
                to_node = None

                for id in self.__selected:
                    for tag in self.__canvas.gettags(id):
                        if tag.startswith("node_"):
                            from_id = id
                            from_node = tag[5:]
                            # print("from:", from_id, from_node)

                for destination in self.__find_associated_ids(possible):
                    for tag in self.__canvas.gettags(destination):
                        if tag.startswith("node_"):
                            to_id = destination
                            to_node = tag[5:]
                            # print("to:", to_id, to_node)

                StateModel().add_edge(
                    from_node,
                    to_node,
                    not directed,
                    int(weight) if weight != "None" else None,
                )
                if from_node != to_node:
                    fx1, fy1, fx2, fy2 = self.__canvas.bbox(from_id)
                    fcx, fcy = (fx1 + fx2) / 2, (fy1 + fy2) / 2
                    tx1, ty1, tx2, ty2 = self.__canvas.bbox(to_id)
                    tcx, tcy = (tx1 + tx2) / 2, (ty1 + ty2) / 2

                    if directed:
                        fcx, fcy, tcx, tcy = self.__calculate_edge_boundaries(
                            fcx, fcy, tcx, tcy
                        )
                        self.__canvas.tag_lower(
                            self.__create_arc_with_arrow(
                                fcx,
                                fcy,
                                tcx,
                                tcy,
                                tags=(
                                    "edge",
                                    f"edge_{from_node}",
                                    f"edge_{to_node}",
                                    f"edge_fromto_{from_node}_{to_node}",
                                ),
                            ),
                            "node",
                        )
                        if weight != "None":
                            lcx, lcy = ((fcx + tcx) / 2) + 10, ((fcy + tcy) / 2) - 10
                            self.__canvas.tag_lower(
                                self.__canvas.create_text(
                                    lcx,
                                    lcy,
                                    fill="black",
                                    text=weight,
                                    tags=(
                                        "cost",
                                        f"cost_{from_node}",
                                        f"cost_{to_node}",
                                        f"cost_fromto_{from_node}_{to_node}",
                                        f"costvalue_{weight}",
                                    ),
                                ),
                                "edge",
                            )

                    else:
                        self.__canvas.tag_lower(
                            self.__canvas.create_line(
                                fcx,
                                fcy,
                                tcx,
                                tcy,
                                width=2,
                                tags=(
                                    "edge",
                                    f"edge_{from_node}",
                                    f"edge_{to_node}",
                                    f"edge_fromto_{from_node}_{to_node}",
                                    f"edge_tofrom_{from_node}_{to_node}",
                                ),
                            ),
                            "node",
                        )
                        if weight != "None":
                            lcx, lcy = ((fcx + tcx) / 2) + 10, ((fcy + tcy) / 2) - 10
                            self.__canvas.tag_lower(
                                self.__canvas.create_text(
                                    lcx,
                                    lcy,
                                    fill="black",
                                    text=weight,
                                    tags=(
                                        "cost",
                                        f"cost_{from_node}",
                                        f"cost_{to_node}",
                                        f"cost_fromto_{from_node}_{to_node}",
                                        f"cost_tofrom_{from_node}_{to_node}",
                                        f"costvalue_{weight}",
                                    ),
                                ),
                                "edge",
                            )

                else:
                    existing = self.__canvas.find_withtag(f"edge_loopback_{from_node}")
                    if existing is None or len(existing) == 0:
                        # loopback time
                        lx1, ly1, lx2, ly2 = self.__canvas.bbox(from_id)
                        lcx, lcy = (lx1 + lx2) / 2, (ly1 + ly2) / 2
                        self.__canvas.tag_lower(
                            self.__create_loopback_as_polygon(
                                (lcx + NODE_RADIUS, lcy + NODE_RADIUS),
                                NODE_RADIUS,
                                (
                                    "edge",
                                    "edge_loopback",
                                    f"edge_loopback_{from_node}",
                                    f"edge_{from_node}",
                                    f"edge_fromto_{from_node}_{to_node}",
                                ),
                            ),
                            "node",
                        )
                        if weight != "None":
                            self.__canvas.tag_lower(
                                self.__canvas.create_text(
                                    lcx + NODE_RADIUS * 2,
                                    lcy + NODE_RADIUS * 2,
                                    fill="black",
                                    text=weight,
                                    tags=(
                                        "cost",
                                        "cost_loopback",
                                        f"cost_loopback_{from_node}",
                                        f"cost_{from_node}",
                                        f"cost_fromto_{from_node}_{to_node}",
                                        f"costvalue_{weight}",
                                    ),
                                ),
                                "edge",
                            )

    def __double_click(self, event):
        """
        On a double (left) click event, the user is choosing to edit the current item - whatever that may be.

        If editing "Nodes" then always assume they've meant to change the pair that is associated with the lowest id
        clicked.

        If editing "Edges" then there should only be one id returned.
        """

        # can only make changes if the DrawControlsFrame is showing
        if StateModel().get_current_tab() != "DrawControlsFrame":
            return

        canvas_xy = self.__event_to_canvas(event)
        operation = StateModel().get_operation()
        StateModel().set_changed()

        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(
                canvas_xy.x - NODE_RADIUS // 8,
                canvas_xy.y - NODE_RADIUS // 8,
                canvas_xy.x + NODE_RADIUS // 8,
                canvas_xy.y + NODE_RADIUS // 8,
            )
            if len(possible) != 0:
                selected = self.__find_associated_ids(possible)

                for id in selected:
                    nodelabel = None
                    for tag in self.__canvas.gettags(id):
                        # there may be multiple hits, but the one we want to use has two tags, one is the generic
                        # "node", the other contains the text we need...
                        if tag.startswith("nodename_"):
                            if nodelabel is None:
                                nodelabel = tag[9:]

                        if tag.startswith("nodelabel_"):
                            nodelabel = tag[10:]

                    if nodelabel is not None:
                        new_name = rename_dialog(self, "Rename Node", nodelabel)
                        if new_name is not None:
                            self.__canvas.dchars(id, 0, "end")
                            self.__canvas.insert(id, tk.INSERT, new_name)
                            self.__canvas.addtag_withtag(f"nodelabel_{new_name}", id)

        elif operation == "Edges":
            # editing the cost of travelling the path
            if StateModel().is_weighted():
                possible = self.__canvas.find_overlapping(
                    canvas_xy.x - NODE_RADIUS // 8,
                    canvas_xy.y - NODE_RADIUS // 8,
                    canvas_xy.x + NODE_RADIUS // 8,
                    canvas_xy.y + NODE_RADIUS // 8,
                )

                print("found possibles near edge...")
                for p in possible:
                    print(p, "->", self.__canvas.gettags(p))

                if len(possible) != 0:
                    for p in possible:
                        tags = self.__canvas.gettags(p)
                        # don't try and process the "cost" text
                        if "edge" in tags:
                            from_node = None
                            to_node = None
                            for tag in tags:
                                if tag.startswith("edge_fromto_"):
                                    _, _, from_node, to_node = tag.split("_")

                            fromto = StateModel().has_edge(from_node, to_node)
                            tofrom = StateModel().has_edge(to_node, from_node)

                            print(type(fromto), fromto, type(tofrom), tofrom)

                            if (
                                not isinstance(fromto, bool)
                                and not isinstance(tofrom, bool)
                                and fromto != tofrom
                            ):
                                values = amend_edge_dialog(
                                    self,
                                    "Amend edge weights",
                                    from_node,
                                    to_node,
                                    [fromto, tofrom],
                                )
                                if values:
                                    if values[0] != "None":
                                        StateModel().add_edge(
                                            from_node, to_node, False, int(values[0])
                                        )
                                        # also need to update the from cost text and tag
                                        cost_id = self.__canvas.find_withtag(
                                            f"cost_fromto_{from_node}_{to_node}"
                                        )
                                        self.__canvas.dchars(cost_id, 0, "end")
                                        self.__canvas.insert(
                                            cost_id, tk.INSERT, values[0]
                                        )
                                        self.__canvas.dtag(
                                            cost_id, f"costvalue_{fromto}"
                                        )
                                        self.__canvas.addtag_withtag(
                                            f"costvalue_{values[0]}",
                                            cost_id,
                                        )
                                    if values[1] != "None":
                                        StateModel().add_edge(
                                            to_node, from_node, False, int(values[1])
                                        )
                                        # also need to update the to cost text and tag
                                        cost_id = self.__canvas.find_withtag(
                                            f"cost_tofrom_{to_node}_{from_node}"
                                        )
                                        self.__canvas.dchars(cost_id, 0, "end")
                                        self.__canvas.insert(
                                            cost_id, tk.INSERT, values[1]
                                        )
                                        self.__canvas.dtag(
                                            cost_id, f"costvalue_{tofrom}"
                                        )
                                        self.__canvas.addtag_withtag(
                                            f"costvalue_{values[1]}",
                                            cost_id,
                                        )
                            else:
                                # found the edge as "_fromto_" (or "_loopback_") so use that value
                                values = amend_edge_dialog(
                                    self,
                                    "Amend edge weight",
                                    from_node,
                                    to_node,
                                    [fromto],
                                )
                                if values:
                                    if values[0] != "None":
                                        StateModel().add_edge(
                                            from_node, to_node, True, int(values[0])
                                        )
                                        # also need to update the cost text and tag
                                        cost_id = self.__canvas.find_withtag(
                                            f"cost_fromto_{from_node}_{to_node}"
                                        )
                                        self.__canvas.dchars(cost_id, 0, "end")
                                        self.__canvas.insert(
                                            cost_id, tk.INSERT, values[0]
                                        )
                                        self.__canvas.dtag(
                                            cost_id, f"costvalue_{fromto}"
                                        )
                                        self.__canvas.addtag_withtag(
                                            f"costvalue_{values[0]}",
                                            cost_id,
                                        )

    def __double_right_click(self, event):
        """
        On a double (right) click event, the user is choosing to delete the current item - whatever that may be.

        If deleting "Nodes" then always assume they've meant to remove the circle and text that is associated with the
        id clicked, along with any edges that link to it.

        If deleting "Edges" then there should only be one id returned - just remove that one.
        """

        # can only make changes if the DrawControlsFrame is showing
        if StateModel().get_current_tab() != "DrawControlsFrame":
            return

        canvas_xy = self.__event_to_canvas(event)
        operation = StateModel().get_operation()
        StateModel().set_changed()

        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(
                canvas_xy.x - NODE_RADIUS // 8,
                canvas_xy.y - NODE_RADIUS // 8,
                canvas_xy.x + NODE_RADIUS // 8,
                canvas_xy.y + NODE_RADIUS // 8,
            )

            if len(possible) != 0:
                selected = self.__find_associated_ids(possible)

                # DEBUG: print out the associated id/labels of the node the user has doouble-clicked to delete
                for tagOrId in selected:
                    print(
                        f"Deleting: {tagOrId} / {', '.join(self.__canvas.gettags(tagOrId))}"
                    )

                node_loopback = None
                node_label = None

                for id in selected:
                    for tag in self.__canvas.gettags(id):
                        # there may be multiple hits, but the one we want to use has multiple tags, one is the generic
                        # "node", the others contain the values we need...
                        if tag.startswith("node_"):
                            node_loopback = tag[5:]

                        if tag.startswith("nodelabel_"):
                            node_label = tag[10:]

                if node_label is None:
                    node_label = node_loopback

                if (
                    dialogs.Messagebox.yesno(
                        message=f"Are you sure you want to delete '{node_label}'?"
                    )
                    == "Yes"
                ):
                    StateModel().delete_node(node_loopback)
                    for id in selected:
                        self.__canvas.delete(id)

        elif operation == "Edges":
            possible = self.__canvas.find_overlapping(
                canvas_xy.x - NODE_RADIUS // 8,
                canvas_xy.y - NODE_RADIUS // 8,
                canvas_xy.x + NODE_RADIUS // 8,
                canvas_xy.y + NODE_RADIUS // 8,
            )

            if len(possible) != 0:
                node_loopback = None
                node_from = None
                node_to = None

                for id in possible:
                    for tag in self.__canvas.gettags(id):
                        # there may be multiple hits, but the one we want to use has multiple tags, one is the generic
                        # "edge", one of the others contains the text we need...
                        if tag.startswith("edge_fromto_"):
                            _, _, node_from, node_to = tag.split("_")

                        elif tag.startswith("edge_loopback_"):
                            node_loopback = tag[14:]

            if node_loopback is not None:
                if (
                    dialogs.Messagebox.yesno(
                        message=f"Are you sure you want to delete the loopback edge on '{node_loopback}'?"
                    )
                    == "Yes"
                ):
                    StateModel().delete_edge(node_loopback, node_loopback)
                    self.__canvas.delete(id)
                    self.__canvas.delete(f"cost_loopback_{node_loopback}")

            elif node_from is not None and node_to is not None:
                if (
                    dialogs.Messagebox.yesno(
                        message=f"Are you sure you want to delete the edge from '{node_from}' to '{node_to}'?"
                    )
                    == "Yes"
                ):
                    StateModel().delete_edge(node_from, node_to)
                    self.__canvas.delete(id)
                    self.__canvas.delete(f"cost_fromto_{node_from}_{node_to}")

    def __find_associated_ids(self, possible):
        associated = set()

        for tagOrId in possible:
            tags = self.__canvas.gettags(tagOrId)
            if "node" in tags:
                associated = associated.union([tagOrId])

                for tag in tags:
                    if tag.startswith("node_"):
                        node = tag[5:]
                        associated = associated.union(
                            self.__canvas.find_withtag(f"nodename_{node}")
                        )

                    elif tag.startswith("nodename_"):
                        node = tag[9:]
                        associated = associated.union(
                            self.__canvas.find_withtag(f"node_{node}")
                        )

                associated = associated.union(
                    self.__canvas.find_withtag(f"edge_{node}")
                )
                associated = associated.union(
                    self.__canvas.find_withtag(f"cost_{node}")
                )

            elif "edge_loopback" in tags:
                associated = associated.union([tagOrId])

                for tag in tags:
                    if tag.startswith("edge_"):
                        node = tag[5:]
                        associated = associated.union(
                            self.__canvas.find_withtag(f"node_{node}")
                        )
                        associated = associated.union(
                            self.__canvas.find_withtag(f"nodename_{node}")
                        )
                        associated = associated.union(
                            self.__canvas.find_withtag(f"cost_loopback_{node}")
                        )

            elif "edge" in tags or "cost" in tags:
                pass

            else:
                raise ValueError(f"Unknown object on canvas with tags {tags}")

        # print(associated)
        return list(associated)

    ###
    # from the answer at
    # https://stackoverflow.com/questions/14829621/formula-to-find-points-on-the-circumference-of-a-circle-given-the-center-of-the
    #
    def __create_loopback_as_polygon(self, centre, radius, tags):
        cx, cy = centre

        points = []
        for t in range(-100, 200, 4):
            x = radius * cos(radians(t)) + cx
            y = radius * sin(radians(t)) + cy
            points.append((x, y))

        return self.__canvas.create_polygon(
            points,
            width=2,
            fill="",
            outline="black",
            smooth=True,
            tags=tags,
        )

    def __calculate_edge_boundaries(self, from_cx, from_cy, to_cx, to_cy):
        # what to do with an infinite gradient? simply subtract from the y-values and leave the x alone,
        # according to which node is the uppermost
        if from_cx == to_cx:
            if from_cy < to_cy:
                from_cy += 50
                to_cy -= 50
            else:
                from_cy -= 50
                to_cy += 50

        # same gradient (on the same y-axis), so just adjust according to which node is leftmost
        elif from_cy == to_cy:
            if from_cx < to_cx:
                from_cx += 50
                to_cx -= 50
            else:
                from_cx -= 50
                to_cx += 50

        # find the correct combination of plus/minus x/y to ensure the correct orientation to the other
        # but bear in mind that (0,0) is top-left and y is +ve going downwards...
        else:
            gradient = (to_cy - from_cy) / (to_cx - from_cx)

            # adjust, by using a similar triangle, to calculate the proportions for a hypoteneuse of
            # 50 ensuring the correct difference is used for a positive or negative gradient
            hypoteneuse = sqrt((from_cy - to_cy) ** 2 + (from_cx - to_cx) ** 2)
            proportion = 50 / hypoteneuse

            # "negative" gradient...
            if gradient < 0:
                dx = proportion * abs(from_cx - to_cx)
                dy = proportion * abs(from_cy - to_cy)
                # print("negative", gradient, dx, dy)

                # if "from" is bigger, then the line goes up-right of the "from" and down-left of the "to"
                if from_cy > to_cy:
                    from_cx += dx
                    from_cy -= dy
                    to_cx -= dx
                    to_cy += dy

                # otherwise, the line goes down-left of "from" and up-right of "to"
                else:
                    from_cx -= dx
                    from_cy += dy
                    to_cx += dx
                    to_cy -= dy

            # "positive" gradient
            else:
                dx = proportion * abs(from_cx - to_cx)
                dy = proportion * abs(from_cy - to_cy)
                # print("positive", gradient, dx, dy)

                # if "from" is smaller, then the line goes down-right of the "from" and up-left of the "to"
                if from_cy < to_cy:
                    from_cx += dx
                    from_cy += dy
                    to_cx -= dx
                    to_cy -= dy

                # otherwise, the line goes up-left of "from" and down-right of "to"
                else:
                    from_cx -= dx
                    from_cy -= dy
                    to_cx += dx
                    to_cy += dy

        return from_cx, from_cy, to_cx, to_cy

    def __create_arc_with_arrow(self, from_cx, from_cy, to_cx, to_cy, tags):
        """
        Code taken from the author's own answer at
        https://stackoverflow.com/questions/36958438/draw-an-arc-between-two-points-on-a-tkinter-canvas
        """

        t = atan2(to_cy - from_cy, to_cx - from_cx)
        mid_x = (from_cx + to_cx) / 2 + ARC_BULGE * sin(t)
        mid_y = (from_cy + to_cy) / 2 - ARC_BULGE * cos(t)

        return self.__canvas.create_line(
            from_cx,
            from_cy,
            mid_x,
            mid_y,
            to_cx,
            to_cy,
            fill="blue",
            width=2,
            arrow=tk.LAST,
            smooth=True,
            tags=tags,
        )

    def __redraw_arc_with_arrow(self, tagOrId, from_cx, from_cy, to_cx, to_cy):
        """
        Adapted from above
        """

        t = atan2(to_cy - from_cy, to_cx - from_cx)
        mid_x = (from_cx + to_cx) / 2 + ARC_BULGE * sin(t)
        mid_y = (from_cy + to_cy) / 2 - ARC_BULGE * cos(t)

        return self.__canvas.coords(
            tagOrId,
            from_cx,
            from_cy,
            mid_x,
            mid_y,
            to_cx,
            to_cy,
        )

    def __rotate_object(self, tagOrId, origin, angle):
        """
        Rotate object on the canvas (expected to be a loopback, at the minute). Script adapted from
        https://wiki.tcl-lang.org/page/Canvas+Rotation

        Args:
            tagOrId (int or string): Object to be rotated, can be a single id or a composite given by a tag
            origin (int pair): x, y for the point of rotation
            angle (int): amount of turn, in degrees
        """

        ox, oy = origin
        rangle = radians(angle)

        # process each component separately
        for id in self.__canvas.find_withtag(tagOrId):
            new_coords = []

            for x, y in zip(*[iter(self.__canvas.coords(id))] * 2):
                # rotates vector (ox,oy)->(x,y) by angle clockwise
                x -= ox  # shift to origin
                y -= oy
                rx = x * cos(rangle) - y * sin(rangle) + ox  # rotate and shift back
                ry = x * sin(rangle) + y * cos(rangle) + oy
                new_coords += (rx, ry)

            self.__canvas.coords(id, new_coords)

    def __event_to_canvas(self, event):
        """
        Given this is a scrollable Canvas, cope with converting the Event x/y into an actual Canvas x/y

        Args:
            event: for the given event, assume will contain x/y pair

        Returns:
            Canvas_XY: named tuple containing x/y values
        """
        return Canvas_XY(
            event.x + self.__canvas.canvasx(0),
            event.y + self.__canvas.canvasy(0),
        )
