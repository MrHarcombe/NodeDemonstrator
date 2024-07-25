import customtkinter as ctk
from tkinter import messagebox
from collections import namedtuple
from math import radians, sin, cos

from rename_dialog import rename_dialog
from amend_dialog import amend_edge_dialog
from state_model import StateModel

# Standard conversion type
Canvas_XY = namedtuple("Canvas_XY", "x,y")

# drawing dimensions
NODE_RADIUS = 50


class CanvasFrame(ctk.CTkFrame):
    """
    Class to be in charge of interacting with the Canvas - handles clicks, drags, etc and translates those into actions
    depending on the current toggles as set by the user.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.__canvas = ctk.CTkCanvas(
            self, width=100, height=100, scrollregion=(0, 0, 10000, 10000)
        )
        hs = ctk.CTkScrollbar(self, orientation=ctk.HORIZONTAL)
        hs.pack(side=ctk.BOTTOM, fill=ctk.X)
        hs.configure(command=self.__canvas.xview)
        vs = ctk.CTkScrollbar(self, orientation=ctk.VERTICAL)
        vs.pack(side=ctk.RIGHT, fill=ctk.Y)
        vs.configure(command=self.__canvas.yview)
        self.__canvas.configure(xscrollcommand=hs.set, yscrollcommand=vs.set)
        self.__canvas.pack(side=ctk.LEFT, expand=True, fill=ctk.BOTH)

        self.__canvas.bind("<Button-1>", self.__click)
        self.__canvas.bind("<ButtonRelease-1>", self.__release)
        self.__canvas.bind("<B1-Motion>", self.__drag)
        self.__canvas.bind("<Double-Button-1>", self.__double_click)
        self.__canvas.bind("<Double-Button-3>", self.__double_right_click)

        ###
        # Mouse wheel scrolling taken from the answer at
        # https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
        # w
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
                self.__canvas.tag_lower(
                    self.__canvas.create_line(
                        *coords,
                        width=2,
                        tags=tags,
                    ),
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
        canvas_xy = self.__event_to_canvas(event)

        operation = StateModel().get_operation()
        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(
                canvas_xy.x - NODE_RADIUS // 4,
                canvas_xy.y - NODE_RADIUS // 4,
                canvas_xy.x + NODE_RADIUS // 4,
                canvas_xy.y + NODE_RADIUS // 4,
            )

            if len(possible) != 0:
                self.__selected = self.__find_associated_ids(possible)
                self.__current = (canvas_xy.x, canvas_xy.y)

            else:
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
                canvas_xy.x - NODE_RADIUS // 4,
                canvas_xy.y - NODE_RADIUS // 4,
                canvas_xy.x + NODE_RADIUS // 4,
                canvas_xy.y + NODE_RADIUS // 4,
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
        storing the new current position.

        But if the operation is "Edges", and something is selected, then the user must be rotating a loopback around...
        so behave accordingly.
        """
        if self.__selected is not None:
            canvas_xy = self.__event_to_canvas(event)
            operation = StateModel().get_operation()

            if operation == "Nodes":
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
                        self.__canvas.coords(id, fcx, fcy, tcx, tcy)
                        self.__canvas.tag_lower(id, "node")

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
                        self.__canvas.tag_lower(id, "edge")

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

        # don't try and do anything if there's nothing selected
        if self.__selected is None:
            return

        canvas_xy = self.__event_to_canvas(event)
        operation = StateModel().get_operation()
        directed = StateModel().get_directed()
        weight = StateModel().get_weight()

        if operation == "Edges":
            possible = self.__canvas.find_overlapping(
                canvas_xy.x - NODE_RADIUS // 4,
                canvas_xy.y - NODE_RADIUS // 4,
                canvas_xy.x + NODE_RADIUS // 4,
                canvas_xy.y + NODE_RADIUS // 4,
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
                    lcx, lcy = ((fcx + tcx) / 2) + 10, ((fcy + tcy) / 2) - 10

                    if directed:
                        self.__canvas.tag_lower(
                            self.__canvas.create_line(
                                fcx,
                                fcy,
                                tcx,
                                tcy,
                                arrow=ctk.LAST,
                                width=2,
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
                                    f"edge_fromto_{to_node}_{from_node}",
                                ),
                            ),
                            "node",
                        )
                        if weight != "None":
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
                                        f"cost_fromto_{to_node}_{from_node}",
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
                                    f"edge_{from_node}_{to_node}",
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
        canvas_xy = self.__event_to_canvas(event)
        operation = StateModel().get_operation()

        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(
                canvas_xy.x - NODE_RADIUS // 4,
                canvas_xy.y - NODE_RADIUS // 4,
                canvas_xy.x + NODE_RADIUS // 4,
                canvas_xy.y + NODE_RADIUS // 4,
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
                            self.__canvas.insert(id, ctk.INSERT, new_name)
                            self.__canvas.addtag_withtag(f"nodelabel_{new_name}", id)

        elif operation == "Edges":
            # editing the cost of travelling the path
            if StateModel().is_weighted():
                possible = self.__canvas.find_overlapping(
                    canvas_xy.x - NODE_RADIUS // 4,
                    canvas_xy.y - NODE_RADIUS // 4,
                    canvas_xy.x + NODE_RADIUS // 4,
                    canvas_xy.y + NODE_RADIUS // 4,
                )

                if len(possible) != 0:
                    # print(id, self.__canvas.gettags(id))
                    tags = self.__canvas.gettags(possible[0])
                    from_node = None
                    to_node = None
                    for tag in tags:
                        if tag.startswith("edge_fromto_"):
                            _, _, from_node, to_node = tag.split("_")

                    fromto = StateModel().has_edge(from_node, to_node)
                    tofrom = StateModel().has_edge(to_node, from_node)

                    if fromto == tofrom:
                        values = amend_edge_dialog(
                            self,
                            "Amend edge weight",
                            from_node,
                            to_node,
                            [fromto],
                        )
                        # print(values)
                        if values:
                            if values[0] != "None":
                                StateModel().add_edge(
                                    from_node, to_node, True, int(values[0])
                                )
                    else:
                        values = amend_edge_dialog(
                            self,
                            "Amend edge weights",
                            from_node,
                            to_node,
                            [fromto, tofrom],
                        )
                        # print(values)
                        if values:
                            if values[0] != "None":
                                StateModel().add_edge(
                                    from_node, to_node, False, int(values[0])
                                )
                            if values[1] != "None":
                                StateModel().add_edge(
                                    to_node, from_node, False, int(values[1])
                                )

    def __double_right_click(self, event):
        """
        On a double (right) click event, the user is choosing to delete the current item - whatever that may be.

        If deleting "Nodes" then always assume they've meant to remove the circle and text that is associated with the
        id clicked, along with any edges that link to it.

        If deleting "Edges" then there should only be one id returned - just remove that one.
        """
        canvas_xy = self.__event_to_canvas(event)
        operation = StateModel().get_operation()

        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(
                canvas_xy.x - NODE_RADIUS // 4,
                canvas_xy.y - NODE_RADIUS // 4,
                canvas_xy.x + NODE_RADIUS // 4,
                canvas_xy.y + NODE_RADIUS // 4,
            )

            if len(possible) != 0:
                selected = self.__find_associated_ids(possible)
                node = None
                node_label = None

                for id in selected:
                    for tag in self.__canvas.gettags(id):
                        # there may be multiple hits, but the one we want to use has multiple tags, one is the generic
                        # "node", the others contain the values we need...
                        if tag.startswith("node_"):
                            node = tag[5:]

                        if tag.startswith("nodelabel_"):
                            node_label = tag[10:]

                if node_label is None:
                    node_label = node

                if messagebox.askyesno(
                    message=f"Are you sure you want to delete '{node_label}'?"
                ):
                    StateModel().delete_node(node)
                    for id in selected:
                        self.__canvas.delete(id)

        elif operation == "Edges":
            possible = self.__canvas.find_overlapping(
                canvas_xy.x - NODE_RADIUS // 4,
                canvas_xy.y - NODE_RADIUS // 4,
                canvas_xy.x + NODE_RADIUS // 4,
                canvas_xy.y + NODE_RADIUS // 4,
            )

            if len(possible) != 0:
                # selected = self.__find_associated_ids(possible)
                for id in possible:
                    for tag in self.__canvas.gettags(id):
                        # there may be multiple hits, but the one we want to use has multiple tags, one is the generic
                        # "edge", one of the others contains the text we need...
                        if tag.startswith("edge_fromto_"):
                            _, _, node_from, node_to = tag.split("_")
                            if messagebox.askyesno(
                                message=f"Are you sure you want to delete the edge from '{node_from}' to '{node_to}'?"
                            ):
                                StateModel().delete_edge(node_from, node_to)
                                self.__canvas.delete(id)

                        elif tag.startswith("edge_loopback_"):
                            node = tag[14:]
                            if messagebox.askyesno(
                                message=f"Are you sure you want to delete the loopback edge on '{node}'?"
                            ):
                                StateModel().delete_edge(node, node)
                                self.__canvas.delete(id)

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

    def __create_arc_with_arrow(self, from_cx, from_cy, to_cx, to_cy, tags):
        radius = 250
        coords = []

        for t in range(270, 360, 4):
            x = radius * cos(radians(t))
            y = radius * sin(radians(t))
            coords += (x, y)

        id = self.__canvas.create_line(
            coords,
            arrow="last",
            smooth=1,
            tags=tags,
        )
        self.__canvas.coords(id, from_cx, from_cy, to_cx, to_cy)
        return id

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
