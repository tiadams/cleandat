import re
import numpy as np
import pandas as pd
from pandas import DataFrame

from cleandat.constants import MISSING_DATA_TOKENS


def clean_unknown_entries(df: DataFrame) -> DataFrame:
    """Takes a dataframe as input and returns the same dataframe with all entries that are unknown replaced by NaN.

    :param df: DataFrame: Specify the dataframe that is passed into the function
    :return: A dataframe
    """
    #  if it is not known, it should be either empty or nan
    tokens = MISSING_DATA_TOKENS
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
    """
    df.drop(row_indices, axis=0, inplace=True)
    return df


def drop_empty_rows(df: DataFrame) -> DataFrame:
    """
    The drop_empty_rows function takes a dataframe as input and drops all rows that are empty.
        It returns the modified dataframe.

    :param df: Pass in the dataframe that we want to drop empty rows from
    :return: The dataframe with rows that are empty
    """
    df.dropna(axis=0, how='all', inplace=True)
    return df


def drop_empty_columns(df: DataFrame) -> DataFrame:
    """
    The drop_empty_columns function takes a dataframe as an argument and returns the same dataframe with any columns
    that are entirely empty (i.e., contain only NaN values) removed.

    :param df: Pass in the dataframe that we want to drop columns from
    :return: A dataframe with all columns that are empty dropped
    """
    for columns in df:
        if df[columns].isnull().all():
            df.drop(columns, axis=1, inplace=True)
    return df


def remove_entries_with_inconsistent_datatypes(df: DataFrame, threshold: float = 0.1) -> DataFrame:
    """ Removes entries that seem inconsistent with the rest of the column (e.g. string values in columns containing
    >90% numbers) and replace them with NaN.

    Only execute this after fully encoding the data / finishing all previous cleaning steps.
    :param df: The dataframe to be cleaned
    :param threshold: The threshold for the ratio of non-allowed inconsistent entries in a column, default 0.1 - meaning
    when more than 10% of the entries in a column are inconsistent (e.g. containing string instead of int), they get
    removed
    :return: The cleaned dataframe
    """
    for column in df:
        if df[column].dtype == 'object':

            # exclude nan entries from the calculation
            number_nan = sum([pd.isna(entry) for entry in df[column]])

            # calculate the percentage of numeric entries in the column
            percentage_numeric = sum([str(entry).isnumeric() for entry in df[column]]) / (len(df[column]) - number_nan)

            # numeric entries which are smaller than the threshold are considered inconsistent
            if percentage_numeric < threshold:
                df[column] = df[column].apply(lambda x: np.nan if str(x).isnumeric() else x)

            # string entries which are smaller than the threshold are considered inconsistent
            if 1 - percentage_numeric < threshold:
                df[column] = df[column].apply(lambda x: np.nan if not str(x).isnumeric() else x)

    return df


def unify_number_format(df: DataFrame) -> DataFrame:
    """Unify the number format of all entries in the dataframe.

    Data may be presented in different formats, e.g. in scientific notation (3.453 * 10^-4).
    This function unifies the format to a simple decimal number.

    :param df: The dataframe to be cleaned
    :return: The cleaned dataframe
    """
    for column in df:
        # replace all entries that contain a comma with a dot
        df[column] = df[column].replace(',', '.', regex=True)

        # replace scientific notation string with machine-readable notation
        # first: replace unicode superscript numbers with regular integers (e.g. ⁴ -> ^4)
        df[column] = df[column].apply(lambda x: replace_unicode_superscript_numbers(x) if pd.notna(x) else x)
        # second: replace the scientific notation with machine-readable notation
        df[column] = df[column].replace('10\s*\^', 'e+0', regex=True)

        # multiplication signs (either x or *) can be replaced with a whitespace
        df[column] = df[column].replace('\s?[\*x]\s?', ' ', regex=True)

        # dashes most likely imply ranges, e.g. when something can't be measured precisely -> take average instead
        df[column] = df[column].apply(lambda x: replace_range_with_average(x) if pd.notna(x) else x)

        # replace exponential notation with float
        df[column] = df[column].apply(lambda x: convert_exponential_to_float(x.replace(" ", "")) if pd.notna(x) else x)

    return df


def replace_range_with_average(input_string: str) -> str:
    """ Takes a string as input and returns the average of the lower and upper bounds of the range

    :param input_string: The input string
    :return: The average of the lower and upper bounds of the range if the input string matches the pattern, #
    else the input string
    """
    if pd.notna(input_string):
        # Define a regular expression pattern to match the range format (e.g., 1-2 or 0.5-1.7)
        pattern = r"(\d+(\.\d+)?)-(\d+(\.\d+)?)"

        # Find all occurrences of the pattern in the input_string
        matches = re.findall(pattern, str(input_string))

        if matches:
            # Calculate the average of the lower and upper bounds of the range
            lower_bound = float(matches[0][0])
            upper_bound = float(matches[0][2])
            average = (lower_bound + upper_bound) / 2

            # Replace the matched range with the calculated average
            return re.sub(pattern, str(average), input_string)

    return input_string


def replace_unicode_superscript_numbers(input_string: str) -> str:
    """
    The replace_unicode_superscript_numbers function takes a string as input and returns the same string with any
    unicode superscript numbers replaced by their equivalent LaTeX code. For example, it will replace ² with ^2.

    :param input_string: Store the string that is passed into the function
    :return: A string with unicode superscript numbers replaced by
    """
    for sup, num in zip("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789"):
        input_string = str(input_string).replace(sup, "^" + num)
    return input_string


def convert_exponential_to_float(value: str) -> float:
    """Converts a string containing an exponential notation to a float.

    :param value: Store the value of each cell in the dataframe
    :return: A float, or the original value if it can't be converted to a float
    :doc-author: Trelent
    """
    # Check if the value is a string containing an exponential notation
    if isinstance(value, str) and 'e' in value.lower():
        try:
            # Convert exponential notation to float
            return float(value)
        except ValueError:
            # If the conversion fails, keep the original value
            return value
    # Check if the value is NaN
    elif pd.isna(value):
        return np.nan
    else:
        return value
