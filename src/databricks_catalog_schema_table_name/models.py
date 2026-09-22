from typing import Self, overload

from .datatypes import StructWithAttribute


class TableName(StructWithAttribute, frozen = True):

    """
    A structured representation of a Databricks table name.

    Encapsulates a table name together with optional prefix and suffix components and 
    their respective separators. The full name can be reconstructed via ``str()``.

    Parameters
    ----------
    prefix : str or None
        Optional prefix component prepended to the name.
    name : str
        The core table name.
    suffix : str or None, optional
        Optional suffix component appended to the name. Defaults to ``None``.
    prefix_separator : str, optional
        String separating the prefix from the name. Defaults to ``'__'``.
    suffix_separator : str, optional
        String separating the name from the suffix. Defaults to ``''``.

    Examples
    --------
    >>> str(TableName(prefix='bronze', name='customers'))
    'bronze__customers'
    """

    prefix: str | None
    name: str
    suffix: str | None = None
    prefix_separator: str = '__'
    suffix_separator: str = ''

    def __str__(self) -> str:

        """
        Render the full table name as a string.

        Returns
        -------
        str
            The concatenation of prefix, name, and suffix using their respective 
            separators. Components that are ``None`` are omitted.
        """

        name = self.name
        if (prefix := self.prefix) is not None:
            name = f'{prefix}{self.prefix_separator}{name}'        

        if (suffix := self.suffix) is not None:
            name = f'{name}{self.suffix_separator}{suffix}'

        return name


    def with_prefix(
        self,
        prefix: str,
    ) -> Self:

        """
        Return a copy with the prefix replaced.

        Parameters
        ----------
        prefix : str
            The new prefix value.

        Returns
        -------
        Self
            A new ``TableName`` with the updated prefix.
        """

        return self.with_attribute(prefix = prefix)


    def with_prefix_separator(
        self,
        prefix_separator: str,
    ) -> Self:

        """
        Return a copy with the prefix separator replaced.

        Parameters
        ----------
        prefix_separator : str
            The new prefix separator value.

        Returns
        -------
        Self
            A new ``TableName`` with the updated prefix separator.
        """

        return self.with_attribute(prefix_separator = prefix_separator)


    def with_name(
        self,
        name: str,
    ) -> Self:

        """
        Return a copy with the core name replaced.

        Parameters
        ----------
        name : str
            The new table name value.

        Returns
        -------
        Self
            A new ``TableName`` with the updated name.
        """

        return self.with_attribute(name = name)


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
            A new ``TableName`` with the updated suffix separator.
        """

        return self.with_attribute(suffix_separator = suffix_separator)


    def with_suffix(
        self,
        suffix: str,
    ) -> Self:

        """
        Return a copy with the suffix replaced.

        Parameters
        ----------
        suffix : str
            The new suffix value.

        Returns
        -------
        Self
            A new ``TableName`` with the updated suffix.
        """

        return self.with_attribute(suffix = suffix)


    @classmethod
    def from_string(
        cls,
        string: str,
        prefix_separator: str | None = '__',
        suffix_separator: str | None = None,
    ) -> Self:

        """
        Parse a ``TableName`` from a raw string.

        Splits the input string into prefix, name, and suffix components according to the
        given separators. If a separator is falsy (empty string or ``None``), the 
        corresponding component is treated as absent.

        Parameters
        ----------
        string : str
            The raw table name string to parse.
        prefix_separator : str or None, optional
            Separator used to split the prefix from the remainder of the string. The 
            split occurs on the first occurrence. If falsy, no prefix is extracted. 
            Defaults to ``'__'``.
        suffix_separator : str or None, optional
            Separator used to split the suffix from the name. The split occurs on the 
            last occurrence. If falsy, no suffix is extracted. Defaults to ``None``.

        Returns
        -------
        Self
            A new ``TableName`` with components populated from the string.

        Raises
        ------
        ValueError
            If ``prefix_separator`` is truthy but not found in the string, or if 
            ``suffix_separator`` is truthy but not found in the remaining name.

        Examples
        --------
        >>> TableName.from_string('bronze__customers')
        TableName(prefix='bronze', name='customers', ...)
        """

        if prefix_separator:
            try:
                prefix, name = string.split(prefix_separator, maxsplit = 1)
            except ValueError as exc:
                raise ValueError(f'{prefix_separator = } not found.') from exc
        else:
            prefix = None
            prefix_separator = ''
            name = string

        if suffix_separator:
            try:
                name, suffix = name.rsplit(suffix_separator, maxsplit = 1)
            except ValueError as exc:
                raise ValueError(f'{suffix_separator = } not found.') from exc
        else:
            suffix_separator = ''
            suffix = None

        return cls(
            prefix = prefix,
            prefix_separator = prefix_separator,
            name = name,
            suffix_separator = suffix_separator,
            suffix = suffix,
        )


    @property
    def str(self) -> str:
        return str(self)


class CatalogSchemaTable(StructWithAttribute, frozen = True):

    """
    A fully qualified Databricks table reference.

    Represents the three-level namespace of a Unity Catalog table, combining a catalog, a
    schema, and a structured table name. The fully qualified name can be reconstructed 
    via ``str()``.

    Parameters
    ----------
    catalog : str
        The catalog component of the reference.
    schema : str
        The schema component of the reference.
    table : TableName
        The structured table name component.

    Examples
    --------
    >>> ref = CatalogSchemaTable(
    ...     catalog='main',
    ...     schema='sales',
    ...     table=TableName(prefix='bronze', name='customers'),
    ... )
    >>> str(ref)
    'main.sales.bronze__customers'
    """

    catalog: str
    schema: str
    table: TableName


    def __str__(self) -> str:

        """
        Render the fully qualified table reference as a string.

        Returns
        -------
        str
            The catalog, schema, and table joined by full stops, e.g. 
            ``'catalog.schema.table'``.
        """

        return f'{self.catalog}.{self.schema}.{self.table}'


    def with_catalog(
        self,
        catalog: str,
    ) -> Self:

        """
        Return a copy with the catalog replaced.

        Parameters
        ----------
        catalog : str
            The new catalog value.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated catalog.
        """

        return self.with_attribute(catalog = catalog)


    def with_schema(
        self,
        schema: str,
    ) -> Self:

        """
        Return a copy with the schema replaced.

        Parameters
        ----------
        schema : str
            The new schema value.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated schema.
        """

        return self.with_attribute(schema = schema)


    @overload
    def with_table(
        self, 
        table: TableName,
    ) -> Self: 

        ...


    @overload
    def with_table(
        self,
        table: str,
        prefix_separator: str | None = ...,
        suffix_separator: str | None = ...,
    ) -> Self: 

        ...


    def with_table(
        self,
        table: TableName | str,
        prefix_separator: str | None = '__',
        suffix_separator: str | None = None,
    ) -> Self:

        """
        Return a copy with the table replaced.

        Accepts either a ready-made ``TableName`` or a raw string. When a string is 
        given, it is parsed into a ``TableName`` using the supplied separators; the 
        ``prefix_separator`` and ``suffix_separator`` arguments are ignored when a 
        ``TableName`` is passed directly.

        Parameters
        ----------
        table : TableName or str
            The new table component. If a ``TableName``, it is used as-is. If a string, 
            it is parsed via :meth:`TableName.from_string`.
        prefix_separator : str or None, optional
            Separator used to split the prefix when ``table`` is a string. The split 
            occurs on the first occurrence. If falsy, no prefix is extracted. Ignored 
            when ``table`` is a ``TableName``. Defaults to ``'__'``.
        suffix_separator : str or None, optional
            Separator used to split the suffix when ``table`` is a string. The split 
            occurs on the last occurrence. If falsy, no suffix is extracted. Ignored 
            when ``table`` is a ``TableName``. Defaults to ``None``.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated table.

        Raises
        ------
        ValueError
            If ``table`` is a string and a truthy separator is not found within it, as 
            propagated from :meth:`TableName.from_string`.

        Examples
        --------
        >>> ref = CatalogSchemaTable(
        ...     catalog='main',
        ...     schema='sales',
        ...     table=TableName(prefix='bronze', name='customers'),
        ... )
        >>> str(ref.with_table('silver__orders'))
        'main.sales.silver__orders'
        >>> str(ref.with_table(TableName(prefix=None, name='raw')))
        'main.sales.raw'
        """

        if isinstance(table, TableName):
            table_obj = table
        else:
            table_obj = TableName.from_string(
                table,
                prefix_separator = prefix_separator,
                suffix_separator = suffix_separator,
            )

        return self.with_attribute(table = table_obj)


    def with_table_attribute(
        self,
        **kwargs: str | None,
    ) -> Self:

        """
        Return a copy with attributes of the nested table replaced.

        Applies the given keyword arguments to the nested ``TableName`` and returns a new
        ``CatalogSchemaTable`` containing the modified table.

        Parameters
        ----------
        **kwargs : str
            Field names and values to replace on the nested ``TableName``. Each key must 
            correspond to an existing ``TableName`` field.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated table.

        Raises
        ------
        TypeError
            If any key does not correspond to a field on ``TableName``.
        """

        new_table = self.table.with_attribute(**kwargs)
        return self.with_attribute(table = new_table)


    def with_table_prefix(
        self,
        prefix: str,
    ) -> Self:

        """
        Return a copy with the nested table's prefix replaced.

        Parameters
        ----------
        prefix : str
            The new prefix value for the nested ``TableName``.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated table prefix.
        """

        return self.with_table_attribute(prefix = prefix)


    def with_table_prefix_separator(
        self,
        prefix_separator: str,
    ) -> Self:

        """
        Return a copy with the nested table's prefix separator replaced.

        Parameters
        ----------
        prefix_separator : str
            The new prefix separator value for the nested ``TableName``.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated table prefix separator.
        """

        return self.with_table_attribute(prefix_separator = prefix_separator)


    def with_table_name(
        self,
        name: str,
    ) -> Self:

        """
        Return a copy with the nested table's core name replaced.

        Parameters
        ----------
        name : str
            The new name value for the nested ``TableName``.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated table name.
        """

        return self.with_table_attribute(name = name)


    def with_table_suffix_separator(
        self,
        suffix_separator: str,
    ) -> Self:

        """
        Return a copy with the nested table's suffix separator replaced.

        Parameters
        ----------
        suffix_separator : str
            The new suffix separator value for the nested ``TableName``.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated table suffix separator.
        """

        return self.with_table_attribute(suffix_separator = suffix_separator)


    def with_table_suffix(
        self,
        suffix: str,
    ) -> Self:

        """
        Return a copy with the nested table's suffix replaced.

        Parameters
        ----------
        suffix : str
            The new suffix value for the nested ``TableName``.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated table suffix.
        """

        return self.with_table_attribute(suffix = suffix)


    @classmethod
    def from_string(
        cls,
        string: str,
        prefix_separator: str | None = '__',
        suffix_separator: str | None = None,
    ) -> Self:

        """
        Parse a ``CatalogSchemaTable`` from a fully qualified string.

        Splits the input on full stops into catalog, schema, and table components, then 
        parses the table component into a ``TableName`` using the given separators.

        Parameters
        ----------
        string : str
            The fully qualified reference, of the form ``'catalog.schema.table'``.
        prefix_separator : str or None, optional
            Separator passed to :meth:`TableName.from_string` for extracting the table 
            prefix. Defaults to ``'__'``.
        suffix_separator : str or None, optional
            Separator passed to :meth:`TableName.from_string` for extracting the table 
            suffix. Defaults to ``None``.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` parsed from the string.

        Raises
        ------
        ValueError
            If the string does not contain exactly two full stops, or if a requested 
            separator is not found within the table component.

        Examples
        --------
        >>> CatalogSchemaTable.from_string('main.sales.bronze__customers')
        CatalogSchemaTable(catalog='main', schema='sales', ...)
        """

        try:
            catalog, schema, table = string.split('.')
        except ValueError as exc:
            raise ValueError('string must contain exactly two full stops.') from exc

        table_name = TableName.from_string(
            table,
            prefix_separator = prefix_separator,
            suffix_separator = suffix_separator,
        )
        return cls(
            catalog = catalog,
            schema = schema, 
            table = table_name, 
        )


    @property
    def str(self) -> str:
        return str(self)