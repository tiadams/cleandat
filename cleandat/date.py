import dateparser
import numpy as np
import pandas as pd
from pandas import DataFrame


def identify_date_columns(df: DataFrame, threshold: float = 0.5) -> list:
    """Identifies columns that are likely to contain date entries.

    Heuristic: if a column contains a large number of date entries, it is likely that the column is a date column
    (e.g. a column containing the date of birth of a person).

    :param df: The dataframe to be analyzed
    :param threshold: The percentage of entries that have to be dates for a column to be considered a date column
    :return: A list of column names that are likely to contain date entries
    """
    date_columns = []
    for column in df:
        if df[column].dtype == 'object':
            pro_date_heuristic = 0
            for entry in df[column]:
                if str(entry).isnumeric() or pd.isnull(entry):
                    continue
                else:
                    if dateparser.parse(str(entry)) is not None:
                        # entry can be interpreted as a date
                        pro_date_heuristic += 1
            # take empty cell (nan) values out of the consideration
            num_nan = df[column].isna().sum()
            if pro_date_heuristic > threshold * (len(df[column]) - num_nan):
                date_columns.append(column)
    return date_columns


def create_durational_column(df: DataFrame, date_col_start: str, date_col_end: str, new_col_name: str, remove_dates: bool = True) -> DataFrame:
    """Creates a new column containing the duration between two date columns in days.

    :param df: The dataframe to which the column should be added
    :param date_col_start: The column containing the start date
    :param date_col_end: The column containing the end date
    :param new_col_name: The name of the new column
    :param remove_dates: If True, remove the date columns after the new column has been created
    :return: The dataframe with the new column
    """
    df[new_col_name] = (df[date_col_end] - df[date_col_start]).dt.days
    if remove_dates:
        df.drop([date_col_start, date_col_end], axis=1, inplace=True)
    return df


def normalize_date_entries(df: DataFrame, date_columns: list[str], date_order: str = 'DMY',
                           remove_unparsable=True) -> DataFrame:
    """Replace all date entries with a uniform format.

    Reformat all date entries to a uniform format - dates may be written in different formats,
    e.g. 01.01.2020 or January 1st, 2020

    :param remove_unparsable: If True, replace entries that cannot be parsed as dates with NaN
    :param date_order: The order of the date entries, e.g. DMY for 01.01.2020 or MDY for January 1st, 2020
    :param df: The dataframe to be reformatted
    :param date_columns: List of column names containing date entries
    :return: The reformatted dataframe
    """
    for col in date_columns:
        df[col] = df[col].apply(lambda x: dateparser.parse(str(x), settings={'DATE_ORDER': date_order})
        if not pd.isnull(x) and dateparser.parse(str(x), settings={'DATE_ORDER': date_order}) is not None else np.nan
        if remove_unparsable else x)
    return df


def decompose_date_entries(df: DataFrame, date_columns: list[str]) -> DataFrame:
    """Decomposes date entries into year, month and day.

    :param df: The dataframe to be decomposed
    :param date_columns: List of column names containing date entries
    :return: The decomposed dataframe
    """
    for col in date_columns:
        df[col + '_year'] = pd.DatetimeIndex(df[col]).year
        df[col + '_month'] = pd.DatetimeIndex(df[col]).month
        df[col + '_day'] = pd.DatetimeIndex(df[col]).day
        df.drop(col, axis=1, inplace=True)
    return df
