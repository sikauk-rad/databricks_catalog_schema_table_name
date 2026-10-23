import builtins
from typing import Any, Self

from msgspec import Struct

from .parsing import split_suffix
from .validation import validate_affix, validate_name, validate_separator


class StructWithAttribute(Struct, frozen = True):

    """
    Base class for frozen structs supporting attribute replacement.

    Provides a convenience method for creating modified copies of frozen struct instances
    with improved error reporting for invalid field names. Copies are always built 
    through the struct's constructor, so any validation defined in ``__post_init__`` is 
    re-applied to the new instance.
    """

    def with_attribute(
        self,
        **kwargs: Any,
    ) -> Self:

        """
        Return a copy of the struct with the given attributes replaced.

        Parameters
        ----------
        **kwargs : Any
            Field names and their new values. Each key must correspond to an existing 
            field on the struct.

        Returns
        -------
        Self
            A new struct instance with the specified fields replaced. All unspecified 
            fields retain their original values.

        Raises
        ------
        TypeError
            If any key in ``kwargs`` does not correspond to an existing field on the 
            struct. The error message lists the unrecognised field names. May also be 
            raised by ``__post_init__`` if a new value has an invalid type.
        ValueError
            If a new value fails validation in ``__post_init__``.
        """

        if (bad_keys := kwargs.keys() - {*self.__struct_fields__}):
            raise TypeError(f'attributes not recognised: {", ".join(sorted(bad_keys))}')
        else:
            fields = {field: getattr(self, field) for field in self.__struct_fields__}
            return type(self)(**(fields | kwargs))


    @property
    def str(self) -> builtins.str:

        """
        Render the object as a string.

        Returns
        -------
        str
            Equivalent to ``str(self)``.
        """

        return builtins.str(self)


class CatalogSchemaNameBase(StructWithAttribute, frozen = True, kw_only = True):

    """
    Base class for catalog and schema names.

    Encapsulates a name together with an optional suffix and its separator. The full name 
    can be reconstructed via ``str()``. Subclasses must provide a default for 
    ``suffix_separator``.

    Parameters
    ----------
    name : str
        The core name. Must be non-empty and must not contain ``'.'``.
    suffix : str or None, optional
        Optional suffix component appended to the name. Must be non-empty and must not 
        contain ``'.'`` if given. Defaults to ``None``.
    suffix_separator : str
        String separating the name from the suffix. Must not contain ``'.'``.
    """

    name: str
    suffix: str | None = None
    suffix_separator: str


    def __post_init__(
        self,
    ) -> None:

        """
        Validate the components after initialisation.

        Raises
        ------
        TypeError
            If any component has an invalid type.
        ValueError
            If the name or suffix is empty, or if any component contains ``'.'``.
        """

        validate_name(self.name)
        validate_affix(self.suffix, 'suffix')
        validate_separator(self.suffix_separator, 'suffix_separator')


    def __str__(self) -> str:

        """
        Render the full object as a string.

        Returns
        -------
        str
            The name, suffix separator, and suffix joined, e.g. 
            ``'namesuffixseparatorsuffix'``. If suffix is ``None``, only the name is 
            returned.
        """

        if (suffix := self.suffix) is None:
            return self.name
        else:
            return f'{self.name}{self.suffix_separator}{suffix}'


    def with_name(
        self,
        name: str,
    ) -> Self:

        """
        Return a copy with the name replaced.

        Parameters
        ----------
        name : str
            The new name value.

        Returns
        -------
        Self
            A new instance with the updated name.
        """

        return self.with_attribute(name = name)


    def with_suffix(
        self,
        suffix: str | None,
    ) -> Self:

        """
        Return a copy with the suffix replaced.

        Parameters
        ----------
        suffix : str or None
            The new suffix value. Set to ``None`` to remove the suffix.

        Returns
        -------
        Self
            A new instance with the updated suffix.
        """

        return self.with_attribute(suffix = suffix)


    def with_suffix_separator(
        self,
        suffix_separator: str,
    ) -> Self:

        """
        Return a copy with the suffix separator replaced.

        Parameters
        ----------
        suffix_separator : str
            The new suffix separator value.

        Returns
        -------
        Self
            A new instance with the updated suffix separator.
        """

        return self.with_attribute(suffix_separator = suffix_separator)


    @classmethod
    def from_string(
        cls,
        string: str,
        suffix_separator: str | None = '_',
    ) -> Self:

        """
        Parse an instance from a raw string.

        The split occurs on the last occurrence of the separator. If the separator is 
        falsy (empty string or ``None``) or does not occur in the string, the suffix is 
        treated as absent and the whole string becomes the name.

        Parameters
        ----------
        string : str
            The raw string to parse.
        suffix_separator : str or None, optional
            Separator used to split the suffix from the name. Defaults to ``'_'``.

        Returns
        -------
        Self
            A new instance with components populated from the string.

        Raises
        ------
        ValueError
            If a parsed component fails validation, e.g. an empty name from ``'_dev'`` or 
            an empty suffix from ``'main_'``.
        """

        name, suffix, separator = split_suffix(string, suffix_separator)

        return cls(
            name = name,
            suffix = suffix,
            suffix_separator = separator,
        )