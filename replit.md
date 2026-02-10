# replit.md

## Overview

Node Demonstrator is a desktop application built with Python and Tkinter (via ttkbootstrap) for visualizing graph algorithms. Users can interactively build graphs through a drag-and-drop canvas interface, then run and step through various graph algorithms with visual feedback. The application supports weighted/unweighted and directed/undirected graphs, with algorithms including BFS, DFS, Dijkstra's shortest path, A* shortest path, tree traversals (pre/in/post order), and Prim's minimum spanning tree.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure

The project follows a Python package structure under `src/nodemon/`. The entry point is `src/nodemon/__main__.py` which calls `main()` in `node_demonstrator.py`, allowing the app to be launched via `python -m nodemon`.

- **`node_demonstrator.py`** — Main application window (`NodeApplication` extends `ttk.Window`). Sets up a horizontal `PanedWindow` with a canvas on the left and a tool notebook on the right.
- **`state_model.py`** — Singleton pattern (via `__new__` override) that holds all graph state. Contains the graph data structure, tracks current mode (nodes/edges), directed/undirected setting, weighted/unweighted setting, filename, and change tracking. Acts as the central data model that all UI components reference.
- **`canvas_frame.py`** — Handles all canvas drawing and mouse interaction (click, drag, double-click for create/move/rename/delete operations). Translates user actions based on current mode (node mode vs edge mode).
- **`tool_frame.py`** — A `ttk.Notebook` with three tabs: Draw (controls), Algorithms (run/step through), and Data (adjacency matrix view).
- **`draw_controls_frame.py`** — New/Load/Save functionality plus toggles for node/edge mode, directed/undirected, and weight settings.
- **`usage_controls_frame.py`** — Algorithm selection and execution controls. Supports both stepped and timed trace modes.
- **`representation_frame.py`** — Displays the adjacency matrix representation of the current graph.

### Graph Data Structures

- **`structures.py`** — Core graph implementations including `MatrixGraph` (adjacency matrix-based graph), `TreeNode`, and `RedBlackNode`. The graph uses an adjacency matrix representation.
- **`animated_structures.py`** — Extends `MatrixGraph` with `AnimatedMatrixGraph` and `AnimatedWeightedMatrixGraph`. These provide iterator-based (yield) versions of traversal algorithms that can be paused/stepped through for visualization. Also includes tree detection (connected + acyclic check).

### Algorithm Visualization

- **`trace_frame.py`** — Abstract base class for all algorithm trace displays. Provides the framework for stepping through algorithm iterations and displaying processed nodes and current data structures.
- **`traversal_frames.py`** — BFS, DFS, and tree traversal visualization frames.
- **`optimisation_frames.py`** — Dijkstra and A* visualization frames.
- **`spanning_frames.py`** — Prim's MST visualization frame.

### Design Patterns

- **Singleton** — `StateModel` ensures a single source of truth for graph state.
- **Iterator/Generator** — Algorithms use Python generators (`yield`) to allow step-by-step execution, enabling both manual stepping and timed auto-play.
- **Observer-like** — Tab switching triggers `<Expose>` events to update the current tab context in StateModel.
- **MVC-ish** — StateModel holds data, canvas_frame handles display, and control frames manage user interaction.

### File I/O

The application supports saving and loading graphs via JSON serialization (previously pickle, now JSON based on imports in `draw_controls_frame.py`).

### UI Framework

Uses `ttkbootstrap` (a themed wrapper around tkinter's ttk) with the "journal" theme. The UI is built with grid geometry management primarily, with some pack usage for scrollbars.

## External Dependencies

- **ttkbootstrap** — Themed Tkinter widget library. Provides modern-looking UI components and the `ttk.Window` base class with theme support. This is the primary UI framework dependency.
- **Python standard library** — `tkinter` (canvas, dialogs, file dialogs), `collections` (defaultdict, namedtuple), `heapq` (priority queues for Dijkstra/A*/Prim's), `json` (file save/load), `math` (geometric calculations for edge drawing), `itertools` and `string` (node name generation), `abc` (abstract base classes).
- **No database** — All data is held in-memory in the singleton StateModel. Persistence is via JSON files on disk.
- **No network/API dependencies** — This is a purely local desktop application.
- **No external graph libraries** — All graph data structures and algorithms are implemented from scratch in `structures.py` and `animated_structures.py`.

### Running the Application

The canonical way to run is `python -m nodemon` from the `src/` directory, or `python src/launch.py`. The root `launch.py` is an alternative launcher that also handles import errors gracefully. Note that this is a GUI application requiring a display environment (Tkinter).

### Playground Directory

`src/playground/` contains experimental/prototype scripts used during development. These are not part of the main application and can be ignored for development purposes.