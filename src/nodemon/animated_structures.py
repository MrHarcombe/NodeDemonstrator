from collections import defaultdict
from heapq import heappush, heappop

from .structures import MatrixGraph

###
#
# iterative tree traversal algorithms adapted from the work at
# https://www.enjoyalgorithms.com/blog/iterative-binary-tree-traversals-using-stack
#


class AnimatedMatrixGraph(MatrixGraph):
    """provides overrides of traversal methods that can be used to pause and/or step through the methods as required,
    as well as methods to detect whether this graph qualifies as a tree, to provide those algorithms for display
    """

    def is_tree(self):
        return (
            self.undirected and self.__is_fully_connected() and not self.__is_cyclic()
        )

    def __is_fully_connected(self):
        connected = True

        if len(self) > 0:
            nodes = sum([1 for node in self.breadth_first(self.matrix[0][0])]) - 1
            # print(nodes, "vs", len(self))
            connected = len(self) == nodes

        return connected

    def __is_cyclic(self):
        cyclic = False

        if len(self) > 0:
            start_node = self.matrix[0][0]

            visited = []
            queue = [(start_node, None)]

            while len(queue) > 0 and not cyclic:
                current, previous = queue.pop(0)
                visited.append(current)

                for node, weight in self.get_connections(current):
                    if node not in visited:
                        queue.append((node, current))
                    elif node != previous:
                        cyclic = True

        return cyclic

    def depth_first(self, start_node, end_node=None):
        if start_node in self.matrix[0]:
            discovered = set([start_node])
            visited = []
            stack = [start_node]

            yield (start_node, visited, stack)

            while len(stack) > 0:
                current = stack.pop()
                visited.append(current)

                if current == end_node:
                    yield ("", visited, stack)
                    break

                else:
                    for node, weight in self.get_connections(current):
                        if node not in discovered:
                            discovered.add(node)
                            stack.append(node)

                    yield (current, visited, stack)

        return None

    def breadth_first(self, start_node, end_node=None):
        if start_node in self.matrix[0]:
            discovered = set([start_node])
            visited = []
            queue = [start_node]

            yield (start_node, visited, queue)

            while len(queue) > 0:
                current = queue.pop(0)
                visited.append(current)

                if current == end_node:
                    yield ("", visited, queue)
                    break

                else:
                    for node, weight in self.get_connections(current):
                        if node not in discovered:
                            discovered.add(node)
                            queue.append(node)

                    yield (current, visited, queue)

        return None

    def pre_order(self, start_node, end_node=None):
        if start_node in self.matrix[0]:
            stack = []
            processed = []
            current = start_node

            yield (current, processed, [])

            while len(stack) > 0 or current is not None:
                if current is not None and current == end_node:
                    yield (current, processed, [])
                    break

                if current is not None:
                    processed.append(current)

                    # of any/all children, assume the first one is "left" and others are "right"
                    children = [
                        child
                        for (child, _) in self.get_connections(current)
                        if child not in processed
                    ]
                    if len(children) > 0:
                        current = children.pop(0)
                        stack += children[::-1]
                    else:
                        current = None

                    yield (current, processed, [])

                else:
                    current = stack.pop()
                    yield (current, processed, [])

    def in_order(self, start_node, end_node=None):
        if start_node in self.matrix[0]:
            stack = []
            processed = []
            visited = []
            current = start_node

            yield (current, processed, [])

            while len(stack) > 0 or current is not None:
                if current is not None and current == end_node:
                    yield (current, processed, [])
                    break

                if current is not None:
                    stack.append(current)
                    visited.append(current)

                    # of any/all children, assume the first one is "left" and others are "right"
                    children = [
                        child
                        for (child, _) in self.get_connections(current)
                        if child not in visited
                    ]
                    if len(children) > 0:
                        current = children.pop(0)
                    else:
                        current = None

                    yield (current, processed, [])

                else:
                    current = stack.pop()
                    processed.append(current)

                    # of any/all children, assume the first one is "left" and others are "right"
                    children = [
                        child
                        for (child, _) in self.get_connections(current)
                        if child not in visited
                    ]
                    if len(children) > 0:
                        current = children.pop(0)
                        stack += children
                    else:
                        current = None

                    yield (current, processed, [])

    def post_order(self, start_node, end_node=None):
        if start_node in self.matrix[0]:
            stack = []
            processed = []
            visited = []
            current = start_node

            yield (current, processed, [])

            while len(stack) > 0 or current is not None:
                if current is not None and current == end_node:
                    yield (current, processed, [])
                    break

                if current is not None:
                    if current in visited:
                        processed.append(current)
                        current = None

                        yield (current, processed, [])

                    else:
                        stack.append(current)
                        visited.append(current)

                        # of any/all children, assume the first one is "left" and others are "right"
                        children = [
                            child
                            for (child, _) in self.get_connections(current)
                            if child not in visited
                        ]
                        if len(children) > 0:
                            current = children.pop(0)
                            stack += children[::-1]
                        else:
                            current = None

                        yield (current, processed, [])

                else:
                    current = stack.pop()
                    yield (current, processed, [])


