# databricks_catalog_schema_table_name

A small Python helper for working with Databricks table names like:

```
main.sales.bronze__customers
```

Instead of gluing text together by hand, you describe each piece once. 
The package builds the full name for you and checks for common mistakes.

---

## What is a "catalog.schema.table" name?

In Databricks, every table has a three-part address, separated by dots:

```
  catalog   .  schema  .  table
  main      .  sales   .  bronze__customers
```

Each part can have smaller pieces of its own:

| Part        | Pieces it can have                | Example               |
|-------------|-----------------------------------|-----------------------|
| **Catalog** | name, optional suffix             | `sales_dev`           |
| **Schema**  | name, optional suffix             | `reporting_core`      |
| **Table**   | optional prefix, name, optional suffix | `bronze__customers` |

- A **prefix** goes in front of the name (for example `bronze`, `silver`, `gold`).
- A **suffix** goes after the name (for example `dev`, `prod`, `hist`).
- A **separator** is the text placed between pieces (for example `_` or `__`).

---

## Installation

You need **Python 3.11 or newer**.

```bash
pip install databricks_catalog_schema_table_name
```

---

## 1. Build a full table name

```python
from databricks_catalog_schema_table_name import (
    CatalogName,
    SchemaName,
    TableName,
    CatalogSchemaTable,
)

ref = CatalogSchemaTable(
    catalog=CatalogName(name="sales", suffix="dev"),
    schema=SchemaName(name="reporting"),
    table=TableName(prefix="bronze", name="customers"),
)

print(ref)
# sales_dev.reporting.bronze__customers
```

Use it directly in Spark:

```python
df = spark.table(ref.str)
```

> `ref.str` and `str(ref)` both give you the full name as text.

---

## 2. Read an existing table name

Already have the name as text? Turn it into an object:

```python
ref = CatalogSchemaTable.from_string("sales_dev.reporting.bronze__customers")

print(ref.catalog.name)    # sales
print(ref.catalog.suffix)  # dev
print(ref.schema.name)     # reporting
print(ref.table.prefix)    # bronze
print(ref.table.name)      # customers
```

---

## 3. Change one piece

Objects never change in place. Each `with_...` method gives you a **new** object,
and the original stays the same.

```python
ref = CatalogSchemaTable.from_string("sales_dev.reporting.bronze__customers")

# Move from dev to prod
prod = ref.with_catalog(ref.catalog.with_suffix("prod"))
print(prod)   # sales_prod.reporting.bronze__customers

# Move from bronze to silver
silver = ref.with_table_prefix("silver")
print(silver) # sales_dev.reporting.silver__customers

# Point to a different table
orders = ref.with_table("gold__orders")
print(orders) # sales_dev.reporting.gold__orders

# The original is untouched
print(ref)    # sales_dev.reporting.bronze__customers
```

You can chain several changes:

```python
new = ref.with_catalog("main").with_schema("analytics").with_table_name("orders")
print(new)    # main.analytics.bronze__orders
```

### All the "change" methods

| On a full reference (`CatalogSchemaTable`) | What it changes        |
|--------------------------------------------|------------------------|
| `with_catalog(...)`                        | the catalog            |
| `with_schema(...)`                         | the schema             |
| `with_table(...)`                          | the whole table        |
| `with_table_prefix(...)`                   | the table prefix       |
| `with_table_name(...)`                     | the table name         |
| `with_table_suffix(...)`                   | the table suffix       |
| `with_table_prefix_separator(...)`         | text between prefix and name |
| `with_table_suffix_separator(...)`         | text between name and suffix |

`with_catalog`, `with_schema` and `with_table` accept either text or a ready-made
`CatalogName` / `SchemaName` / `TableName`.

`CatalogName`, `SchemaName` and `TableName` have their own `with_name`,
`with_suffix` and `with_suffix_separator` methods. `TableName` also has
`with_prefix` and `with_prefix_separator`.

To remove a prefix or suffix, pass `None`:

```python
ref.with_table_prefix(None)   # sales_dev.reporting.customers
```

---

## Default separators

| Piece                         | Default separator | Example              |
|-------------------------------|-------------------|----------------------|
| Catalog name → suffix         | `_`               | `sales_dev`          |
| Schema name → suffix          | `_`               | `reporting_core`     |
| Table prefix → name           | `__` (two underscores) | `bronze__customers` |
| Table name → suffix           | *(nothing)*       | `customershist`      |

You can change any of them, for example:

```python
table = TableName(prefix="silver", name="orders", suffix="hist", suffix_separator="_")
print(table)  # silver__orders_hist
```

---

## Things to watch out for

**1. Underscores in catalog and schema names.**
When reading text, the **last** `_` is treated as the start of a suffix:

```python
ref = CatalogSchemaTable.from_string("my_catalog.my_schema.customers")
print(ref.catalog.name)    # my
print(ref.catalog.suffix)  # catalog
```

The full name is still correct (`my_catalog.my_schema.customers`).
If you don't use suffixes, switch this off with `None`:

```python
ref = CatalogSchemaTable.from_string(
    "my_catalog.my_schema.customers",
    catalog_suffix_separator=None,
    schema_suffix_separator=None,
)
print(ref.catalog.name)    # my_catalog
```

**2. Table suffixes are not read by default.**
To read `orders_hist` as name `orders` + suffix `hist`, say so:

```python
ref = CatalogSchemaTable.from_string(
    "main.sales.silver__orders_hist",
    table_suffix_separator="_",
)
print(ref.table.suffix)  # hist
```

**3. Adding a table suffix with no separator.**
The default table suffix separator is empty, so `with_table_suffix("hist")` gives
`customershist`. To get `customers_hist`, set the separator too:

```python
ref.with_table_attribute(suffix="hist", suffix_separator="_")
```

**4. Missing separators are fine.**
If the text has no prefix or suffix, that piece is simply left empty (`None`).
No error is raised.

```python
TableName.from_string("customers").prefix   # None
```

---

## Errors you might see

The package stops you from building broken names.

| What you did                                  | Error        |
|-----------------------------------------------|--------------|
| Text with too few or too many dots (`main.sales`) | `ValueError: string must contain exactly two full stops.` |
| An empty piece (`main..customers`, `__customers`) | `ValueError: ... must be a non-empty string` |
| A dot inside a piece (`TableName(name="a.b")`) | `ValueError: ... must not contain .` |
| Plain text where an object is needed (`CatalogSchemaTable(catalog="main", ...)`) | `TypeError: catalog must be an instance of CatalogName.` |
| A field that doesn't exist (`with_attribute(wrong=1)`) | `TypeError: attributes not recognised: wrong` |

> Tip: when building a `CatalogSchemaTable` from scratch, wrap the catalog and
> schema in `CatalogName(...)` and `SchemaName(...)`. Or just use
> `CatalogSchemaTable.from_string("catalog.schema.table")`.

---

## For developers

```bash
pip install -e .[dev]   # install with dev tools
pytest                  # run tests
mypy src                # type checking
ruff check .            # linting
```

---

## License

MIT

## Author

Milan Kundra