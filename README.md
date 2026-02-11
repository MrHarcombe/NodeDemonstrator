# Node Demonstrator

Building a drag and drop desktop (Tkinter) application to help visualise various graph algorithms.

## Current progress

- drag and drop interface to build a graph 
  - can be weighted or unweighted
  - in "node" mode...
    - click to create a node
    - drag to move a node and associated edges
    - double-click to rename nodes, if the default names aren't sufficient
    - double-right click to delete a node
  - in "edge" mode...
    - click and drag between nodes to create an edge
    - drag to rotate a loopback edge out of the way
    - double-click to change the weight of an edge
    - double-right click to delete an edge
- choice of stepped or timed trace of supported algorithms
  - available algorithms 
    - breadth-first / depth-first from a given start point (with or without end point, ie traversal and/or search)
    - Dijkstra and A* shortest path
    - Prim's minimum spanning tree
    - tree traversal algorithms (within certain constraints)
- view of the adjacency matrix behind the drawn graph

## Usage

- This project uses the ttkbootstrap library (it should have installed as part of the process - need to add a way to override the theme)
- To run, install package then launch with "python -m nodemon"

## Future algorithm support

- Kruskal's minimum spanning trees
- Other algorithms from [here](https://memgraph.com/blog/graph-algorithms-applications), or [here](https://memgraph.com/blog/graph-algorithms-list) or [here](https://towardsdatascience.com/10-graph-algorithms-visually-explained-e57faa1336f3)?
- Any other suggestions?