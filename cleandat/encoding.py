import numpy as np
import pandas as pd
from pandas import DataFrame

from cleandat import constants


def get_encoding(string: str) -> (str, int):
    """ Checks whether a string could be meant as documentation for an encoding.

    Encoding may be divided by a combination of whitespaces and/or delimiters, e.g. for male/female encoding
    1=m, 1->m, 1 - m, 1 : m.

    :param string: The string that should be checked
    :return: The assumed key and value of the encoding, if the string is a code string, else None
    """
    possible_delimiters = constants.DELIMITERS
    if any(delimiter in string for delimiter in possible_delimiters):
        for delimiter in possible_delimiters:
            if delimiter in string:
                try:
                    key, value = string.split(delimiter)
                except ValueError:
                    return None
                # remove trailing and leading whitespaces
                key = key.strip()
                value = value.strip()
                if key.isnumeric() and isinstance(value, str):
                    return value, int(key)
                # in case the order is swapped, e.g. m=1 instead of 1=m
                if value.isnumeric() and isinstance(key, str):
                    return key, int(value)

    else:
        return None


def identify_descriptive_header_cells(df: DataFrame) -> DataFrame:
    """Identifies cells that are likely to contain an encoding scheme opposed to containing actual data.

    Heuristic: If an entry contains a number and a string divided by some kind of delimiter (that may be a whitespace,
    a colon, etc.) and the number is contained in the data of this column, it is likely a descriptive header.

    Example: '1= Age' or '1 : Age' or '1 Age' or '1=Age' or '1->Age' or '1_Age'

    :param df: The dataframe to be analyzed
    :return: boolean matrix with the same dimensions as the dataframe, where True indicates a descriptive header cell
    """
    is_header_matrix = pd.DataFrame(False, index=df.index, columns=df.columns)
    for column in df:
        for row_idx, entry in enumerate(df[column]):
            # first case: cell is emtpy
            if pd.isnull(entry):
                is_header_matrix.at[row_idx, column] = np.nan
                continue
            # second case: cell is not an encoding cell
            if get_encoding(str(entry)) is None:
                continue
            # third case: cell is an encoding cell
            key, value = get_encoding(str(entry))
            # check if the key is also contained in the data of this column
            if key is not None and value is not None and int(value) in df[column]:
                is_header_matrix.at[row_idx, column] = True
    return is_header_matrix


def get_column_encoding_schemes(df: DataFrame) -> dict:
    """ Gets the encoding schemes from a heuristic of descriptive header cells of a dataframe.

    :param df: The dataframe from which the encoding schemes should be extracted
    :return: For each column, a dictionary containing the encoding schemes
    """
    is_header_cell = identify_descriptive_header_cells(df)
    # ignore empty cells
    is_header_cell.replace(np.nan, False, inplace=True)
    schemas = {}
    for column in df:
        col_mappings = {}
        for entry in df[column][is_header_cell[column]]:
            if entry is not None and get_encoding(entry) is not None:
                key, value = get_encoding(entry)
                col_mappings[key] = value
        if len(col_mappings) > 0:
            schemas[column] = col_mappings
    return schemas


def identify_descriptive_header_rows(df: DataFrame, error_tolerance: float = 0.1) -> list[int]:
    """Identifies rows that are likely to contain an encoding scheme opposed to containing actual data.

    Heuristic: if a row contains a descriptive header cell and only other entries that are either non-empty or other
    descriptive header entries, it is likely that the whole row is used to describe an encoding of the data.

    :param df: The dataframe to be analyzed
    :param error_tolerance: Percentage of entries allowed that do not conform to the heuristic
    :return: Row indices of rows that are likely to contain an encoding scheme
    """
    bool_headers_df = identify_descriptive_header_cells(df)
    row_indices = []
    for idx, row in enumerate(bool_headers_df.index):
        # check for rows containing encoding cells
        if bool_headers_df.loc[row].any():
            if (bool_headers_df.iloc[idx] == False).sum() / df.shape[1] < error_tolerance:
                row_indices.append(idx)
    return row_indices


def encode_dataframe(df: DataFrame, encoding_schemes: dict) -> DataFrame:
    """Encodes a dataframe according to a given encoding scheme.

    :param df: The dataframe to be encoded
    :param encoding_schemes: The encoding schemes to be used for encoding the dataframe
    :return: The encoded dataframe
    """
    encoded_df = df.copy()
    for column in df:
        if column in encoding_schemes:
            encoded_df[column] = encoded_df[column].replace(encoding_schemes[column])
    return encoded_df
