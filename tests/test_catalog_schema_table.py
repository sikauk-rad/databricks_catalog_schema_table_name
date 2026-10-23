import re

import pytest

from databricks_catalog_schema_table_name import (
    CatalogName,
    CatalogSchemaTable,
    SchemaName,
    TableName,
)


class TestConstruction:
    def test_str(self, ref):
        assert str(ref) == "main.sales.bronze__customers"

    def test_str_property(self, ref):
        assert ref.str == "main.sales.bronze__customers"

    def test_str_with_suffixes(self):
        ref = CatalogSchemaTable(
            catalog=CatalogName(name="sdna_innovation", suffix="dev"),
            schema=SchemaName(name="dp_nuage_general", suffix="core"),
            table=TableName(prefix="dim", name="input"),
        )
        assert str(ref) == "sdna_innovation_dev.dp_nuage_general_core.dim__input"

    @pytest.mark.parametrize(
        ("kwargs", "message"),
        [
            (
                {"catalog": "main", "schema": SchemaName(name="s"),
                 "table": TableName(name="t")},
                "catalog must be an instance of CatalogName.",
            ),
            (
                {"catalog": CatalogName(name="c"), "schema": "sales",
                 "table": TableName(name="t")},
                "schema must be an instance of SchemaName.",
            ),
            (
                {"catalog": CatalogName(name="c"), "schema": SchemaName(name="s"),
                 "table": "customers"},
                "table must be an instance of TableName.",
            ),
            (
                {"catalog": SchemaName(name="c"), "schema": SchemaName(name="s"),
                 "table": TableName(name="t")},
                "catalog must be an instance of CatalogName.",
            ),
        ],
    )
    def test_wrong_types_raise(self, kwargs, message):
        with pytest.raises(TypeError, match=re.escape(message)):
            CatalogSchemaTable(**kwargs)


class TestWithCatalog:
    def test_with_string(self, ref):
        updated = ref.with_catalog("prod")

        assert updated.catalog == CatalogName(name="prod")
        assert str(updated) == "prod.sales.bronze__customers"
        assert str(ref) == "main.sales.bronze__customers"

    def test_with_string_parses_suffix(self, ref):
        updated = ref.with_catalog("main_prod")

        assert updated.catalog == CatalogName(name="main", suffix="prod")
        assert str(updated) == "main_prod.sales.bronze__customers"

    def test_with_string_and_no_suffix_separator(self, ref):
        updated = ref.with_catalog("main_prod", suffix_separator=None)

        assert updated.catalog.name == "main_prod"
        assert updated.catalog.suffix is None

    def test_with_catalog_name_object(self, ref):
        updated = ref.with_catalog(CatalogName(name="main", suffix="dev"))
        assert str(updated) == "main_dev.sales.bronze__customers"

    def test_change_only_catalog_suffix(self, ref):
        updated = ref.with_catalog(ref.catalog.with_suffix("dev"))
        assert str(updated) == "main_dev.sales.bronze__customers"

    def test_invalid_string_raises(self, ref):
        with pytest.raises(ValueError, match=re.escape("name must be a non-empty string.")):
            ref.with_catalog("")


class TestWithSchema:
    def test_with_string(self, ref):
        updated = ref.with_schema("analytics")

        assert updated.schema == SchemaName(name="analytics")
        assert str(updated) == "main.analytics.bronze__customers"
        assert ref.schema.name == "sales"

    def test_with_string_parses_suffix(self, ref):
        updated = ref.with_schema("dp_nuage_general_core")

        assert updated.schema == SchemaName(name="dp_nuage_general", suffix="core")

    def test_with_string_and_no_suffix_separator(self, ref):
        updated = ref.with_schema("dp_nuage_general_core", suffix_separator=None)

        assert updated.schema.name == "dp_nuage_general_core"
        assert updated.schema.suffix is None

    def test_with_schema_name_object(self, ref):
        updated = ref.with_schema(SchemaName(name="analytics", suffix="core"))
        assert str(updated) == "main.analytics_core.bronze__customers"


class TestWithTable:
    def test_with_table_name_object(self, ref):
        updated = ref.with_table(TableName(prefix="gold", name="orders"))
        assert str(updated) == "main.sales.gold__orders"

    def test_with_string(self, ref):
        updated = ref.with_table("gold__orders")

        assert updated.table == TableName(prefix="gold", name="orders")
        assert str(updated) == "main.sales.gold__orders"

    def test_with_string_and_suffix_separator(self, ref):
        updated = ref.with_table(
            "gold__orders_hist",
            prefix_separator="__",
            suffix_separator="_",
        )

        assert updated.table.prefix == "gold"
        assert updated.table.name == "orders"
        assert updated.table.suffix == "hist"
        assert str(updated) == "main.sales.gold__orders_hist"

    def test_with_string_without_prefix(self, ref):
        updated = ref.with_table("orders")

        assert updated.table.prefix is None
        assert str(updated) == "main.sales.orders"

    def test_invalid_string_raises(self, ref):
        with pytest.raises(
            ValueError, match=re.escape("prefix must be a non-empty string or None.")
        ):
            ref.with_table("__orders")


