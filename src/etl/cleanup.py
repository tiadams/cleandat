import numpy as np
from pandas import DataFrame


def clean_unknown_entries(df: DataFrame) -> DataFrame:
    """Takes a dataframe as input and returns the same dataframe with all entries that are unknown replaced by NaN.

    :param df: DataFrame: Specify the dataframe that is passed into the function
    :return: A dataframe
    """
    #  if it is not known, it should be either empty or nan
    tokens = ['?', 'unknown']
    df.replace(tokens, np.nan, inplace=True)
    return df


def drop_rows(df: DataFrame, row_indices: list[int]) -> DataFrame:
    """
    The drop_rows function takes a DataFrame and a list of row indices as input.
    It drops the rows in the DataFrame that correspond to those indices, and returns
    the resulting DataFrame.

    :param df: DataFrame: Specify the dataframe that will be passed into the function
    :param row_indices: list[int]: Specify the indices of rows to be dropped
    :return: A dataframe
    :doc-author: Trelent
    """
    df.drop(row_indices, axis=0, inplace=True)
    return df


def drop_empty_rows(df):
    """
    The drop_empty_rows function takes a dataframe as input and drops all rows that are empty.
        It returns the modified dataframe.

    :param df: Pass in the dataframe that we want to drop empty rows from
    :return: The dataframe with rows that are empty
    :doc-author: Trelent
    """
    df.dropna(axis=0, how='all', inplace=True)
    return df


def drop_empty_columns(df):
    """
    The drop_empty_columns function takes a dataframe as an argument and returns the same dataframe with any columns that
    are entirely empty (i.e., contain only NaN values) removed.

    :param df: Pass in the dataframe that we want to drop columns from
    :return: A dataframe with all columns that are empty dropped
    :doc-author: Trelent
    """
    for columns in df:
        if df[columns].isnull().all():
            df.drop(columns, axis=1, inplace=True)
    return df


def remove_entries_with_inconsistent_datatypes(df, threshold=0.1):
    """ Removes entries that seem inconsistent with the rest of the column (e.g. string values in columns containing
    >90% numbers) and replace them with NaN.

    Only execute this after fully encoding the data / finishing all previous cleaning steps.
    :param df: The dataframe to be cleaned
    :param threshold: This threshold defines the minimum percentage of entries that need to be inconsistent to be
    dropped from the dataframe
    :return:
    """
    for column in df:
        if df[column].dtype == 'object':
            percentage_numeric = sum([str(entry).isnumeric() for entry in df[column]]) / len(df[column])
            # numeric entries which are smaller than the threshold are considered inconsistent
            if percentage_numeric < threshold:
                df[column] = df[column].apply(lambda x: np.nan if str(x).isnumeric() else x)
            # string entries which are smaller than the threshold are considered inconsistent
            if 1 - percentage_numeric < threshold:
                df[column] = df[column].apply(lambda x: np.nan if not str(x).isnumeric() else x)
    return df
