from abc import abstractmethod
from collections import defaultdict
from heapq import heappush, heappop
from time import time


class TreeNode:
    """Simple, open, class for use in a binary search tree. Stores a given value, and
    references to parent, left and right children. Traversal methods pass in the whole
    node and allow access to all attributes."""

    def __init__(self, value):
        self.value = value
        self.parent = None
        self.left = None
        self.right = None

    def pre_traverse(self, op):
        op(self)
        if self.left is not None:
            self.left.pre_traverse(op)
        if self.right is not None:
            self.right.pre_traverse(op)

    def in_traverse(self, op):
        if self.left is not None:
            self.left.in_traverse(op)
        op(self)
        if self.right is not None:
            self.right.in_traverse(op)

    def post_traverse(self, op):
        if self.left is not None:
            self.left.post_traverse(op)
        if self.right is not None:
            self.right.post_traverse(op)
        op(self)

    def __str__(self):
        return
        f"TreeNode({self.value}, "
        f"{'Root' if self.parent is None else 'HasParent'}, "
        f"{'NoLeft' if self.left is None else 'HasLeft'}, "
        f"{'NoRight' if self.right is None else 'HasRight'})"


class RedBlackNode(TreeNode):
    """Extends TreeNode for use in a RedBlackTree, adds an attribute to store the colour
    of the node; True if the node is black, False if the node is red."""

    def __init__(self, value, parent):
        super().__init__(value)
        self.parent = parent
        self.is_black = False

    def __str__(self):
        return
        f"RedBlackNode({self.value}, "
        f"{'Black' if self.is_black else 'Red'}, "
        f"{'Root' if self.parent is None else 'HasParent'}, "
        f"{'NoLeft' if self.left is None else 'HasLeft'}, "
        f"{'NoRight' if self.right is None else 'HasRight'})"

    @staticmethod
    def is_right_child(node):
        """Returns True if the node is a right child of its parent, False otherwise."""
        return node.parent is not None and node == node.parent.right


class Tree:
    """Vanilla binary search tree implementation. Only provides checks for empty and
    presence. Addition and standard traversal methods are also provided, no delete."""

    def __init__(self):
        self.root = None

    def is_empty(self):
        return self.root is None

    def _insert(self, value: object, parent: TreeNode, on_right: bool):
        new_node = TreeNode(value)

        if parent is None:
            self.root = new_node

        elif on_right:
            parent.right = new_node
            new_node.parent = parent

        else:
            parent.left = new_node
            new_node.parent = parent

    def add(self, value: object):
        if self.is_empty():
            self._insert(value, None, True)

        else:
            current = self.root
            looking = True
            while looking:
                if value < current.value:
                    if current.left is None:
                        self._insert(value, current, False)
                        looking = False
                    else:
                        current = current.left

                else:
                    if current.right is None:
                        self._insert(value, current, True)
                        looking = False
                    else:
                        current = current.right

    @abstractmethod
    def _delete(self, candidate: TreeNode):
        pass

    def remove(self, value: object):
        if self.is_empty():
            return

        else:
            current = self.root
            looking = True
            while looking:
                if value == current.value:
                    self._delete(current)

                elif value < current.value:
                    if current.left is None:
                        return
                    else:
                        current = current.left

                elif value > current.value:
                    if current.right is None:
                        return
                    else:
                        current = current.right

    def contains(self, value):
        return value in self

    def __contains__(self, value):
        found = False

        if not self.is_empty():
            current = self.root
            looking = True
            while looking:
                if value == current.value:
                    found = True
                    looking = False

                elif value < current.value:
                    if current.left is None:
                        looking = False
                    else:
                        current = current.left

                else:
                    if current.right is None:
                        looking = False
                    else:
                        current = current.right

        return found

    def pre_traverse(self, op):
        if not self.is_empty():
            self.root.pre_traverse(op)

    def in_traverse(self, op):
        if not self.is_empty():
            self.root.in_traverse(op)

    def post_traverse(self, op):
        if not self.is_empty():
            self.root.post_traverse(op)


