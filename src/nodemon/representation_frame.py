import ttkbootstrap as ttk
import ttkbootstrap.constants as tk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import Tableview

from .state_model import StateModel


class RepresentationFrame(ttk.Frame):
    def __init__(self, parent, canvas_frame):
        super().__init__(parent)
        self.__canvas_frame = canvas_frame
        self.__adjacency_matrix = None

        self.__scroll = ScrolledFrame(self)
        self.__scroll.hide_scrollbars()
        self.__scroll.grid(sticky=tk.NSEW)

        self.__scroll.columnconfigure(0, weight=1)
        self.__scroll.rowconfigure(0, weight=1)

        self.__adjacency_matrix = None
        ttk.Style().configure("half_height.TLabel")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.bind(
            "<Expose>",
            lambda event: self.update_table(),
        )

    def update_table(self):
        StateModel().set_current_tab(self.__class__.__name__)

        if self.__adjacency_matrix:
            self.__adjacency_matrix.destroy()
            self.__adjacency_matrix = None
        
        columns, rows, height = self.__generate_table_data()
        if height is not None:
            # columns, rows, height = self.__generate_table_data()
            self.__adjacency_matrix = ttk.Frame(master=self.__scroll, bootstyle=tk.PRIMARY)
            self.__adjacency_matrix.grid(sticky=tk.NSEW)

            column_headings = []
            column_headings.append(ttk.Button(master=self.__adjacency_matrix, text=" ", bootstyle=tk.LINK, state=tk.DISABLED))
            column_headings[-1].grid(sticky=tk.NSEW)
            for index, column in enumerate(columns):
                column_headings.append(
                    ttk.Button(
                        master=self.__adjacency_matrix,
                        text=column, bootstyle=tk.PRIMARY
                    ))
                column_headings[-1].grid(sticky=tk.NSEW, row=index+1, column=0)
            column_headings.append(ttk.Label(master=self.__adjacency_matrix, text=" ", style="half_height.TLabel"))
            column_headings[-1].grid(sticky=tk.NSEW)

            tableview = Tableview(
                master=self.__adjacency_matrix,
                coldata=columns,
                rowdata=rows,
                height=height,
                autofit=True,
                autoalign=False,
                paginated=False,
                searchable=False,
                # disable_right_click=True,
                bootstyle=tk.PRIMARY,
            )
            tableview.grid(sticky=tk.NSEW, row=0, column=1, rowspan=len(rows)+2)

            self.__adjacency_matrix.columnconfigure(1, weight=1)
            self.__adjacency_matrix.rowconfigure([n for n in range(len(rows)+1)], weight=1)

            column_headings[0].update()
            height = column_headings[0].winfo_height()

            style = ttk.Style()
            style.map("Treeview", rowheight=[("!disabled", height)])
            style.map("Treeview.Heading", rowheight=[("!disabled", height)])
            style.map("half_height.TLabel", rowheight=[("!disabled", height // 2)])

    def __generate_table_data(self):
        internal_matrix = StateModel().get_graph_matrix()

        if len(internal_matrix[0]) == 0:
            return (None, None, None)

        column_headings = internal_matrix[0]
        row_values = [
            [value if value else "-" for value in row]
            for col, row in enumerate(internal_matrix[1:])
        ]

        return column_headings, row_values, len(row_values)