class AnimatedWeightedMatrixGraph(AnimatedMatrixGraph):
    """a weighted, (maybe) directional graph, with optimisation methods that can be used to pause and/or step through
    the methods as required"""

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
        """
        Implements the standard Dijkstra shortest path algorithm. If no end node is given, then all nodes are
        exhaustively explored according to the rules of the algorithm; if an end node is provided then the algorithm
        will end as soon as that node is encountered as the shortest path will have been found (as at each stage the
        shortest unexplored path will have been chosen, as a heapq implementation is used to ensure time-efficient
        ordering).

        Args:
            start_node (string): node to be used as the starting point for the path finding
            end_node (string, optional): node to be used as a target / end point for the path finding. Defaults to None.

        Returns:
            _type_: Path, in order from start to end node (if an end node was given); or a list of tuples containing
            the cost of travelling from the start node to that node (if no end node was given).

        Yields:
            _type_: at the beginning of each iteration through the algorithm, a tuple containing the current node, the
            state of visited nodes, and heapq of nodes to be processed.
        """
        queue = []
        data = defaultdict(lambda: [float("inf"), None])
        data[start_node] = [0, None]

        heappush(queue, (0, start_node))
        yield start_node, data, queue

        while len(queue) > 0:
            current_cost, current_node = heappop(queue)

            if current_node == end_node:
                break

            else:
                for neighbour, cost in self.get_connections(current_node):
                    previous_cost, _ = data[neighbour]
                    if current_cost + cost < previous_cost:
                        data[neighbour][0] = current_cost + cost
                        data[neighbour][1] = current_node
                        heappush(queue, (data[neighbour][0], neighbour))

                yield current_node, data, queue

        if end_node is None:
            yield "", data, []

        else:
            path = []
            current = end_node
            while current != start_node:
                path.append(current)
                current = data[current][1]
            path.append(current)
            yield "", data, path[::-1]

    def astar_manhattan_distance(node_from, node_to):
        return sum(abs(val1 - val2) for val1, val2 in zip(node_from, node_to))

    def reconstruct_astar_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.insert(0, current)
        return total_path

    def astar(self, start_node, end_node, func):
        """
        Implements the standard A* shortest path algorithm. Nodes are explored according to the rules of the
        algorithm, using the given heuristic

        Args:
            start_node (string): node to be used as the starting point for the path finding.
            end_node (string): node to be used as a target / end point for the path finding.
            func (function): heuristic function used to estimate the cost of travelling from the current node to the
            end node.

        Returns:
            _type_: Calculated costs of travelling from start to end node, with interim calculations. Use the
            separate function 'reconstruct_astar_path' to build the full path, if required.

        Yields:
            _type_: at the beginning of each iteration through the algorithm, a tuple containing the current node, the
            state of visited nodes, and heapq of nodes to be processed.
        """
        open_set = []
        came_from = {}

        g_score = defaultdict(lambda: float("inf"))
        g_score[start_node] = 0

        f_score = defaultdict(lambda: float("inf"))
        f_score[start_node] = func(start_node, end_node)

        heappush(open_set, (f_score[start_node], start_node))
        yield start_node, (f_score, g_score, came_from), open_set

        while len(open_set) > 0:
            _, current = heappop(open_set)

            if current == end_node:
                yield (
                    "",
                    (f_score, g_score, came_from),
                    self.reconstruct_astar_path(came_from, current),
                )
                break

            else:
                for neighbour, cost in self.get_connections(current):
                    tentative_g_score = g_score[current] + cost
                    if tentative_g_score < g_score[neighbour]:
                        came_from[neighbour] = current
                        g_score[neighbour] = tentative_g_score
                        neighbour_f_score = tentative_g_score + func(
                            neighbour, end_node
                        )
                        f_score[neighbour] = neighbour_f_score
                        if neighbour not in open_set:
                            heappush(open_set, (neighbour_f_score, neighbour))

                yield current, (f_score, g_score, came_from), open_set


if __name__ == "__main__":

    def test_animated_matrix_graph():
        print("Testing animated adjacency matrix...")
        g = AnimatedMatrixGraph(True)
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g.add_node("D")
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")
        g.add_edge("C", "D")
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

        for step in g.depth_first("A"):
            if isinstance(step, tuple):
                current, visited, stack = step
                print(
                    "currently at:",
                    current,
                    "; visited:",
                    ",".join(visited),
                    "; waiting:",
                    ",".join(stack),
                )
            else:
                print("depth first from A:", ",".join(step))

        for step in g.breadth_first("A"):
            if isinstance(step, tuple):
                current, visited, queue = step
                print(
                    "currently at:",
                    current,
                    "; visited:",
                    ",".join(visited),
                    "; waiting:",
                    ",".join(queue),
                )
            else:
                print("breadth first from A:", ",".join(step))
        print("...done")

    def test_animated_weighted_matrix_graph():
        print("Testing animated weighted adjacency matrix...")
        g = AnimatedWeightedMatrixGraph(True)
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g.add_node("D")
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")
        g.add_edge("C", "D")
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

        for step in g.dijkstra("A"):
            if isinstance(step, tuple):
                current, data, queue = step
                print(
                    "currently at:",
                    current,
                    "; processed:",
                    " / ".join(f"{k}: {v}" for k, v in data.items()),
                    "; waiting:",
                    " / ".join(f"{c}: {n}" for c, n, in queue),
                )

    def test_tree_detection():
        print("Testing animated weighted adjacency matrix tree detection...")
        g = AnimatedWeightedMatrixGraph(True)
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g.add_node("D")
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")
        print("Cyclic:", g.is_cyclic())
        print("Tree:", g.is_tree())

    # test_animated_weighted_matrix_graph()
    test_tree_detection()
