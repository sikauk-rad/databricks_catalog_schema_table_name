import re

import pytest

from databricks_catalog_schema_table_name.validation import (
    validate_affix,
    validate_name,
    validate_separator,
)


class TestValidateName:
    def test_valid(self):
        validate_name("customers")

    def test_not_a_string(self):
        with pytest.raises(TypeError, match=re.escape("name must be a string.")):
            validate_name(123)

    def test_empty(self):
        with pytest.raises(ValueError, match=re.escape("name must be a non-empty string.")):
            validate_name("")

    def test_contains_dot(self):
        with pytest.raises(ValueError, match=re.escape("name must not contain ..")):
            validate_name("cust.omers")


class TestValidateAffix:
    @pytest.mark.parametrize("value", [None, "dev", "bronze"])
    def test_valid(self, value):
        validate_affix(value, "suffix")

    def test_not_a_string(self):
        with pytest.raises(TypeError, match=re.escape("suffix must be a string or None.")):
            validate_affix(1, "suffix")

    def test_empty(self):
        with pytest.raises(
            ValueError, match=re.escape("prefix must be a non-empty string or None.")
        ):
            validate_affix("", "prefix")

    def test_contains_dot(self):
        with pytest.raises(ValueError, match=re.escape("prefix must not contain ..")):
            validate_affix("a.b", "prefix")


class TestValidateSeparator:
    @pytest.mark.parametrize("value", ["", "_", "__", "-"])
    def test_valid(self, value):
        validate_separator(value, "suffix_separator")

    def test_not_a_string(self):
        with pytest.raises(
            TypeError, match=re.escape("suffix_separator must be a string.")
        ):
            validate_separator(None, "suffix_separator")

    def test_contains_dot(self):
        with pytest.raises(
            ValueError, match=re.escape("prefix_separator must not contain ..")
        ):
            validate_separator(".", "prefix_separator")