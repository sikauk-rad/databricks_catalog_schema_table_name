import pytest

from databricks_catalog_schema_table_name import CatalogSchemaTable, TableName


class TestTableNameStr:
    def test_str_with_prefix_only(self):
        table = TableName(prefix="bronze", name="customers")
        assert str(table) == "bronze__customers"

    def test_str_with_suffix_only(self):
        table = TableName(
            prefix=None,
            name="customers",
            suffix="hist",
            suffix_separator="_",
        )
        assert str(table) == "customers_hist"

    def test_str_with_prefix_and_suffix(self):
        table = TableName(
            prefix="silver",
            name="orders",
            suffix="hist",
            prefix_separator="__",
            suffix_separator="_",
        )
        assert str(table) == "silver__orders_hist"

    def test_str_without_prefix_or_suffix(self):
        table = TableName(prefix=None, name="customers")
        assert str(table) == "customers"

    def test_str_property(self):
        table = TableName(prefix="bronze", name="customers")
        assert table.str == "bronze__customers"


class TestTableNameWithMethods:
    def test_with_prefix(self):
        table = TableName(prefix="bronze", name="customers")
        updated = table.with_prefix("silver")

        assert updated.prefix == "silver"
        assert updated.name == "customers"
        assert str(updated) == "silver__customers"
        assert table.prefix == "bronze"

    def test_with_name(self):
        table = TableName(prefix="bronze", name="customers")
        updated = table.with_name("orders")

        assert updated.name == "orders"
        assert str(updated) == "bronze__orders"
        assert table.name == "customers"

    def test_with_suffix(self):
        table = TableName(prefix="bronze", name="customers")
        updated = table.with_suffix("hist")

        assert updated.suffix == "hist"
        assert str(updated) == "bronze__customershist"
        assert table.suffix is None

    def test_with_prefix_separator(self):
        table = TableName(prefix="bronze", name="customers")
        updated = table.with_prefix_separator("_")

        assert updated.prefix_separator == "_"
        assert str(updated) == "bronze_customers"
        assert table.prefix_separator == "__"

    def test_with_suffix_separator(self):
        table = TableName(prefix="bronze", name="customers", suffix="hist")
        updated = table.with_suffix_separator("_")

        assert updated.suffix_separator == "_"
        assert str(updated) == "bronze__customers_hist"
        assert table.suffix_separator == ""

    def test_with_attribute_valid(self):
        table = TableName(prefix="bronze", name="customers")
        updated = table.with_attribute(prefix="silver", name="orders")

        assert updated.prefix == "silver"
        assert updated.name == "orders"
        assert str(updated) == "silver__orders"

    def test_with_attribute_invalid_raises_type_error(self):
        table = TableName(prefix="bronze", name="customers")

        with pytest.raises(TypeError, match="unrecognised arguments: wrong_field"):
            table.with_attribute(wrong_field="x")


class TestTableNameFromString:
    def test_from_string_default_prefix_separator(self):
        table = TableName.from_string("bronze__customers")

        assert table.prefix == "bronze"
        assert table.name == "customers"
        assert table.suffix is None
        assert table.prefix_separator == "__"
        assert table.suffix_separator == ""
        assert str(table) == "bronze__customers"

    def test_from_string_with_prefix_and_suffix(self):
        table = TableName.from_string(
            "silver__orders_hist",
            prefix_separator="__",
            suffix_separator="_",
        )

        assert table.prefix == "silver"
        assert table.name == "orders"
        assert table.suffix == "hist"
        assert table.prefix_separator == "__"
        assert table.suffix_separator == "_"
        assert str(table) == "silver__orders_hist"

    def test_from_string_without_prefix_when_prefix_separator_none(self):
        table = TableName.from_string(
            "customers",
            prefix_separator=None,
        )

        assert table.prefix is None
        assert table.name == "customers"
        assert table.suffix is None
        assert table.prefix_separator == ""
        assert table.suffix_separator == ""
        assert str(table) == "customers"

    def test_from_string_without_prefix_when_prefix_separator_empty(self):
        table = TableName.from_string(
            "customers",
            prefix_separator="",
        )

        assert table.prefix is None
        assert table.name == "customers"
        assert table.prefix_separator == ""

    def test_from_string_without_suffix_when_suffix_separator_none(self):
        table = TableName.from_string(
            "bronze__customers",
            prefix_separator="__",
            suffix_separator=None,
        )

        assert table.prefix == "bronze"
        assert table.name == "customers"
        assert table.suffix is None
        assert table.suffix_separator == ""

    def test_from_string_raises_when_prefix_separator_not_found(self):
        with pytest.raises(ValueError, match=r"prefix_separator = '__' not found\."):
            TableName.from_string("customers", prefix_separator="__")

    def test_from_string_raises_when_suffix_separator_not_found(self):
        with pytest.raises(ValueError, match=r"suffix_separator = '_' not found\."):
            TableName.from_string(
                "bronze__customers",
                prefix_separator="__",
                suffix_separator="_",
            )


