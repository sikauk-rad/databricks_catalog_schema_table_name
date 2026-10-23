import pytest

from databricks_catalog_schema_table_name import (
    CatalogName,
    CatalogSchemaTable,
    SchemaName,
    TableName,
)


@pytest.fixture
def ref() -> CatalogSchemaTable:
    """A simple reference: main.sales.bronze__customers"""
    return CatalogSchemaTable(
        catalog=CatalogName(name="main"),
        schema=SchemaName(name="sales"),
        table=TableName(prefix="bronze", name="customers"),
    )