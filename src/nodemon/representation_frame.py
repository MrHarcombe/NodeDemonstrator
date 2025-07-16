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

        # columns, rows, height = self.__generate_table_data()
        self.__adjacency_matrix = Tableview(
            master=self.__scroll,
            coldata=[],
            rowdata=[[]],
            height=0,
            autofit=True,
            autoalign=False,
            paginated=False,
            searchable=False,
            bootstyle=tk.PRIMARY,
            # stripecolor=("light", None),
        )
        self.__adjacency_matrix.grid(sticky=tk.NSEW)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.bind(
            "<Expose>",
            lambda event: self.update_table(),
        )

    def update_table(self):
        StateModel().set_current_tab(self.__class__.__name__)
        columns, rows, height = self.__generate_table_data()
        if height is not None:
            self.__adjacency_matrix.build_table_data(columns, rows)
            self.__adjacency_matrix.configure(height=height)

    def __generate_table_data(self):
        internal_matrix = StateModel().get_graph_matrix()

        if len(internal_matrix[0]) == 0:
            return (None, None, None)

        column_headings = [""] + internal_matrix[0]
        row_values = [
            [column_headings[col + 1]] + [value if value else "-" for value in row]
            for col, row in enumerate(internal_matrix[1:])
        ]

        return column_headings, row_values, len(row_values)
