import itertools


class ChangedEntry:

    id_iter = itertools.count()

    def __init__(self, applied_function: str, column: str, row_index: int, value_before: str, value_after: str):
        self.id: int = next(self.id_iter)
        self.applied_function: str = applied_function
        self.column: str = column
        self.row_index: int = row_index
        self.value_before: str = value_before
        self.value_after: str = value_after


class ChangeLog:

    def __init__(self):
        self.entries: list[ChangedEntry] = []

    def add_entry(self, entry: ChangedEntry):
        self.entries.append(entry)

    def pretty_print(self):
        for entry in self.entries:
            print(f'[{entry.id}] {entry.applied_function}: '
                  f'{entry.column}[{entry.row_index}] | '
                  f'{entry.value_before} -> {entry.value_after}')
