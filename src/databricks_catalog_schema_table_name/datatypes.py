from typing import Self

from msgspec import Struct
from msgspec.structs import replace


class StructWithAttribute(Struct, frozen = True):

    """
    Base class for frozen structs supporting attribute replacement.

    Provides a convenience method for creating modified copies of frozen struct instances
    with improved error reporting for invalid field names.
    """

    def with_attribute(
        self,
        **kwargs,
    ) -> Self:

        """
        Return a copy of the struct with the given attributes replaced.

        Parameters
        ----------
        **kwargs
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
            struct. The error message lists the unrecognised field names.
        """

        try:
            return replace(self, **kwargs)
        except TypeError as exc:
            original_keys = {*self.__struct_fields__}
            bad_keys = kwargs.keys() - original_keys
            raise TypeError(f'unrecognised arguments: {", ".join(bad_keys)}.') from exc