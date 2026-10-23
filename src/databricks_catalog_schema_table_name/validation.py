from . import constants


def validate_name(
    name: object,
) -> None:

    """
    Validate the core name component of a catalog, schema, or table.

    Parameters
    ----------
    name : object
        The value to validate.

    Raises
    ------
    TypeError
        If ``name`` is not a string.
    ValueError
        If ``name`` is empty or contains the namespace separator ``'.'``.
    """

    if not isinstance(name, str):
        raise TypeError('name must be a string.')
    elif not name:
        raise ValueError('name must be a non-empty string.')
    elif constants.NAMESPACE_SEPARATOR in name:
        raise ValueError(f'name must not contain {constants.NAMESPACE_SEPARATOR}.')


def validate_affix(
    affix: object,
    field_name: str,
) -> None:

    """
    Validate an optional prefix or suffix component.

    Parameters
    ----------
    affix : object
        The value to validate. ``None`` denotes an absent affix and is always valid.
    field_name : str
        Name of the field being validated, used in error messages.

    Raises
    ------
    TypeError
        If ``affix`` is neither a string nor ``None``.
    ValueError
        If ``affix`` is an empty string or contains the namespace separator ``'.'``.
    """

    if affix is None:
        return
    elif not isinstance(affix, str):
        raise TypeError(f'{field_name} must be a string or None.')
    elif not affix:
        raise ValueError(f'{field_name} must be a non-empty string or None.')
    elif constants.NAMESPACE_SEPARATOR in affix:
        raise ValueError(
            f'{field_name} must not contain {constants.NAMESPACE_SEPARATOR}.'
        )


def validate_separator(
    separator: object,
    field_name: str,
) -> None:

    """
    Validate a prefix or suffix separator.

    Parameters
    ----------
    separator : object
        The value to validate. An empty string is permitted.
    field_name : str
        Name of the field being validated, used in error messages.

    Raises
    ------
    TypeError
        If ``separator`` is not a string.
    ValueError
        If ``separator`` contains the namespace separator ``'.'``.
    """

    if not isinstance(separator, str):
        raise TypeError(f'{field_name} must be a string.')
    elif constants.NAMESPACE_SEPARATOR in separator:
        raise ValueError(
            f'{field_name} must not contain {constants.NAMESPACE_SEPARATOR}.'
        )