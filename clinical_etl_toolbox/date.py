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


def clean_date_entries(df: DataFrame, date_columns: list[str], date_order: str = 'DMY',
                       replace_unparsable=True) -> DataFrame:
    """Replace all date entries with a uniform format.

    Reformat all date entries to a uniform format - dates may be written in different formats,
    e.g. 01.01.2020 or January 1st, 2020

    :param replace_unparsable: If True, replace entries that cannot be parsed as dates with NaN
    :param date_order: The order of the date entries, e.g. DMY for 01.01.2020 or MDY for January 1st, 2020
    :param df: The dataframe to be reformatted
    :param date_columns: List of column names containing date entries
    :return: The reformatted dataframe
    """
    for col in date_columns:
        for idx, entry in enumerate(df[col]):
            if not pd.isnull(entry):
                date = dateparser.parse(str(entry), settings={'DATE_ORDER': date_order})
                if date is not None:
                    df.loc[idx, col] = date
                else:
                    if replace_unparsable:
                        df.loc[idx, col] = np.nan
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
