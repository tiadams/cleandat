import itertools

class ChangedEntry:

    id_iter = itertools.count()

    def __init__(self, applied_function: str, column: str, row_index: int, value_before: str, value_after: str):
        self.id = next(self.id_iter)
        self.applied_function = applied_function
        self.column = column
        self.row_index = row_index
        self.value_before = value_before
        self.value_after = value_after