class RedBlackTree(Tree):
    """Implementation of the RedBlackTree detailed on Wikipedia as a child class of the
    binary search tree implemented above (see https://en.wikipedia.org/wiki/Red%E2%80%93black_tree).
    """

    def __init__(self):
        super().__init__()

    def __rotate_subtree(self, parent, direction):
        """Rotates the subtree (which may be the root of the tree) in the given direction
        (True -> right, False -> left)."""
        grandparent = parent.parent
        sibling = parent.left if direction else parent.right
        assert sibling is not None
        child = sibling.right if direction else sibling.left

        if direction:
            parent.left = child
            sibling.right = parent
        else:
            parent.right = child
            sibling.left = parent

        if child is not None:
            child.parent = parent

        parent.parent = sibling
        sibling.parent = grandparent

        if grandparent is not None:
            if parent == grandparent.right:
                grandparent.right = sibling
            else:
                grandparent.left = sibling
        else:
            self.root = sibling

        return sibling

    def _insert(self, value, parent, on_right):
        node = RedBlackNode(value, parent)

        if parent is None:
            self.root = node
            return

        if on_right:
            parent.right = node
        else:
            parent.left = node

        # start of the (do while)-loop:
        while True:
            if parent.is_black:
                # Case_I1 (P is black):
                return  # insertion complete

            # From now on P is red.
            grandparent = parent.parent
            if grandparent is None:
                # P is red and root
                # goto Case_I4
                parent.is_black = True
                return

            # else: P red and G!=NULL.
            on_right = RedBlackNode.is_right_child(
                parent
            )  # the side of parent G on which node P is located
            uncle = grandparent.left if on_right else grandparent.right
            if uncle is None or uncle.is_black:  # considered black
                # P is red && U is black
                # goto Case_I56
                if node == (parent.left if on_right else parent.right):
                    # Case_I5 (P is red && U is black && N is inner grandchild of G):
                    self.__rotate_subtree(parent, on_right)  # P is never the root
                    node = parent  # new current node
                    parent = (
                        grandparent.right if on_right else grandparent.left
                    )  # new parent of N
                    # fall through to Case_I6

                # Case_I6 (P is red && U is black && N is outer grandchild of G):
                self.__rotate_subtree(grandparent, not on_right)  # G may be the root
                parent.is_black = True
                grandparent.is_black = False
                return  # insertion complete

            # Case_I2 (P+U red):
            parent.is_black = True
            uncle.is_black = True
            grandparent.is_black = False
            node = grandparent  # new current node
            # iterate 1 black level higher
            #     (= 2 tree levels)

            parent = node.parent
            if parent is None:
                break
        # end of the (do while)-loop


"""
        def _delete(self, candidate : RedBlackNode):
                # need to add the simple cases first, before proceeding

                parent = candidate.parent # -> parent node of N
                on_right = RedBlackNode.is_right_child(candidate) # side of P on which N is located (∈ { LEFT, RIGHT })
                # -> sibling of N
                # -> close     nephew
                # -> distant nephew

                # P != NULL, since N is not the root.
                # Replace N at its parent P by NIL:
                P->child[dir] = NIL;
                goto Start_D;            // jump into the loop

                # start of the (do while)-loop:
                while True:
                        dir = childDir(N);     // side of parent P on which node N is located
                        Start_D:
                        S = P->child[1-dir]; // sibling of N (has black height >= 1)
                        D = S->child[1-dir]; // distant nephew
                        C = S->child[    dir]; // close     nephew
                        if (S->color == RED)
                                goto Case_D3;                                    // S red ===> P+C+D black
                        // S is black:
                        if (D != NIL && D->color == RED) // not considered black
                                goto Case_D6;                                    // D red && S black
                        if (C != NIL && C->color == RED) // not considered black
                                goto Case_D5;                                    // C red && S+D black
                        // Here both nephews are == NIL (first iteration) or black (later).
                        if (P->color == RED)
                                goto Case_D4;                                    // P red && C+S+D black

                        // Case_D1 (P == NULL):
                        return; // deletion complete

                        // Case_D2 (P+C+S+D black):
                        S->color = RED;
                        N = P; // new current node (maybe the root)
                        // iterate 1 black level
                        //     (= 1 tree level) higher

                        parent = candidate.parent
                        if parent is None:
                                break
                # end of the (do while)-loop
"""


