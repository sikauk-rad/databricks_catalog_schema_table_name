import pytest

from databricks_catalog_schema_table_name.parsing import split_prefix, split_suffix


class TestSplitPrefix:
    def test_splits_on_separator(self):
        assert split_prefix("bronze__customers", "__") == ("bronze", "customers", "__")

    def test_splits_on_first_occurrence(self):
        assert split_prefix("a__b__c", "__") == ("a", "b__c", "__")

    def test_separator_not_found_keeps_separator(self):
        assert split_prefix("customers", "__") == (None, "customers", "__")

    @pytest.mark.parametrize("separator", [None, ""])
    def test_falsy_separator_normalised_to_empty(self, separator):
        assert split_prefix("bronze__customers", separator) == (
            None,
            "bronze__customers",
            "",
        )


class TestSplitSuffix:
    def test_splits_on_separator(self):
        assert split_suffix("orders_hist", "_") == ("orders", "hist", "_")

    def test_splits_on_last_occurrence(self):
        assert split_suffix("my_orders_hist", "_") == ("my_orders", "hist", "_")

    def test_separator_not_found_keeps_separator(self):
        assert split_suffix("orders", "_") == ("orders", None, "_")

    @pytest.mark.parametrize("separator", [None, ""])
    def test_falsy_separator_normalised_to_empty(self, separator):
        assert split_suffix("orders_hist", separator) == ("orders_hist", None, "")