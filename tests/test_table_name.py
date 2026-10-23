import re

import pytest

from databricks_catalog_schema_table_name import TableName


class TestDefaults:
    def test_defaults(self):
        table = TableName(name="customers")

        assert table.prefix is None
        assert table.suffix is None
        assert table.prefix_separator == "__"
        assert table.suffix_separator == ""

    def test_requires_keyword_arguments(self):
        with pytest.raises(TypeError):
            TableName("customers")


class TestStr:
    def test_with_prefix_only(self):
        assert str(TableName(prefix="bronze", name="customers")) == "bronze__customers"

    def test_with_suffix_only(self):
        table = TableName(name="customers", suffix="hist", suffix_separator="_")
        assert str(table) == "customers_hist"

    def test_with_prefix_and_suffix(self):
        table = TableName(
            prefix="silver",
            name="orders",
            suffix="hist",
            prefix_separator="__",
            suffix_separator="_",
        )
        assert str(table) == "silver__orders_hist"

    def test_without_prefix_or_suffix(self):
        assert str(TableName(name="customers")) == "customers"

    def test_default_suffix_separator_is_empty(self):
        assert str(TableName(name="customers", suffix="hist")) == "customershist"

    def test_str_property(self):
        assert TableName(prefix="bronze", name="customers").str == "bronze__customers"


class TestWithMethods:
    def test_with_prefix(self):
        table = TableName(prefix="bronze", name="customers")
        updated = table.with_prefix("silver")

        assert str(updated) == "silver__customers"
        assert table.prefix == "bronze"

    def test_with_prefix_none_removes_prefix(self):
        updated = TableName(prefix="bronze", name="customers").with_prefix(None)

        assert updated.prefix is None
        assert str(updated) == "customers"

    def test_with_name(self):
        table = TableName(prefix="bronze", name="customers")
        updated = table.with_name("orders")

        assert str(updated) == "bronze__orders"
        assert table.name == "customers"

    def test_with_suffix(self):
        table = TableName(prefix="bronze", name="customers")
        updated = table.with_suffix("hist")

        assert str(updated) == "bronze__customershist"
        assert table.suffix is None

    def test_with_suffix_none_removes_suffix(self):
        table = TableName(name="customers", suffix="hist", suffix_separator="_")
        assert str(table.with_suffix(None)) == "customers"

    def test_with_prefix_separator(self):
        table = TableName(prefix="bronze", name="customers")
        updated = table.with_prefix_separator("_")

        assert str(updated) == "bronze_customers"
        assert table.prefix_separator == "__"

    def test_with_suffix_separator(self):
        table = TableName(prefix="bronze", name="customers", suffix="hist")
        updated = table.with_suffix_separator("_")

        assert str(updated) == "bronze__customers_hist"
        assert table.suffix_separator == ""

    def test_with_attribute_multiple_fields(self):
        updated = TableName(prefix="bronze", name="customers").with_attribute(
            prefix="silver", name="orders"
        )
        assert str(updated) == "silver__orders"

    def test_with_attribute_invalid_raises_type_error(self):
        with pytest.raises(TypeError, match="attributes not recognised: wrong_field"):
            TableName(name="customers").with_attribute(wrong_field="x")

    def test_with_attribute_lists_bad_fields_sorted(self):
        with pytest.raises(TypeError, match="attributes not recognised: aaa, zzz"):
            TableName(name="customers").with_attribute(zzz=1, aaa=2)

    def test_with_methods_still_validate(self):
        table = TableName(name="customers")

        with pytest.raises(
            ValueError, match=re.escape("prefix must be a non-empty string or None.")
        ):
            table.with_prefix("")

        with pytest.raises(ValueError, match=re.escape("name must not contain ..")):
            table.with_name("a.b")