class ListGraph:

    class ListGraphNode:

        def __init__(self, node):
            self.node = node
            self.paths = []

        def add_edge(self, to):
            if to not in self.paths:
                self.paths.append(to)

        def is_connected(self, to):
            return to in self.paths

        def __str__(self):
            return f"ListGraphNode(node: {self.node}, paths: {', '.join(self.paths)})"

    def __init__(self):
        self.nodes = []

    def contains(self, value):
        return value in self

    def __contains__(self, value):
        for n in self.nodes:
            if n.node == value:
                return True
        return False

    def add_node(self, node):
        if node not in self:
            self.nodes.append(ListGraph.ListGraphNode(node))

    def delete_node(self, node):
        if node in self:
            # remove the node itself
            for n in range(len(self.nodes)):
                if self.nodes[n].node == node:
                    break
            del self.nodes[n]
            # remove references to the node
            for n in self.nodes:
                if node in n.paths:
                    n.paths.remove(node)

    def add_edge(self, from_node, to_node):
        if from_node in self and to_node in self:
            for n in self.nodes:
                if n.node == from_node:
                    n.add_edge(to_node)
                elif n.node == to_node:
                    n.add_edge(from_node)

    def is_connected(self, from_node, to_node):
        if from_node in self and to_node in self:
            for n in self.nodes:
                if n.node == from_node:
                    return n.is_connected(to_node)
        return False


class MatrixGraph:
    """an unweighted, (maybe) directional graph"""

    def __init__(self, undirected=False):
        self.matrix = [[]]
        self.undirected = undirected

    def is_empty(self):
        return len(self.matrix[0]) == 0

    def __len__(self):
        return len(self.matrix[0])

    def contains(self, node):
        return node in self.matrix[0]

    def __contains__(self, node):
        return self.contains(node)

    def add_node(self, node):
        if node not in self.matrix[0]:
            self.matrix[0].append(node)
            for n in range(1, len(self.matrix)):
                self.matrix[n].append(False)
            self.matrix.append([False for n in range(len(self.matrix[0]))])

    def delete_node(self, node):
        if node in self.matrix[0]:
            index = self.matrix[0].index(node)
            del self.matrix[0][index]
            del self.matrix[index]
            for n in range(1, len(self.matrix)):
                del self.matrix[n][index]

    def add_edge(self, from_node, to_node, undirected=False):
        if from_node not in self.matrix[0]:
            self.add_node(from_node)
        if to_node not in self.matrix[0]:
            self.add_node(to_node)
        if not self.is_connected(from_node, to_node):
            from_index = self.matrix[0].index(from_node)
            to_index = self.matrix[0].index(to_node)
            self.matrix[from_index + 1][to_index] = True
            self.matrix[to_index + 1][from_index] = True
            if self.undirected or undirected:
                self.matrix[to_index + 1][from_index] = True

    def delete_edge(self, from_node, to_node, undirected=False):
        if self.is_connected(from_node, to_node):
            from_index = self.matrix[0].index(from_node)
            to_index = self.matrix[0].index(to_node)
            self.matrix[from_index + 1][to_index] = False
            if self.undirected or undirected:
                self.matrix[to_index + 1][from_index] = False

    def is_connected(self, from_node, to_node):
        if from_node in self.matrix[0] and to_node in self.matrix[0]:
            from_index = self.matrix[0].index(from_node)
            to_index = self.matrix[0].index(to_node)
            return self.matrix[from_index + 1][to_index]
        return False

    def get_connections(self, node):
        if node in self.matrix[0]:
            return iter(
                [
                    c
                    for c in zip(
                        self.matrix[0], self.matrix[self.matrix[0].index(node) + 1]
                    )
                    if c[1]
                ]
            )
        return []

    def depth_first(self, start_node, end_node=None):
        if start_node in self.matrix[0]:
            discovered = set([start_node])
            visited = []
            stack = [start_node]

            while len(stack) > 0:
                current = stack.pop()
                visited.append(current)

                if current == end_node:
                    break

                for node, weight in self.get_connections(current):
                    if node not in discovered:
                        discovered.add(node)
                        stack.append(node)
            return visited
        return None

    def breadth_first(self, start_node, end_node=None):
        if start_node in self.matrix[0]:
            discovered = set([start_node])
            visited = []
            queue = [start_node]

            while len(queue) > 0:
                current = queue.pop(0)
                visited.append(current)

                if current == end_node:
                    break

                for node, weight in self.get_connections(current):
                    if node not in discovered:
                        discovered.add(node)
                        queue.append(node)
            return visited
        return None