class TestCatalogSchemaTableStr:
    def test_str(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        assert str(ref) == "main.sales.bronze__customers"

    def test_str_property(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        assert ref.str == "main.sales.bronze__customers"


class TestCatalogSchemaTableWithMethods:
    def test_with_catalog(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        updated = ref.with_catalog("prod")

        assert updated.catalog == "prod"
        assert updated.schema == "sales"
        assert str(updated) == "prod.sales.bronze__customers"
        assert ref.catalog == "main"

    def test_with_schema(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        updated = ref.with_schema("analytics")

        assert updated.schema == "analytics"
        assert str(updated) == "main.analytics.bronze__customers"
        assert ref.schema == "sales"

    def test_with_table_using_table_name(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        updated = ref.with_table(TableName(prefix="gold", name="orders"))

        assert updated.table.prefix == "gold"
        assert updated.table.name == "orders"
        assert str(updated) == "main.sales.gold__orders"

    def test_with_table_using_string(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        updated = ref.with_table("gold__orders")

        assert updated.table.prefix == "gold"
        assert updated.table.name == "orders"
        assert str(updated) == "main.sales.gold__orders"

    def test_with_table_using_string_with_suffix_separator(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        updated = ref.with_table(
            "gold__orders_hist",
            prefix_separator="__",
            suffix_separator="_",
        )

        assert updated.table.prefix == "gold"
        assert updated.table.name == "orders"
        assert updated.table.suffix == "hist"
        assert str(updated) == "main.sales.gold__orders_hist"

    def test_with_table_attribute(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        updated = ref.with_table_attribute(prefix="silver", name="orders")

        assert updated.table.prefix == "silver"
        assert updated.table.name == "orders"
        assert str(updated) == "main.sales.silver__orders"
        assert ref.table.prefix == "bronze"
        assert ref.table.name == "customers"

    def test_with_table_attribute_invalid_raises_type_error(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )

        with pytest.raises(TypeError, match="unrecognised arguments: wrong_field"):
            ref.with_table_attribute(wrong_field="x")

    def test_with_table_prefix(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        updated = ref.with_table_prefix("silver")

        assert updated.table.prefix == "silver"
        assert str(updated) == "main.sales.silver__customers"

    def test_with_table_name(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        updated = ref.with_table_name("orders")

        assert updated.table.name == "orders"
        assert str(updated) == "main.sales.bronze__orders"

    def test_with_table_suffix(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        updated = ref.with_table_suffix("hist")

        assert updated.table.suffix == "hist"
        assert str(updated) == "main.sales.bronze__customershist"

    def test_with_table_prefix_separator(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers"),
        )
        updated = ref.with_table_prefix_separator("_")

        assert updated.table.prefix_separator == "_"
        assert str(updated) == "main.sales.bronze_customers"

    def test_with_table_suffix_separator(self):
        ref = CatalogSchemaTable(
            catalog="main",
            schema="sales",
            table=TableName(prefix="bronze", name="customers", suffix="hist"),
        )
        updated = ref.with_table_suffix_separator("_")

        assert updated.table.suffix_separator == "_"
        assert str(updated) == "main.sales.bronze__customers_hist"


class TestCatalogSchemaTableFromString:
    def test_from_string_default(self):
        ref = CatalogSchemaTable.from_string("main.sales.bronze__customers")

        assert ref.catalog == "main"
        assert ref.schema == "sales"
        assert ref.table.prefix == "bronze"
        assert ref.table.name == "customers"
        assert ref.table.suffix is None
        assert str(ref) == "main.sales.bronze__customers"

    def test_from_string_with_suffix(self):
        ref = CatalogSchemaTable.from_string(
            "main.sales.silver__orders_hist",
            prefix_separator="__",
            suffix_separator="_",
        )

        assert ref.catalog == "main"
        assert ref.schema == "sales"
        assert ref.table.prefix == "silver"
        assert ref.table.name == "orders"
        assert ref.table.suffix == "hist"
        assert str(ref) == "main.sales.silver__orders_hist"

    def test_from_string_raises_when_not_exactly_three_parts(self):
        with pytest.raises(ValueError, match="string must contain exactly two full stops."):
            CatalogSchemaTable.from_string("main.sales")

    def test_from_string_raises_when_too_many_parts(self):
        with pytest.raises(ValueError, match="string must contain exactly two full stops."):
            CatalogSchemaTable.from_string("main.sales.extra.table")

    def test_from_string_propagates_table_parsing_error(self):
        with pytest.raises(ValueError, match=r"prefix_separator = '__' not found\."):
            CatalogSchemaTable.from_string("main.sales.customers", prefix_separator="__")