class TestFromString:
    def test_default_prefix_separator(self):
        table = TableName.from_string("bronze__customers")

        assert table == TableName(prefix="bronze", name="customers")

    def test_with_prefix_and_suffix(self):
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

    def test_prefix_splits_on_first_occurrence(self):
        table = TableName.from_string("bronze__customers__v2")

        assert table.prefix == "bronze"
        assert table.name == "customers__v2"

    def test_suffix_splits_on_last_occurrence(self):
        table = TableName.from_string(
            "silver__daily_orders_hist",
            suffix_separator="_",
        )

        assert table.name == "daily_orders"
        assert table.suffix == "hist"

    def test_missing_prefix_separator_means_no_prefix(self):
        table = TableName.from_string("customers")

        assert table.prefix is None
        assert table.name == "customers"
        assert table.prefix_separator == "__"

    def test_missing_suffix_separator_means_no_suffix(self):
        table = TableName.from_string("bronze__customers", suffix_separator="_")

        assert table.prefix == "bronze"
        assert table.name == "customers"
        assert table.suffix is None
        assert table.suffix_separator == "_"

    @pytest.mark.parametrize("separator", [None, ""])
    def test_falsy_prefix_separator_disables_prefix(self, separator):
        table = TableName.from_string("bronze__customers", prefix_separator=separator)

        assert table.prefix is None
        assert table.name == "bronze__customers"
        assert table.prefix_separator == ""

    @pytest.mark.parametrize("separator", [None, ""])
    def test_falsy_suffix_separator_disables_suffix(self, separator):
        table = TableName.from_string("customers_hist", suffix_separator=separator)

        assert table.suffix is None
        assert table.name == "customers_hist"
        assert table.suffix_separator == ""

    def test_empty_prefix_raises(self):
        with pytest.raises(
            ValueError, match=re.escape("prefix must be a non-empty string or None.")
        ):
            TableName.from_string("__customers")

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match=re.escape("name must be a non-empty string.")):
            TableName.from_string("bronze__")

    def test_empty_suffix_raises(self):
        with pytest.raises(
            ValueError, match=re.escape("suffix must be a non-empty string or None.")
        ):
            TableName.from_string("customers_", suffix_separator="_")

    @pytest.mark.parametrize(
        ("string", "prefix_separator", "suffix_separator"),
        [
            ("bronze__customers", "__", ""),
            ("customers", "__", ""),
            ("silver__orders_hist", "__", "_"),
            ("orders_hist", None, "_"),
            ("a__b__c", "__", ""),
            ("bronze_customers", "_", None),
        ],
    )
    def test_round_trip(self, string, prefix_separator, suffix_separator):
        table = TableName.from_string(string, prefix_separator, suffix_separator)
        assert str(table) == string


class TestValidation:
    @pytest.mark.parametrize(
        ("kwargs", "error", "message"),
        [
            ({"name": ""}, ValueError, "name must be a non-empty string."),
            ({"name": "cust.omers"}, ValueError, "name must not contain .."),
            ({"name": 123}, TypeError, "name must be a string."),
            ({"name": "c", "prefix": ""}, ValueError,
             "prefix must be a non-empty string or None."),
            ({"name": "c", "prefix": "a.b"}, ValueError, "prefix must not contain .."),
            ({"name": "c", "prefix": 1}, TypeError, "prefix must be a string or None."),
            ({"name": "c", "suffix": ""}, ValueError,
             "suffix must be a non-empty string or None."),
            ({"name": "c", "suffix": "a.b"}, ValueError, "suffix must not contain .."),
            ({"name": "c", "prefix_separator": "."}, ValueError,
             "prefix_separator must not contain .."),
            ({"name": "c", "prefix_separator": None}, TypeError,
             "prefix_separator must be a string."),
            ({"name": "c", "suffix_separator": "_._"}, ValueError,
             "suffix_separator must not contain .."),
        ],
    )
    def test_invalid_values_raise(self, kwargs, error, message):
        with pytest.raises(error, match=re.escape(message)):
            TableName(**kwargs)


class TestBehaviour:
    def test_is_frozen(self):
        table = TableName(name="customers")
        with pytest.raises(AttributeError):
            table.name = "orders"

    def test_equal_and_hashable(self):
        a = TableName(prefix="bronze", name="customers")
        b = TableName.from_string("bronze__customers")

        assert a == b
        assert len({a, b}) == 1