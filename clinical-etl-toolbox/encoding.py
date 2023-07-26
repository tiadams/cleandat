import numpy as np
import pandas as pd
from pandas import DataFrame

from etl.helper import get_encoding


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
                is_header_matrix.at[row_idx, column] = np.nan
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
    # ignore empty entries since not all columns have the same number of encodings
    bool_headers_df.replace(np.nan, True, inplace=True)
    return [row for row in bool_headers_df.index if
            bool_headers_df.loc[row].sum() > (1 - error_tolerance) * len(df.columns)]


def encode_dataframe(df: DataFrame, encoding_schemes: dict) -> DataFrame:
    """Encodes a dataframe according to a given encoding scheme.

    :param df: The dataframe to be encoded
    :param encoding_schemes: The encoding schemes to be used for encoding the dataframe
    :return: The encoded dataframe
    """
    encoded_df = df.copy()
    for column in df:
        if column in encoding_schemes:
            encoded_df[column].replace(encoding_schemes[column], inplace=True)
            # everything else that can't be matched to a number or the scheme should be NaN
            encoded_df[column].replace(to_replace=r'[^0-9]', value=np.nan, regex=True, inplace=True)
    return encoded_df