class TestWithTableParts:
    def test_with_table_attribute(self, ref):
        updated = ref.with_table_attribute(prefix="silver", name="orders")

        assert str(updated) == "main.sales.silver__orders"
        assert str(ref) == "main.sales.bronze__customers"

    def test_with_table_attribute_invalid_raises_type_error(self, ref):
        with pytest.raises(TypeError, match="attributes not recognised: wrong_field"):
            ref.with_table_attribute(wrong_field="x")

    def test_with_table_attribute_validates(self, ref):
        with pytest.raises(ValueError, match=re.escape("prefix must not contain ..")):
            ref.with_table_attribute(prefix="a.b")

    def test_with_table_prefix(self, ref):
        assert str(ref.with_table_prefix("silver")) == "main.sales.silver__customers"

    def test_with_table_prefix_none(self, ref):
        assert str(ref.with_table_prefix(None)) == "main.sales.customers"

    def test_with_table_name(self, ref):
        assert str(ref.with_table_name("orders")) == "main.sales.bronze__orders"

    def test_with_table_suffix(self, ref):
        assert str(ref.with_table_suffix("hist")) == "main.sales.bronze__customershist"

    def test_with_table_prefix_separator(self, ref):
        assert str(ref.with_table_prefix_separator("_")) == "main.sales.bronze_customers"

    def test_with_table_suffix_separator(self, ref):
        updated = ref.with_table_suffix("hist").with_table_suffix_separator("_")
        assert str(updated) == "main.sales.bronze__customers_hist"


class TestWithAttribute:
    def test_rejects_plain_string_for_catalog(self, ref):
        with pytest.raises(
            TypeError, match=re.escape("catalog must be an instance of CatalogName.")
        ):
            ref.with_attribute(catalog="prod")

    def test_rejects_unknown_field(self, ref):
        with pytest.raises(TypeError, match="attributes not recognised: database"):
            ref.with_attribute(database="x")

    def test_chaining(self, ref):
        updated = ref.with_catalog("prod").with_schema("analytics").with_table_prefix(
            "gold"
        )
        assert str(updated) == "prod.analytics.gold__customers"


class TestFromString:
    def test_default(self, ref):
        parsed = CatalogSchemaTable.from_string("main.sales.bronze__customers")

        assert parsed == ref
        assert parsed.table.suffix is None

    def test_parses_catalog_and_schema_suffixes(self):
        parsed = CatalogSchemaTable.from_string(
            "sdna_innovation_dev.dp_nuage_general_core.dim__input"
        )

        assert parsed.catalog == CatalogName(name="sdna_innovation", suffix="dev")
        assert parsed.schema == SchemaName(name="dp_nuage_general", suffix="core")
        assert parsed.table == TableName(prefix="dim", name="input")

    def test_with_table_suffix(self):
        parsed = CatalogSchemaTable.from_string(
            "main.sales.silver__orders_hist",
            table_prefix_separator="__",
            table_suffix_separator="_",
        )

        assert parsed.table.prefix == "silver"
        assert parsed.table.name == "orders"
        assert parsed.table.suffix == "hist"

    def test_all_separators_disabled(self):
        parsed = CatalogSchemaTable.from_string(
            "my_catalog.my_schema.my__table",
            catalog_suffix_separator=None,
            schema_suffix_separator=None,
            table_prefix_separator=None,
            table_suffix_separator=None,
        )

        assert parsed.catalog.name == "my_catalog"
        assert parsed.catalog.suffix is None
        assert parsed.schema.name == "my_schema"
        assert parsed.schema.suffix is None
        assert parsed.table.prefix is None
        assert parsed.table.name == "my__table"

    @pytest.mark.parametrize(
        "string",
        ["main.sales", "main", "main.sales.extra.table"],
    )
    def test_wrong_number_of_parts_raises(self, string):
        with pytest.raises(
            ValueError, match=re.escape("string must contain exactly two full stops.")
        ):
            CatalogSchemaTable.from_string(string)

    @pytest.mark.parametrize(
        "string",
        ["main..customers", ".sales.customers", "main.sales."],
    )
    def test_empty_part_raises(self, string):
        with pytest.raises(ValueError, match=re.escape("name must be a non-empty string.")):
            CatalogSchemaTable.from_string(string)

    def test_propagates_table_parsing_error(self):
        with pytest.raises(
            ValueError, match=re.escape("prefix must be a non-empty string or None.")
        ):
            CatalogSchemaTable.from_string("main.sales.__customers")

    @pytest.mark.parametrize(
        "string",
        [
            "main.sales.customers",
            "main.sales.bronze__customers",
            "sdna_innovation_dev.dp_nuage_general_core.dim__input",
            "a_b_c.d_e_f.g__h__i",
        ],
    )
    def test_round_trip(self, string):
        assert str(CatalogSchemaTable.from_string(string)) == string


class TestBehaviour:
    def test_is_frozen(self, ref):
        with pytest.raises(AttributeError):
            ref.catalog = CatalogName(name="prod")

    def test_equal_and_hashable(self, ref):
        other = CatalogSchemaTable.from_string("main.sales.bronze__customers")

        assert ref == other
        assert len({ref, other}) == 1