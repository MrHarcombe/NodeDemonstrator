import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from math import radians, sin, cos

from rename_dialog import rename_dialog
from state_model import StateModel

# drawing dimensions
NODE_RADIUS = 50


class CanvasFrame(ttk.Frame):
    """
    Class to be in charge of interacting with the Canvas - handles clicks, drags, etc and translates those into actions
    depending on the current toggles as set by the user.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.__canvas = tk.Canvas(
            self, width=100, height=100, scrollregion=(0, 0, 10000, 10000)
        )
        hs = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        hs.pack(side=tk.BOTTOM, fill=tk.X)
        hs.config(command=self.__canvas.xview)
        vs = tk.Scrollbar(self, orient=tk.VERTICAL)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        vs.config(command=self.__canvas.yview)
        self.__canvas.config(xscrollcommand=hs.set, yscrollcommand=vs.set)
        self.__canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.__canvas.bind("<Button-1>", self.__click)
        self.__canvas.bind("<ButtonRelease-1>", self.__release)
        self.__canvas.bind("<B1-Motion>", self.__drag)
        self.__canvas.bind("<Double-Button-1>", self.__double_click)
        self.__canvas.bind("<Double-Button-3>", self.__right_double_click)

        self.__selected = None
        self.__current = None

    def __click(self, event):
        """
        On a mouse down event, if the user is currently operating on "Nodes" then this will either be the start of a
        move (if on a current Node) or a create (if not).

        If moving an existing node, then use the helper function to find the associated ids for the first overlapping
        id clicked on.

        If creating, always create a circle and text node with associated tags.
        """
        operation = StateModel().get_operation()
        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(
                event.x - NODE_RADIUS,
                event.y - NODE_RADIUS,
                event.x + NODE_RADIUS,
                event.y + NODE_RADIUS,
            )

            if len(possible) != 0:
                self.__selected = self.__find_associated_ids(possible)
                self.__current = (event.x, event.y)

            else:
                node_name = StateModel().get_next_node_name()
                StateModel().add_node(node_name)
                self.__canvas.create_oval(
                    event.x - NODE_RADIUS,
                    event.y - NODE_RADIUS,
                    event.x + NODE_RADIUS,
                    event.y + NODE_RADIUS,
                    fill="black",
                    width=0,
                    tags=("node", f"node_{node_name}"),
                )
                self.__canvas.create_text(
                    event.x,
                    event.y,
                    fill="white",
                    text=node_name,
                    tags=("node", f"nodetext_{node_name}"),
                )

        elif operation == "Edges":
            possible = self.__canvas.find_overlapping(
                event.x - NODE_RADIUS,
                event.y - NODE_RADIUS,
                event.x + NODE_RADIUS,
                event.y + NODE_RADIUS,
            )

            if len(possible) != 0:
                self.__selected = self.__find_associated_ids(possible)
                self.__current = (event.x, event.y)

            # the user can only drag from one node to another to create a new edge, or to drag around a loopback for
            # visibility - anything should be ignored, even if it was a valid click
            if self.__selected is not None:
                print("on click, selected =", self.__selected)
                tags = [
                    (selected, self.__canvas.gettags(selected))
                    for selected in self.__selected
                ]
                print("pre, selected tags =", tags)
                self.__selected = list(
                    filter(
                        lambda tagOrId: any(
                            "node" == tag or "edge_loopback" == tag
                            for tag in self.__canvas.gettags(tagOrId)
                        ),
                        self.__selected,
                    )
                )
                if len(self.__selected) == 0:
                    self.__selected = None
                    self.__current = None
                tags = [
                    (selected, self.__canvas.gettags(selected))
                    for selected in self.__selected
                ]
                print("post, selected tags =", tags)

    def __release(self, event):
        """
        When the mouse is released, assuming the user is trying to create a new edge; the program will need to
        determine which is the destination node and then create an edge from the starting node to this destination
        (note: loopbacks are allowed).
        """

        # don't try and do anything if there's nothing selected
        if self.__selected is None:
            return

        operation = StateModel().get_operation()
        if operation == "Edges":
            possible = self.__canvas.find_overlapping(
                event.x - NODE_RADIUS,
                event.y - NODE_RADIUS,
                event.x + NODE_RADIUS,
                event.y + NODE_RADIUS,
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
                            from_node = tag[tag.index("_") + 1 :]

                for destination in self.__find_associated_ids(possible):
                    for tag in self.__canvas.gettags(destination):
                        if tag.startswith("node_"):
                            to_id = destination
                            to_node = tag[tag.index("_") + 1 :]

                StateModel().add_edge(from_node, to_node)
                if from_node != to_node:
                    fx1, fy1, fx2, fy2 = self.__canvas.coords(from_id)
                    fcx, fcy = (fx1 + fx2) / 2, (fy1 + fy2) / 2
                    tx1, ty1, tx2, ty2 = self.__canvas.coords(to_id)
                    tcx, tcy = (tx1 + tx2) / 2, (ty1 + ty2) / 2
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
                                f"edge_from_{from_node}",
                                f"edge_to_{to_node}",
                            ),
                        ),
                        1,
                    )

                else:
                    # loopback time
                    lx1, ly1, lx2, ly2 = self.__canvas.coords(from_id)
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
                        1,
                    )

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
            operation = StateModel().get_operation()
            if operation == "Nodes":
                for id in self.__selected:
                    tags = self.__canvas.gettags(id)
                    if "node" in tags or "edge_loopback" in tags:
                        self.__canvas.move(
                            id, event.x - self.__current[0], event.y - self.__current[1]
                        )

                for id in self.__selected:
                    tags = self.__canvas.gettags(id)
                    if "edge" in tags and "edge_loopback" not in tags:
                        for tag in tags:
                            if tag.startswith("edge_from_"):
                                from_node = tag[10:]
                            if tag.startswith("edge_to_"):
                                to_node = tag[8:]

                        fx1, fy1, fx2, fy2 = self.__canvas.coords(f"node_{from_node}")
                        fcx, fcy = (fx1 + fx2) / 2, (fy1 + fy2) / 2
                        tx1, ty1, tx2, ty2 = self.__canvas.coords(f"node_{to_node}")
                        tcx, tcy = (tx1 + tx2) / 2, (ty1 + ty2) / 2
                        self.__canvas.coords(id, fcx, fcy, tcx, tcy)
                        self.__canvas.tag_lower(id, 1)

                self.__current = (event.x, event.y)

            elif operation == "Edges":
                assert len(self.__selected) != 0
                loopback = next(
                    tagOrId
                    for tagOrId in self.__selected
                    for tag in self.__canvas.gettags(tagOrId)
                    if tag == "edge_loopback"
                )

                node = next(
                    tagOrId
                    for tagOrId in self.__selected
                    for tag in self.__canvas.gettags(tagOrId)
                    if tag == "node"
                )
                nx1, ny1, nx2, ny2 = self.__canvas.coords(node)
                ncx, ncy = (nx1 + nx2) / 2, (ny1 + ny2) / 2

                rotation = event.x - self.__current[0]
                self.__rotate_object(loopback, (ncx, ncy), -rotation)
                self.__current = (event.x, event.y)

    def __double_click(self, event):
        """
        On a double (left) click event, the user is choosing to edit the current item - whatever that may be.

        If editing "Nodes" then always assume they've meant to change the pair that is associated with the lowest id
        clicked.

        If editing "Edges" then there should only be one id returned.
        """
        operation = StateModel().get_operation()
        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(
                event.x - NODE_RADIUS,
                event.y - NODE_RADIUS,
                event.x + NODE_RADIUS,
                event.y + NODE_RADIUS,
            )

            if len(possible) != 0:
                selected = self.__find_associated_ids(possible)

                for id in selected:
                    for tag in self.__canvas.gettags(id):
                        # there may be multiple hits, but the one we want to use has two tags, one is the generic
                        # "node", the other contains the text we need...
                        if tag.startswith("nodetext_"):
                            new_name = rename_dialog(
                                self, "Rename Node", tag[tag.index("_") + 1 :]
                            )
                            if new_name is not None:
                                self.__canvas.dchars(id, 0, "end")
                                self.__canvas.insert(id, tk.INSERT, new_name)

    def __right_double_click(self, event):
        """
        On a double (right) click event, the user is choosing to delete the current item - whatever that may be.

        If deleting "Nodes" then always assume they've meant to remove the circle and text that is associated with the
        id clicked, along with any edges that link to it.

        If deleting "Edges" then there should only be one id returned - just remove that one.
        """
        operation = StateModel().get_operation()
        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(
                event.x - NODE_RADIUS,
                event.y - NODE_RADIUS,
                event.x + NODE_RADIUS,
                event.y + NODE_RADIUS,
            )

            if len(possible) != 0:
                selected = self.__find_associated_ids(possible)
                for id in selected:
                    for tag in self.__canvas.gettags(id):
                        # there may be multiple hits, but the one we want to use has two tags, one is the generic
                        # "node", the other contains the text we need...
                        if tag.startswith("node_"):
                            node = tag[tag.index("_") + 1 :]
                            if messagebox.askyesno(
                                message=f"Are you sure you want to delete '{node}'"
                            ):
                                self.__delete_element(node)
                                for id in selected:
                                    self.__canvas.delete(id)

    def __find_associated_by_tag(self, possible, tag):
        for id in possible:
            tags = self.__canvas.gettags(id)
            if "node" in tags:
                node_name = next()
                looking_for = f"{tag}_{node_name}"

            elif "edge" in tags:
                edge_name = next()
                looking_for = f"{tag}_{edge_name}"

            else:
                raise ValueError(f"Unknown object on canvas with tags {tags}")

            if tag in tags:
                return [possible] + filter(
                    lambda id: id != possible, self.__find_associated(looking_for)
                )

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
                            self.__canvas.find_withtag(f"nodetext_{node}")
                        )

                    elif tag.startswith("nodetext_"):
                        node = tag[8:]
                        associated = associated.union(
                            self.__canvas.find_withtag(f"node_{node}")
                        )

                associated = associated.union(
                    self.__canvas.find_withtag(f"edge_{node}")
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
                            self.__canvas.find_withtag(f"nodetext_{node}")
                        )

            elif "edge" in tags:
                pass

            else:
                raise ValueError(f"Unknown object on canvas with tags {tags}")

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
            points, width=2, fill="", outline="black", smooth=True, tags=tags
        )

    ###
    # Rotation script adapted from
    # https://wiki.tcl-lang.org/page/Canvas+Rotation
    #
    def __rotate_object(self, tagOrId, origin, angle):
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
