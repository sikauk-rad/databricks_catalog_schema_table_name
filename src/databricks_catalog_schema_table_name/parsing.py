def split_prefix(
    string: str,
    prefix_separator: str | None,
) -> tuple[str | None, str, str]:

    """
    Split a prefix from the start of a string.

    The split occurs on the first occurrence of the separator. If the separator is falsy 
    (empty string or ``None``) or does not occur in the string, the prefix is treated as 
    absent and the whole string is returned as the remainder.

    Parameters
    ----------
    string : str
        The raw string to parse.
    prefix_separator : str or None
        Separator used to split the prefix from the remainder.

    Returns
    -------
    tuple[str or None, str, str]
        The prefix (or ``None``), the remainder, and the separator to store. A falsy 
        separator is normalised to ``''``.
    """

    if not prefix_separator:
        return None, string, ''

    prefix, separator, remainder = string.partition(prefix_separator)

    if not separator:
        return None, string, prefix_separator
    else:
        return prefix, remainder, prefix_separator


def split_suffix(
    string: str,
    suffix_separator: str | None,
) -> tuple[str, str | None, str]:

    """
    Split a suffix from the end of a string.

    The split occurs on the last occurrence of the separator. If the separator is falsy 
    (empty string or ``None``) or does not occur in the string, the suffix is treated as 
    absent and the whole string is returned as the name.

    Parameters
    ----------
    string : str
        The raw string to parse.
    suffix_separator : str or None
        Separator used to split the suffix from the name.

    Returns
    -------
    tuple[str, str or None, str]
        The name, the suffix (or ``None``), and the separator to store. A falsy separator 
        is normalised to ``''``.
    """

    if not suffix_separator:
        return string, None, ''

    name, separator, suffix = string.rpartition(suffix_separator)

    if not separator:
        return string, None, suffix_separator
    else:
        return name, suffix, suffix_separator