class WeightedMatrixGraph(MatrixGraph):
    """a weighted, (maybe) directional graph"""

    def __init__(self, undirected=False):
        super().__init__(undirected)

    def add_edge(self, from_node, to_node, weight=1, undirected=False):
        """
        Adds an edge from one node to another; re-add to update the edge

        Args:
            from_node (string): Name of the node at one end of the edge
            to_node (string): Name of the node at the other end of the edge
            weight (int, optional): Cost of travelling the edge. Defaults to 1.
            undirected (bool, optional): If True, will create the matching edge in reverse. Defaults to False.
        """
        if from_node in self.matrix[0] and to_node in self.matrix[0]:
            from_index = self.matrix[0].index(from_node)
            to_index = self.matrix[0].index(to_node)
            self.matrix[from_index + 1][to_index] = weight
            if self.undirected or undirected:
                self.matrix[to_index + 1][from_index] = weight

    def dijkstra(self, start_node, end_node=None):
        queue = []
        data = defaultdict(lambda: [float("inf"), None])
        data[start_node] = [0, None]

        heappush(queue, (0, start_node))

        while len(queue) > 0:
            current_cost, current_node = heappop(queue)

            if current_node == end_node:
                break

            for neighbour, cost in self.get_connections(current_node):
                previous_cost, _ = data[neighbour]
                if current_cost + cost < previous_cost:
                    data[neighbour][0] = current_cost + cost
                    data[neighbour][1] = current_node
                    heappush(queue, (data[neighbour][0], neighbour))

        if end_node is None:
            return data.items()

        path = []
        current = end_node
        while current != start_node:
            path.append(current)
            current = data[current][1]
        path.append(current)
        return path[::-1]

    def astar_manhattan_distance(node_from, node_to):
        return sum(abs(val1 - val2) for val1, val2 in zip(node_from, node_to))

    def reconstruct_astar_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.insert(0, current)
        return total_path

    def astar(self, start_node, end_node, func):
        open_set = []
        came_from = {}

        g_score = defaultdict(lambda: float("inf"))
        g_score[start_node] = 0

        f_score = defaultdict(lambda: float("inf"))
        f_score[start_node] = func(start_node, end_node)

        heappush(open_set, (f_score[start_node], start_node))

        while len(open_set) > 0:
            _, current = heappop(open_set)

            if current == end_node:
                return came_from

            for friend, cost in self.get_connections(current):
                tentative_g_score = g_score[current] + cost
                if tentative_g_score < g_score[friend]:
                    came_from[friend] = current
                    g_score[friend] = tentative_g_score
                    friend_f_score = tentative_g_score + func(friend, end_node)
                    f_score[friend] = friend_f_score
                    if friend not in open_set:
                        heappush(open_set, (friend_f_score, friend))


