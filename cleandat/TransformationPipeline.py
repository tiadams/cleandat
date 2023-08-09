import logging
from typing import Callable

from pandas import DataFrame

from cleandat.ChangedEntry import ChangedEntry


class TransformationPipeline:

    def __init__(self, df: DataFrame):
        self.steps: list[Callable[[DataFrame, list[str]], DataFrame]] = []
        self.changelog: list[ChangedEntry] = []
        self.data: DataFrame = df

    def add_task(self, task: Callable[[DataFrame, list[str]], DataFrame], columns: list[str] = None):
        self.steps.append((task, columns))

    def run(self):
        for task, columns in self.steps:
            before_transformation = self.data.copy()
            logging.info(f'Running task {task} on columns {columns}')
            self.data = task(self.data, columns)
            self._extend_changelog(task, before_transformation, self.data)
        return self.data

    def _extend_changelog(self, transformation_step: Callable, df_before: DataFrame, df_after: DataFrame):
        diff = df_before.compare(df_after)
        different_columns = {x[0] for x in diff.columns}
        for column in different_columns:
            for row_idx in diff[column].index:
                value_before = str(diff[column].loc[row_idx, 'self'])
                value_after = str(diff[column].loc[row_idx, 'other'])
                function_name = transformation_step.__name__
                log_entry = ChangedEntry(function_name, column, row_idx, value_before, value_after)
                self.changelog.append(log_entry)

    def print_changelog(self):
        for entry in self.changelog:
            print(f'[{entry.id}] {entry.applied_function}: {entry.column}[{entry.row_index}] | {entry.value_before} -> {entry.value_after}')
