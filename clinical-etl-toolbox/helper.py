from etl import constants


def get_encoding(string: str) -> (int, str):
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
                    return int(key), value
    else:
        return None
