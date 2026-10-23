from typing import Self, overload

from . import constants
from .datatypes import CatalogSchemaNameBase, StructWithAttribute
from .parsing import split_prefix, split_suffix
from .validation import validate_affix, validate_name, validate_separator


class CatalogName(CatalogSchemaNameBase, frozen = True, kw_only = True):

    """
    A structured representation of a Databricks catalog name.

    Parameters
    ----------
    name : str
        The core catalog name.
    suffix : str or None, optional
        Optional suffix component appended to the name. Defaults to ``None``.
    suffix_separator : str, optional
        String separating the name from the suffix. Defaults to ``'_'``.

    Examples
    --------
    >>> str(CatalogName(name = 'sdna_innovation', suffix = 'dev'))
    'sdna_innovation_dev'
    """

    suffix_separator: str = constants.DEFAULT_CATALOG_SUFFIX_SEPARATOR


class SchemaName(CatalogSchemaNameBase, frozen = True, kw_only = True):

    """
    A structured representation of a Databricks schema name.

    Parameters
    ----------
    name : str
        The core schema name.
    suffix : str or None, optional
        Optional suffix component appended to the name. Defaults to ``None``.
    suffix_separator : str, optional
        String separating the name from the suffix. Defaults to ``'_'``.

    Examples
    --------
    >>> str(SchemaName(name = 'dp_nuage_general', suffix = 'core'))
    'dp_nuage_general_core'
    """

    suffix_separator: str = constants.DEFAULT_SCHEMA_SUFFIX_SEPARATOR


class TableName(StructWithAttribute, frozen = True, kw_only = True):

    """
    A structured representation of a Databricks table name.

    Encapsulates a table name together with optional prefix and suffix components and 
    their respective separators. The full name can be reconstructed via ``str()``.

    Parameters
    ----------
    prefix : str or None, optional
        Optional prefix component prepended to the name. Defaults to ``None``.
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
    >>> str(TableName(prefix = 'bronze', name = 'customers'))
    'bronze__customers'
    """

    prefix: str | None = None
    name: str
    suffix: str | None = None
    prefix_separator: str = constants.DEFAULT_TABLE_PREFIX_SEPARATOR
    suffix_separator: str = constants.DEFAULT_TABLE_SUFFIX_SEPARATOR


    def __post_init__(self) -> None:

        """
        Validate the components after initialisation.

        Applies the same rules as ``CatalogName`` and ``SchemaName``, with the prefix 
        validated identically to the suffix.

        Raises
        ------
        TypeError
            If any component has an invalid type.
        ValueError
            If the name, prefix, or suffix is empty, or if any component contains 
            ``'.'``.
        """

        validate_name(self.name)
        validate_affix(self.prefix, 'prefix')
        validate_separator(self.prefix_separator, 'prefix_separator')
        validate_affix(self.suffix, 'suffix')
        validate_separator(self.suffix_separator, 'suffix_separator')


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
        prefix: str | None,
    ) -> Self:

        """
        Return a copy with the prefix replaced.

        Parameters
        ----------
        prefix : str or None
            The new prefix value. Set to ``None`` to remove the prefix.

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
            A new ``TableName`` with the updated suffix.
        """

        return self.with_attribute(suffix = suffix)


    @classmethod
    def from_string(
        cls,
        string: str,
        prefix_separator: str | None = constants.DEFAULT_TABLE_PREFIX_SEPARATOR,
        suffix_separator: str | None = constants.DEFAULT_TABLE_SUFFIX_SEPARATOR,
    ) -> Self:

        """
        Parse a ``TableName`` from a raw string.

        Splits the input string into prefix, name, and suffix components according to the
        given separators. If a separator is falsy (empty string or ``None``) or does not 
        occur in the string, the corresponding component is treated as absent. This 
        matches the behaviour of :meth:`CatalogName.from_string` and 
        :meth:`SchemaName.from_string`.

        Parameters
        ----------
        string : str
            The raw table name string to parse.
        prefix_separator : str or None, optional
            Separator used to split the prefix from the remainder of the string. The 
            split occurs on the first occurrence. Defaults to ``'__'``.
        suffix_separator : str or None, optional
            Separator used to split the suffix from the name. The split occurs on the 
            last occurrence. Defaults to ``''``, meaning no suffix is extracted.

        Returns
        -------
        Self
            A new ``TableName`` with components populated from the string.

        Raises
        ------
        ValueError
            If a parsed component fails validation, e.g. an empty prefix from 
            ``'__customers'`` or an empty name from ``'bronze__'``.

        Examples
        --------
        >>> TableName.from_string('bronze__customers')
        TableName(prefix='bronze', name='customers', suffix=None, prefix_separator='__', suffix_separator='')
        >>> TableName.from_string('customers')
        TableName(prefix=None, name='customers', suffix=None, prefix_separator='__', suffix_separator='')
        """

        prefix, remainder, parsed_prefix_separator = split_prefix(
            string,
            prefix_separator,
        )
        name, suffix, parsed_suffix_separator = split_suffix(
            remainder,
            suffix_separator,
        )

        return cls(
            prefix = prefix,
            prefix_separator = parsed_prefix_separator,
            name = name,
            suffix_separator = parsed_suffix_separator,
            suffix = suffix,
        )


