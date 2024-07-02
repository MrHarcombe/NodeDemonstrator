import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from itertools import chain, product
from string import ascii_uppercase
from structures import MatrixGraph, WeightedMatrixGraph
# from xcanvas import XCanvas

from rename_dialog import rename_dialog

WIDTH=1280
HEIGHT=720

NODE_RADIUS=50


class CanvasFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.__canvas = tk.Canvas(self, width=100, height=100, scrollregion=(0,0,10000,10000))
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

        self.__selected = ()
        self.__current = ()

    def __click(self, event):
        operation = StateModel().get_operation()
        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(event.x - NODE_RADIUS, event.y - NODE_RADIUS, event.x + NODE_RADIUS, event.y + NODE_RADIUS)
            # print(possible)
            
            if len(possible) != 0:
                # print("Might be dragging?")
                self.__selected = sorted(possible)[:2]
                self.__current = (event.x, event.y)
                
            else:
                node_name = StateModel().get_next_node_name()
                StateModel().add_node(node_name)
                # centre = (event.x, event.y)
                self.__canvas.create_oval(event.x - NODE_RADIUS, event.y - NODE_RADIUS, event.x + NODE_RADIUS, event.y + NODE_RADIUS, fill="black", width=0, tags=("node", f"node_{node_name}"))
                self.__canvas.create_text(event.x, event.y, fill="white", text=node_name, tags=("node", f"nodetext_{node_name}"))

    def __release(self, event):
        pass

    def __drag(self, event):
        for id in self.__selected:
            self.__canvas.move(id, event.x - self.__current[0], event.y - self.__current[1])
        self.__current = (event.x, event.y)

    def __double_click(self, event):
        operation = StateModel().get_operation()
        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(event.x - NODE_RADIUS, event.y - NODE_RADIUS, event.x + NODE_RADIUS, event.y + NODE_RADIUS)
            # print(possible)
            
            if len(possible) != 0:
                # print("Might be editing?")
                for p in sorted(possible):
                    if p % 2 == 0:
                        tags = self.__canvas.gettags(p)
                        for tag in tags:
                            if "_" in tag:
                                new_name = rename_dialog(self, "Rename Node", tag[tag.index("_")+1:])
                                if new_name != None:
                                    self.__canvas.dchars(p, 0, "end")
                                    self.__canvas.insert(p, tk.INSERT, new_name)

    def __right_double_click(self, event):
        operation = StateModel().get_operation()
        if operation == "Nodes":
            possible = self.__canvas.find_overlapping(event.x - NODE_RADIUS, event.y - NODE_RADIUS, event.x + NODE_RADIUS, event.y + NODE_RADIUS)
            # print(possible)
            
            if len(possible) != 0:
                # print("Might be deleting?")
                for p in sorted(possible):
                    if p % 2 == 0:
                        tags = self.__canvas.gettags(p)
                        for tag in tags:
                            if "_" in tag:
                                node = tag[tag.index("_")+1:]
                                if messagebox.askyesno(message=f"Are you sure you want to delete '{node}'"):
                                    delete = True
                                    
                if delete:
                    # node = tag[tag.index("_")+1:]
                    self.__delete_element(node)
                    self.__canvas.delete("node_" + node)
                    self.__canvas.delete("nodetext_" + node)


    def __add_element(self):
        # needs to know StateModel.get_operation
        match StateModel().get_operation():
            case "AddNode":
                node_name = StateModel().get_next_node_name()
                StateModel().add_node(node_name)
                # centre = (event.x, event.y)
                self.__canvas.create_oval(event.x - NODE_RADIUS, event.y - NODE_RADIUS, event.x + NODE_RADIUS, event.y + NODE_RADIUS, fill="black", width=0, tags=("node", f"node_{node_name}"))
                self.__canvas.create_text(event.x, event.y, fill="white", text=node_name, tags=("node", f"nodetext_{node_name}"))
            case "AddEdge":
                pass
        

    def __connect_element(self):
        # needs to know StateModel.get_operation
        pass

    def __edit_element(self):
        # needs to know StateModel.get_operation
        pass

    def __delete_element(self, element):
        # needs to know StateModel.get_operation
        pass

    # def save_posn(self, event):
    #     self.lastx, self.lasty = event.x, event.y
    # 
    # def add_line(self, event):
    #     self.__canvas.create_line((self.lastx, self.lasty, event.x, event.y))
    #     self.save_posn(event)


class DrawControlsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.__operation = tk.StringVar(value="Nodes")

        glf = ttk.LabelFrame(self, text="Graph")
        tk.Button(glf, text="New", command=lambda: StateModel().create_new()).grid(sticky=tk.NSEW)
        tk.Button(glf, text="Load", command=lambda: StateModel().load_existing()).grid(sticky=tk.NSEW)
        tk.Button(glf, text="Save", command=lambda: StateModel().save_current()).grid(sticky=tk.NSEW)
        glf.grid(sticky=tk.NSEW)
        glf.columnconfigure(0, weight=1)
        for i in range(3):
            glf.rowconfigure(i, weight=1)
        

        nlf = ttk.LabelFrame(self, text="Work On")
        tk.Radiobutton(nlf, text="Nodes", indicatoron=tk.OFF, variable=self.__operation, value="Nodes", command=self.update_operation).grid(sticky=tk.NSEW)
        tk.Radiobutton(nlf, text="Edges", indicatoron=tk.OFF, variable=self.__operation, value="Edges", command=self.update_operation).grid(sticky=tk.NSEW)
        nlf.grid(sticky=tk.NSEW)
        nlf.columnconfigure(0, weight=1)
        for i in range(2):
            nlf.rowconfigure(i, weight=1)

        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=2)
        self.columnconfigure(0, weight=1)

    def update_operation(self):
        StateModel().set_operation(self.__operation.get())


class UsageControlsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="This will be the graph usage frame").grid()


class ToolFrame(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.__tabs = [
            DrawControlsFrame(self),
            UsageControlsFrame(self)
            ]
        
        self.add(self.__tabs[0], text='Draw')
        self.add(self.__tabs[1], text='Algorithms')


class StateModel:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(StateModel, cls).__new__(cls)

            # Put any initialization here.
            cls.__instance.__graph = WeightedMatrixGraph()
            cls.__instance.__filename = None
            cls.__instance.__operation = "AddNode"
            cls.__instance.__changed = True
            cls.__instance.__generator = StateModel.__next_node_name_generator()
        
        return cls.__instance

    def __next_node_name_generator():
        yield from chain(*[product(ascii_uppercase, repeat=i) for i in range(1, 1_000)])

    def create_new(self):
        # need to check if changed, and if so save the current
        if self.__changed:
            pass
        
        # ask if the graph is to be weighted
        if messagebox.askyesno(message="Will the graph be weighted?") == tk.YES:
            self.__graph = WeightedMatrixGraph()
        else:
            self.__graph = MatrixGraph()
        
        # whatever you created, we've changed (need this to think about saving, later)
        self.__changed = True
    
    def load_existing(self):
        pass
    
    def save_current(self):
        pass
    
    def set_operation(self, operation):
        self.__operation = operation
        
    def get_operation(self):
        return self.__operation

    def get_next_node_name(self):
        return "".join(next(self.__generator))

    def add_node(self, node_name):
        self.__graph.add_node(node_name)


class NodeApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Node Demonstrator")
        self.geometry(f"{WIDTH}x{HEIGHT}+10+10")
        
        self.canvas = CanvasFrame(self).grid(column=0, row=0, sticky=tk.NSEW)
        self.tools = ToolFrame(self).grid(column=1, row=0, sticky=tk.NSEW)

        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)


if __name__ == "__main__":
    app = NodeApplication()
    app.mainloop()
