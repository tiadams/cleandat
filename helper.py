import constants


def get_encoding(string):
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
                key, value = string.split(delimiter)
                # remove trailing and leading whitespaces
                key = key.strip()
                value = value.strip()
                if key.isnumeric() and value.isalpha():
                    return key, value
    else:
        return None
