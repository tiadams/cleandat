from pandas import DataFrame

from clinical_etl_toolbox.cleanup import drop_rows, drop_empty_columns, drop_empty_rows, clean_unknown_entries, \
    remove_entries_with_inconsistent_datatypes, unify_number_format
from clinical_etl_toolbox.encoding import get_column_encoding_schemes, encode_dataframe, \
    identify_descriptive_header_rows
from clinical_etl_toolbox.date import identify_date_columns, clean_date_entries, decompose_date_entries


def find_encodings_and_encode_strings(df: DataFrame, drop_encoding_rows: bool = True) -> DataFrame:
    """Finds the encoding schemes of a dataframe, encodes the dataframe and removes the encoding rows.

    :param drop_encoding_rows: Whether rows containing the encoding description should be dropped afterwards,
    default true
    :param df: The dataframe to be encoded
    :return: The encoded dataframe without the rows which describe the encoding schemes
    """
    encodings = get_column_encoding_schemes(df)
    df = encode_dataframe(df, encodings)
    if drop_encoding_rows:
        encoding_rows = identify_descriptive_header_rows(df)
        df = drop_rows(df, encoding_rows)
    return df


def remove_empty_columns_and_rows(df: DataFrame) -> DataFrame:
    """Removes empty columns and rows from a dataframe.

    :param df: The dataframe to be cleaned
    :return: The cleaned dataframe
    """
    df = drop_empty_columns(df)
    df = drop_empty_rows(df)
    return df


def clean_date_entries(df: DataFrame, decompose_dates: bool = True) -> DataFrame:
    """Cleans and encodes date entries in a dataframe.

    :param decompose_dates: Whether date entries should be decomposed into _day, month, year columns, default true
    :param df: The dataframe to be cleaned
    :return: The cleaned dataframe
    """
    date_columns = identify_date_columns(df)
    df = clean_date_entries(df, date_columns)
    if decompose_dates:
        df = decompose_date_entries(df, date_columns)
    return df


def remove_inconsistencies(df: DataFrame) -> DataFrame:
    """Removes inconsistencies from a dataframe and replaces them with NaN.

    Should be used after as a last step (especially after encoding steps) since it removes data.

    :param df: The dataframe to be cleaned
    :return: The cleaned dataframe
    """
    df = unify_number_format(df)
    df = clean_unknown_entries(df)
    df = remove_entries_with_inconsistent_datatypes(df)
    return df
