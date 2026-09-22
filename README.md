# databricks_catalog_schema_table_name

Simple object-oriented management of Databricks catalog-schema-table names.

This package provides small immutable models for working with:

- table names with optional prefixes and suffixes
- fully qualified Databricks table references in the form `catalog.schema.table`

It is especially useful when you want to manipulate names safely and consistently instead of hand-building strings everywhere.

## Features

- Immutable models using [`msgspec.Struct`](https://jcristharif.com/msgspec/)
- Clear object model for:
  - `TableName`
  - `CatalogSchemaTable`
- Easy string conversion with `str(...)`
- Convenient `with_*` methods for non-mutating updates
- Parsing from strings with configurable separators

## Installation

```bash
pip install databricks_catalog_schema_table_name
```

## Quick start

```python
from databricks_catalog_schema_table_name import TableName, CatalogSchemaTable

table = TableName(prefix="bronze", name="customers")
print(str(table))
# bronze__customers

ref = CatalogSchemaTable(
    catalog="main",
    schema="sales",
    table=table,
)
print(str(ref))
# main.sales.bronze__customers
```

## Models

### `TableName`

Represents a table name with optional:

- `prefix`
- `name`
- `suffix`
- `prefix_separator`
- `suffix_separator`

Example:

```python
from databricks_catalog_schema_table_name import TableName

table = TableName(prefix="silver", name="orders")
print(str(table))
# silver__orders
```

With suffix:

```python
table = TableName(
    prefix="silver",
    name="orders",
    suffix="hist",
    prefix_separator="__",
    suffix_separator="_",
)
print(str(table))
# silver__orders_hist
```

### `CatalogSchemaTable`

Represents a fully qualified Databricks table reference:

```python
from databricks_catalog_schema_table_name import TableName, CatalogSchemaTable

ref = CatalogSchemaTable(
    catalog="main",
    schema="analytics",
    table=TableName(prefix="gold", name="customers"),
)

print(str(ref))
# main.analytics.gold__customers
```

## Parsing from strings

### Parse a `TableName`

```python
from databricks_catalog_schema_table_name import TableName

table = TableName.from_string("bronze__customers")
print(table)
# TableName(prefix='bronze', name='customers', suffix=None, prefix_separator='__', suffix_separator='')
```

With suffix parsing:

```python
table = TableName.from_string(
    "silver__orders_hist",
    prefix_separator="__",
    suffix_separator="_",
)

print(table.prefix)
# silver

print(table.name)
# orders

print(table.suffix)
# hist
```

### Parse a `CatalogSchemaTable`

```python
from databricks_catalog_schema_table_name import CatalogSchemaTable

ref = CatalogSchemaTable.from_string("main.sales.bronze__customers")

print(ref.catalog)
# main

print(ref.schema)
# sales

print(str(ref.table))
# bronze__customers
```

## Non-mutating updates

All models are frozen/immutable. To make changes, use the provided `with_*` methods.

### Update `TableName`

```python
from databricks_catalog_schema_table_name import TableName

table = TableName(prefix="bronze", name="customers")
new_table = table.with_prefix("silver")

print(str(table))
# bronze__customers

print(str(new_table))
# silver__customers
```

Other examples:

```python
table = table.with_name("orders")
table = table.with_suffix("hist")
table = table.with_suffix_separator("_")
```

### Update `CatalogSchemaTable`

```python
from databricks_catalog_schema_table_name import TableName, CatalogSchemaTable

ref = CatalogSchemaTable(
    catalog="main",
    schema="sales",
    table=TableName(prefix="bronze", name="customers"),
)

updated = ref.with_catalog("prod").with_schema("analytics")
print(str(updated))
# prod.analytics.bronze__customers
```

Update the nested table:

```python
updated = ref.with_table_prefix("silver")
print(str(updated))
# main.sales.silver__customers
```

Or replace the table directly:

```python
updated = ref.with_table("gold__orders")
print(str(updated))
# main.sales.gold__orders
```

You can also pass a `TableName` instance:

```python
updated = ref.with_table(TableName(prefix="gold", name="orders"))
print(str(updated))
# main.sales.gold__orders
```

## API overview

### `TableName`

Main fields:

- `prefix: str | None`
- `name: str`
- `suffix: str | None = None`
- `prefix_separator: str = "__"`
- `suffix_separator: str = ""`

Main methods:

- `str(table)` or `table.str`
- `TableName.from_string(...)`
- `with_prefix(...)`
- `with_name(...)`
- `with_suffix(...)`
- `with_prefix_separator(...)`
- `with_suffix_separator(...)`

### `CatalogSchemaTable`

Main fields:

- `catalog: str`
- `schema: str`
- `table: TableName`

Main methods:

- `str(ref)` or `ref.str`
- `CatalogSchemaTable.from_string(...)`
- `with_catalog(...)`
- `with_schema(...)`
- `with_table(...)`
- `with_table_attribute(...)`
- `with_table_prefix(...)`
- `with_table_name(...)`
- `with_table_suffix(...)`
- `with_table_prefix_separator(...)`
- `with_table_suffix_separator(...)`

## Error behavior

### Invalid field replacement

If you call `with_attribute(...)` or `with_table_attribute(...)` with a field name that does not exist, a `TypeError` is raised.

### Parsing errors

Parsing methods raise `ValueError` when expected separators are not found.

Example:

```python
from databricks_catalog_schema_table_name import TableName

TableName.from_string("customers", prefix_separator="__")
# ValueError: prefix_separator = '__' not found.
```

## Why use this package?

Instead of writing code like this:

```python
full_name = f"{catalog}.{schema}.{prefix}__{table}"
```

you can write:

```python
ref = CatalogSchemaTable(
    catalog=catalog,
    schema=schema,
    table=TableName(prefix=prefix, name=table),
)
```

This makes name handling:

- more explicit
- easier to test
- less error-prone
- easier to refactor

## Requirements

- Python 3.10+
- `msgspec`

## Development

Install with development dependencies:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest
```

Type checking:

```bash
mypy src
```

Linting:

```bash
ruff check .
```

## License

MIT license. 

## Author

Milan Kundra