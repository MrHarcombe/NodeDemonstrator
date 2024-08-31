# Node Demonstrator

Building a drag and drop desktop (Tkinter) application to help visualise various graph algorithms.

## Current progress

- drag and drop interface to build a graph 
  - can be weighted or unweighted
  - in "node" mode... 
    - drag to move a node and associated edges
    - double-click to rename nodes, if the default names aren't sufficient
    - double-right click to delete a node
  - in "edge" mode... 
    - drag to rotate a loopback edge out of the way
    - double-click to change the weight of an edge
    - double-right click to delete an edge
- choice of stepped or timed trace of supported algorithms
- available algorithms 
  - breadth-first / depth-first from a given start point (with or without end point, ie traversal and/or search)
  - Dijkstra and A* shortest path

## Usage

- Currently, this project uses the tweaked version of CustomTkinter that needs to be obtained directly from [here](https://github.com/DerSchinken/CustomTkinter/tree/fix-1419) until the [submitted PR](https://github.com/TomSchimansky/CustomTkinter/pull/2240) is approved into the main project.
- To run, install package then launch with "python -m nodemon"

## Future algorithm support

- Kruskal's and Prim's minimum spanning trees
- Other algorithms from [here](https://memgraph.com/blog/graph-algorithms-applications), or [here](https://memgraph.com/blog/graph-algorithms-list) or [here](https://towardsdatascience.com/10-graph-algorithms-visually-explained-e57faa1336f3)?
- Any other suggestions?