import pandas as pd
import numpy as np
import dateparser
from pandas import DataFrame


def identify_descriptive_header_cells(df: DataFrame) -> DataFrame:
    """Identifies cells that are likely to contain an encoding scheme opposed to containing actual data.

    Heuristic: If an entry contains a number and a string divided by some kind of delimiter (that may be a whitespace,
    a colon, etc.) and the number is contained in the data of this column, it is likely a descriptive header.

    Example: '1= Age' or '1 : Age' or '1 Age' or '1=Age' or '1->Age' or '1_Age'

    :param df: The dataframe to be analyzed
    :return: boolean matrix with the same dimensions as the dataframe, where True indicates a descriptive header cell
    """
    possible_delimiters = [':', '=', '-', '->', '_']
    is_header_matrix = pd.DataFrame(False, index=df.index, columns=df.columns)
    for column in df:
        for row_idx, entry in enumerate(df[column]):
            # first case: cell is emtpy
            if pd.isnull(entry):
                is_header_matrix[column][row_idx] = np.nan
                continue
            code_idx = None
            contains_number = False
            contains_string = False
            # second case: entries are only separated by whitespaces (and contain no delimiter)
            if ' ' in str(entry) and not any(delimiter in str(entry) for delimiter in possible_delimiters):
                for part in str(entry).split():
                    if part.isnumeric():
                        contains_number = True
                    else:
                        contains_string = True
                # code is (most likely) the first number in the entry
                if contains_string and contains_number:
                    code_idx = [x for x in str(entry).split() if x.isnumeric()][0]
            # third case: entries are separated by a delimiter, no whitespaces inbetween
            elif any(delimiter in str(entry) for delimiter in possible_delimiters) and ' ' not in str(entry):
                for delimiter in possible_delimiters:
                    for part in str(entry).split(delimiter):
                        if part.isnumeric():
                            contains_number = True
                        else:
                            contains_string = True
                # code is (most likely) the first number in the entry
                if delimiter in str(entry) and contains_string and contains_number:
                    code_idx = [x for x in str(entry).split(delimiter) if x.isnumeric()][0]
            # forth case: entries are separated by a delimiter, with whitespaces inbetween
            elif any(delimiter in str(entry) for delimiter in possible_delimiters) and ' ' in str(entry):
                fully_split = []
                # first split by whitespaces
                for part in str(entry).split():
                    if any(delimiter in str(entry) for delimiter in possible_delimiters):
                        fully_split.extend(part)
                    # then split by delimiters
                    else:
                        for delimiter in possible_delimiters:
                            if delimiter in part:
                                fully_split.extend(part.split(delimiter))

                for part in fully_split:
                    if part.isnumeric():
                        contains_number = True
                    else:
                        contains_string = True
                if contains_string and contains_number:
                    code_idx = [x for x in fully_split if x.isnumeric()][0]
            # check if the code is contained in the data of this column
            if code_idx is not None and contains_number and contains_string and int(code_idx) in df[column]:
                is_header_matrix[column][row_idx] = True
    return is_header_matrix


def get_column_encoding_schemes_from_descriptive_header_cells(df: DataFrame) -> dict:
    """ Gets the encoding schemes from the descriptive header cells of a dataframe.

    :param df: The dataframe from which the encoding schemes should be extracted
    :return: For each column, a dictionary containing the encoding schemes
    """
    is_header_cell = identify_descriptive_header_cells(df)
    for colum in df:
        for row_idx, entry in enumerate(df[colum]):
            if is_header_cell[colum][row_idx]:
                print(entry)




def identify_descriptive_header_rows(df: DataFrame, error_tolerance: float = 0.1) -> list[int]:
    """Identifies rows that are likely to contain an encoding scheme opposed to containing actual data.

    Heuristic: if a row contains a descriptive header cell and only other entries that are either non-empty or other
    descriptive header entries, it is likely that the whole row is used to describe an encoding of the data.

    :param df: The dataframe to be analyzed
    :param error_tolerance: Percentage of entries allowed that do not conform to the heuristic
    :return: Row indices of rows that are likely to contain an encoding scheme
    """
    bool_headers_df = identify_descriptive_header_cells(df)
    # ignore empty entries since not all columns have the same number of encodings
    bool_headers_df.replace(np.nan, True, inplace=True)
    return [row for row in bool_headers_df.index if
            bool_headers_df.loc[row].sum() > (1 - error_tolerance) * len(df.columns)]


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
                if pd.isnull(entry):
                    # empty cells should count towards the threshold
                    pro_date_heuristic += 1
                if not str(entry).isnumeric():
                    if dateparser.parse(str(entry)) is not None:
                        pro_date_heuristic += 1
            if pro_date_heuristic > threshold * len(df[column]):
                date_columns.append(column)
    return date_columns


def clean_date_entries(df: DataFrame, date_columns: list[str], date_order: str = 'DMY') -> DataFrame:
    """Replace all date entries with a uniform format.

    Reformat all date entries to a uniform format - dates may be written in different formats,
    e.g. 01.01.2020 or January 1st, 2020

    :param date_order: The order of the date entries, e.g. DMY for 01.01.2020 or MDY for January 1st, 2020
    :param df: The dataframe to be reformated
    :param date_columns: List of column names containing date entries
    :return: The reformated dataframe
    """
    for col in date_columns:
        for idx, entry in enumerate(df[col]):
            if not pd.isnull(entry):
                df.loc[idx, col] = dateparser.parse(str(entry), settings={'DATE_ORDER': date_order}).strftime(
                    '%Y-%m-%d')
    return df


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
    df.drop(row_indices, axis=0, inplace=True)
    return df


def drop_empty_rows(df):
    df.dropna(axis=0, how='all', inplace=True)
    return df


def drop_empty_columns(df):
    for columns in df:
        if df[columns].isnull().all():
            df.drop(columns, axis=1, inplace=True)
    return df


# Only execute this after fully encoding the data
def remove_entries_with_inconsistent_datatypes(df, threshold=0.1):
    for column in df:
        if df[column].dtype == 'object':
            # check for each entry if it is a number
            return df
    return df