if __name__ == "__main__":

    def test_tree():
        print("Testing tree...")
        t = Tree()
        for n in (7, 4, 2, 6, 16, 12, 19):
            t.add(n)
        assert 12 in t
        assert 13 not in t
        t.add(10)
        assert 10 in t

        tree = []
        print("Pre-order traversal:")
        t.pre_traverse(lambda n: tree.append(str(n.value)))
        print(", ".join(tree))

        tree = []
        print("In-order traversal:")
        t.in_traverse(lambda n: tree.append(str(n.value)))
        print(", ".join(tree))

        tree = []
        print("Post-order traversal:")
        t.post_traverse(lambda n: tree.append(str(n.value)))
        print(", ".join(tree))

        print("Tree.Root:", str(t.root))
        print("...done")

    def test_red_black_tree():
        print("Testing red-black tree...")
        t = RedBlackTree()
        for n in range(100):
            t.add(n)

        t.pre_traverse(lambda n: print(n.value, end=","))
        print()
        print("...done")

    def test_list_graph():
        print("Testing graph (adjacency list)...")
        g = ListGraph()
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "C")
        print("B" in g)
        print(g.is_connected("A", "B"))
        print(g.is_connected("A", "C"))
        g.add_node("D")
        g.add_edge("B", "D")
        g.add_edge("C", "D")
        g.delete_node("C")
        print("D" in g)
        print("C" in g)
        print(g.is_connected("A", "C"))
        print(g.is_connected("B", "D"))
        print("...done")

    def test_matrix_graph():
        print("Testing graph (adjacency matrix)...")
        g = MatrixGraph(True)
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g.add_node("D")
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")
        g.add_edge("C", "D")
        print("C" in g)
        print(g.is_connected("A", "C"))
        print(g.is_connected("B", "D"))
        g.add_node("E")
        g.add_node("F")
        g.add_node("G")
        g.add_node("H")
        g.add_edge("B", "E")
        g.add_edge("D", "F")
        g.add_edge("D", "G")
        g.add_edge("C", "G")
        g.add_edge("E", "F")
        g.add_edge("F", "H")
        g.add_edge("G", "H")
        print("D" in g)
        print(g.is_connected("D", "F"))

        visited = g.depth_first("A")
        print("depth first from A: ", ",".join(visited))

        visited = g.breadth_first("A")
        print("breadth first from A: ", ",".join(visited))
        print("...done")

    def test_weighted_graph():
        print("Testing graph (adjacency matrix)...")
        g = WeightedMatrixGraph(True)
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g.add_node("D")
        g.add_edge("A", "B", 2)
        g.add_edge("A", "C", 10)
        g.add_edge("B", "D", 3)
        g.add_edge("C", "D", 6)
        print("C" in g)
        print(g.is_connected("A", "C"))
        print(g.is_connected("B", "D"))
        g.add_node("E")
        g.add_node("F")
        g.add_node("G")
        g.add_node("H")
        g.add_edge("B", "E", 9)
        g.add_edge("D", "F", 11)
        g.add_edge("D", "G", 7)
        g.add_edge("C", "G", 8)
        g.add_edge("E", "F", 5)
        g.add_edge("F", "H", 6)
        g.add_edge("G", "H", 1)
        print("D" in g)
        print(g.is_connected("F", "D"))

        print("IsEmpty:", g.is_empty())
        print("Len:", len(g))

        visited = g.depth_first("A")
        print("depth first from A: ", ",".join(visited))

        visited = g.breadth_first("A")
        print("breadth first from A: ", ",".join(visited))

        print("shortest path info from A:", g.dijkstra("A"))

        start = time()
        print("shortest path from A to H:", ",".join(g.dijkstra("A", "H")))
        print("Elapsed:", time() - start)
        start = time()
        print(
            "shortest A* path from A to H:",
            ",".join(
                g.reconstruct_astar_path(
                    g.astar("A", "H", lambda a, b: ord(b) - ord(a) - ord("A")), "H"
                )
            ),
        )
        print("Elapsed:", time() - start)
        print("shortest path from F to C:", ",".join(g.dijkstra("F", "C")))

        print("...done")

    def test_graph_connections():
        g = WeightedMatrixGraph()
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g.add_node("D")
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        for e in g.get_connections("A"):
            print("Connected to", e)
        print(g.matrix)

    # test_red_black_tree()
    test_weighted_graph()