class CatalogSchemaTable(StructWithAttribute, frozen = True, kw_only = True):

    """
    A fully qualified Databricks table reference.

    Represents the three-level namespace of a Unity Catalog table, combining a catalog, a
    schema, and a structured table name. The fully qualified name can be reconstructed 
    via ``str()`` or ``.str``.

    Parameters
    ----------
    catalog : CatalogName
        The catalog component of the reference.
    schema : SchemaName
        The schema component of the reference.
    table : TableName
        The structured table name component.

    Examples
    --------
    >>> ref = CatalogSchemaTable(
    ...     catalog = CatalogName(name = 'sdna_innovation', suffix = 'dev'),
    ...     schema = SchemaName(name = 'dp_nuage_general', suffix = 'core'),
    ...     table = TableName(prefix = 'dim', name = 'input'),
    ... )
    >>> str(ref)
    'sdna_innovation_dev.dp_nuage_general_core.dim__input'
    """

    catalog: CatalogName
    schema: SchemaName
    table: TableName


    def __post_init__(self) -> None:

        """
        Validate the component types after initialisation.

        Raises
        ------
        TypeError
            If ``catalog``, ``schema``, or ``table`` is not an instance of 
            ``CatalogName``, ``SchemaName``, or ``TableName`` respectively.
        """

        if not isinstance(self.catalog, CatalogName):
            raise TypeError('catalog must be an instance of CatalogName.')
        elif not isinstance(self.schema, SchemaName):
            raise TypeError('schema must be an instance of SchemaName.')
        elif not isinstance(self.table, TableName):
            raise TypeError('table must be an instance of TableName.')


    def __str__(self) -> str:

        """
        Render the fully qualified table reference as a string.

        Returns
        -------
        str
            The catalog, schema, and table joined by full stops, e.g. 
            ``'catalog.schema.table'``.
        """

        return constants.NAMESPACE_SEPARATOR.join(
            (str(self.catalog), str(self.schema), str(self.table))
        )


    @overload
    def with_catalog(
        self,
        catalog: CatalogName,
    ) -> Self:

        ...


    @overload
    def with_catalog(
        self,
        catalog: str,
        *,
        suffix_separator: str | None = ...,
    ) -> Self:

        ...


    def with_catalog(
        self,
        catalog: CatalogName | str,
        *,
        suffix_separator: str | None = constants.DEFAULT_CATALOG_SUFFIX_SEPARATOR,
    ) -> Self:

        """
        Return a copy with the catalog replaced.

        Accepts either a ready-made ``CatalogName`` or a raw string. When a string is 
        given, it is parsed into a ``CatalogName`` using the supplied separator; the 
        ``suffix_separator`` argument is ignored when a ``CatalogName`` is passed 
        directly.

        Parameters
        ----------
        catalog : CatalogName or str
            The new catalog component. If a ``CatalogName``, it is used as-is. If a 
            string, it is parsed via :meth:`CatalogName.from_string`.
        suffix_separator : str or None, optional
            Separator used to split the suffix when ``catalog`` is a string. The split 
            occurs on the last occurrence. If falsy, no suffix is extracted. Ignored when 
            ``catalog`` is a ``CatalogName``. Defaults to ``'_'``.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated catalog.

        Raises
        ------
        ValueError
            If ``catalog`` is a string and a parsed component fails validation, as 
            propagated from :meth:`CatalogName.from_string`.
        """

        if isinstance(catalog, CatalogName):
            catalog_obj = catalog
        else:
            catalog_obj = CatalogName.from_string(
                catalog,
                suffix_separator = suffix_separator,
            )

        return self.with_attribute(catalog = catalog_obj)


    @overload
    def with_schema(
        self,
        schema: SchemaName,
    ) -> Self:

        ...


    @overload
    def with_schema(
        self,
        schema: str,
        *,
        suffix_separator: str | None = ...,
    ) -> Self:

        ...


    def with_schema(
        self,
        schema: SchemaName | str,
        *,
        suffix_separator: str | None = constants.DEFAULT_SCHEMA_SUFFIX_SEPARATOR,
    ) -> Self:

        """
        Return a copy with the schema replaced.

        Accepts either a ready-made ``SchemaName`` or a raw string. When a string is 
        given, it is parsed into a ``SchemaName`` using the supplied separator; the 
        ``suffix_separator`` argument is ignored when a ``SchemaName`` is passed 
        directly.

        Parameters
        ----------
        schema : SchemaName or str
            The new schema component. If a ``SchemaName``, it is used as-is. If a string, 
            it is parsed via :meth:`SchemaName.from_string`.
        suffix_separator : str or None, optional
            Separator used to split the suffix when ``schema`` is a string. The split
            occurs on the last occurrence. If falsy, no suffix is extracted. Ignored when 
            ``schema`` is a ``SchemaName``. Defaults to ``'_'``.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated schema.

        Raises
        ------
        ValueError
            If ``schema`` is a string and a parsed component fails validation, as 
            propagated from :meth:`SchemaName.from_string`.
        """

        if isinstance(schema, SchemaName):
            schema_obj = schema
        else:
            schema_obj = SchemaName.from_string(
                schema,
                suffix_separator = suffix_separator,
            )

        return self.with_attribute(schema = schema_obj)


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
        *,
        prefix_separator: str | None = ...,
        suffix_separator: str | None = ...,
    ) -> Self:

        ...


    def with_table(
        self,
        table: TableName | str,
        *,
        prefix_separator: str | None = constants.DEFAULT_TABLE_PREFIX_SEPARATOR,
        suffix_separator: str | None = constants.DEFAULT_TABLE_SUFFIX_SEPARATOR,
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
            occurs on the last occurrence. If falsy, no suffix is extracted. Ignored when 
            ``table`` is a ``TableName``. Defaults to ``''``.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated table.

        Raises
        ------
        ValueError
            If ``table`` is a string and a parsed component fails validation, as 
            propagated from :meth:`TableName.from_string`.

        Examples
        --------
        >>> ref = CatalogSchemaTable(
        ...     catalog = CatalogName(name = 'main'),
        ...     schema = SchemaName(name = 'sales'),
        ...     table = TableName(prefix = 'bronze', name = 'customers'),
        ... )
        >>> str(ref.with_table('silver__orders'))
        'main.sales.silver__orders'
        >>> str(ref.with_table(TableName(name = 'raw')))
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
        **kwargs : str or None
            Field names and values to replace on the nested ``TableName``. Each key must 
            correspond to an existing ``TableName`` field.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` with the updated table.

        Raises
        ------
        TypeError
            If any key does not correspond to a field on ``TableName``, or if a value 
            has an invalid type.
        ValueError
            If a new value fails ``TableName`` validation.
        """

        new_table = self.table.with_attribute(**kwargs)
        return self.with_attribute(table = new_table)


    def with_table_prefix(
        self,
        prefix: str | None,
    ) -> Self:

        """
        Return a copy with the nested table's prefix replaced.

        Parameters
        ----------
        prefix : str or None
            The new prefix value for the nested ``TableName``. Set to ``None`` to 
            remove the prefix.

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
        suffix: str | None,
    ) -> Self:

        """
        Return a copy with the nested table's suffix replaced.

        Parameters
        ----------
        suffix : str or None
            The new suffix value for the nested ``TableName``. Set to ``None`` to 
            remove the suffix.

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
        *,
        catalog_suffix_separator: str | None = constants.DEFAULT_CATALOG_SUFFIX_SEPARATOR,
        schema_suffix_separator: str | None = constants.DEFAULT_SCHEMA_SUFFIX_SEPARATOR,
        table_prefix_separator: str | None = constants.DEFAULT_TABLE_PREFIX_SEPARATOR,
        table_suffix_separator: str | None = constants.DEFAULT_TABLE_SUFFIX_SEPARATOR,
    ) -> Self:

        """
        Parse a ``CatalogSchemaTable`` from a fully qualified string.

        Splits the input on full stops into catalog, schema, and table components, then 
        parses each component using the given separators. Missing separators are treated 
        consistently across all three components: the corresponding prefix or suffix is 
        absent.

        Parameters
        ----------
        string : str
            The fully qualified reference, of the form ``'catalog.schema.table'``.
        catalog_suffix_separator : str or None, optional
            Separator passed to :meth:`CatalogName.from_string` for extracting the 
            catalog suffix. Defaults to ``'_'``.
        schema_suffix_separator : str or None, optional
            Separator passed to :meth:`SchemaName.from_string` for extracting the schema 
            suffix. Defaults to ``'_'``.
        table_prefix_separator : str or None, optional
            Separator passed to :meth:`TableName.from_string` for extracting the table 
            prefix. Defaults to ``'__'``.
        table_suffix_separator : str or None, optional
            Separator passed to :meth:`TableName.from_string` for extracting the table 
            suffix. Defaults to ``''``, meaning no suffix is extracted.

        Returns
        -------
        Self
            A new ``CatalogSchemaTable`` parsed from the string.

        Raises
        ------
        ValueError
            If the string does not contain exactly two full stops, or if any parsed 
            component fails validation (e.g. an empty schema from ``'main..table'``).

        Examples
        --------
        >>> str(CatalogSchemaTable.from_string('main.sales.bronze__customers'))
        'main.sales.bronze__customers'
        >>> str(CatalogSchemaTable.from_string('main.sales.customers'))
        'main.sales.customers'
        """

        try:
            catalog, schema, table = string.split(constants.NAMESPACE_SEPARATOR)
        except ValueError as exc:
            raise ValueError('string must contain exactly two full stops.') from exc

        catalog_name = CatalogName.from_string(
            string = catalog,
            suffix_separator = catalog_suffix_separator,
        )

        schema_name = SchemaName.from_string(
            string = schema,
            suffix_separator = schema_suffix_separator,
        )

        table_name = TableName.from_string(
            table,
            prefix_separator = table_prefix_separator,
            suffix_separator = table_suffix_separator,
        )

        return cls(
            catalog = catalog_name,
            schema = schema_name,
            table = table_name,
        )