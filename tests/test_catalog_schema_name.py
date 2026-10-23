import re

import pytest

from databricks_catalog_schema_table_name import CatalogName, SchemaName


@pytest.fixture(params=[CatalogName, SchemaName], ids=["CatalogName", "SchemaName"])
def name_cls(request):
    """Run every test for both CatalogName and SchemaName."""
    return request.param


class TestDefaults:
    def test_defaults(self, name_cls):
        obj = name_cls(name="main")
        assert obj.name == "main"
        assert obj.suffix is None
        assert obj.suffix_separator == "_"

    def test_requires_keyword_arguments(self, name_cls):
        with pytest.raises(TypeError):
            name_cls("main")


class TestStr:
    def test_without_suffix(self, name_cls):
        assert str(name_cls(name="main")) == "main"

    def test_with_suffix(self, name_cls):
        assert str(name_cls(name="sdna_innovation", suffix="dev")) == "sdna_innovation_dev"

    def test_with_custom_separator(self, name_cls):
        obj = name_cls(name="main", suffix="dev", suffix_separator="__")
        assert str(obj) == "main__dev"

    def test_with_empty_separator(self, name_cls):
        obj = name_cls(name="main", suffix="dev", suffix_separator="")
        assert str(obj) == "maindev"

    def test_str_property(self, name_cls):
        assert name_cls(name="main", suffix="dev").str == "main_dev"


class TestWithMethods:
    def test_with_name(self, name_cls):
        obj = name_cls(name="main", suffix="dev")
        updated = obj.with_name("other")

        assert str(updated) == "other_dev"
        assert obj.name == "main"

    def test_with_suffix(self, name_cls):
        obj = name_cls(name="main", suffix="dev")
        updated = obj.with_suffix("prod")

        assert str(updated) == "main_prod"
        assert obj.suffix == "dev"

    def test_with_suffix_none_removes_suffix(self, name_cls):
        updated = name_cls(name="main", suffix="dev").with_suffix(None)
        assert updated.suffix is None
        assert str(updated) == "main"

    def test_with_suffix_separator(self, name_cls):
        obj = name_cls(name="main", suffix="dev")
        updated = obj.with_suffix_separator("__")

        assert str(updated) == "main__dev"
        assert obj.suffix_separator == "_"

    def test_with_methods_keep_the_same_class(self, name_cls):
        updated = name_cls(name="main").with_suffix("dev")
        assert type(updated) is name_cls

    def test_with_methods_still_validate(self, name_cls):
        with pytest.raises(ValueError, match=re.escape("name must be a non-empty string.")):
            name_cls(name="main").with_name("")

    def test_with_attribute_invalid_raises_type_error(self, name_cls):
        with pytest.raises(TypeError, match="attributes not recognised: wrong_field"):
            name_cls(name="main").with_attribute(wrong_field="x")


class TestFromString:
    def test_splits_suffix_on_last_separator(self, name_cls):
        obj = name_cls.from_string("sdna_innovation_dev")

        assert obj.name == "sdna_innovation"
        assert obj.suffix == "dev"
        assert obj.suffix_separator == "_"

    def test_no_separator_in_string_means_no_suffix(self, name_cls):
        obj = name_cls.from_string("main")

        assert obj.name == "main"
        assert obj.suffix is None
        assert obj.suffix_separator == "_"

    @pytest.mark.parametrize("separator", [None, ""])
    def test_falsy_separator_disables_suffix(self, name_cls, separator):
        obj = name_cls.from_string("sdna_innovation_dev", suffix_separator=separator)

        assert obj.name == "sdna_innovation_dev"
        assert obj.suffix is None
        assert obj.suffix_separator == ""

    def test_custom_separator(self, name_cls):
        obj = name_cls.from_string("my_catalog__dev", suffix_separator="__")

        assert obj.name == "my_catalog"
        assert obj.suffix == "dev"

    def test_returns_correct_class(self, name_cls):
        assert type(name_cls.from_string("main_dev")) is name_cls

    def test_empty_name_raises(self, name_cls):
        with pytest.raises(ValueError, match=re.escape("name must be a non-empty string.")):
            name_cls.from_string("_dev")

    def test_empty_suffix_raises(self, name_cls):
        with pytest.raises(
            ValueError, match=re.escape("suffix must be a non-empty string or None.")
        ):
            name_cls.from_string("main_")

    @pytest.mark.parametrize(
        ("string", "separator"),
        [
            ("main", "_"),
            ("main_dev", "_"),
            ("sdna_innovation_dev", "_"),
            ("sdna_innovation_dev", None),
            ("main__dev", "__"),
        ],
    )
    def test_round_trip(self, name_cls, string, separator):
        assert str(name_cls.from_string(string, separator)) == string


class TestValidation:
    @pytest.mark.parametrize(
        ("kwargs", "error", "message"),
        [
            ({"name": ""}, ValueError, "name must be a non-empty string."),
            ({"name": "ma.in"}, ValueError, "name must not contain .."),
            ({"name": 123}, TypeError, "name must be a string."),
            ({"name": "main", "suffix": ""}, ValueError,
             "suffix must be a non-empty string or None."),
            ({"name": "main", "suffix": "d.ev"}, ValueError, "suffix must not contain .."),
            ({"name": "main", "suffix": 1}, TypeError, "suffix must be a string or None."),
            ({"name": "main", "suffix_separator": "."}, ValueError,
             "suffix_separator must not contain .."),
            ({"name": "main", "suffix_separator": None}, TypeError,
             "suffix_separator must be a string."),
        ],
    )
    def test_invalid_values_raise(self, name_cls, kwargs, error, message):
        with pytest.raises(error, match=re.escape(message)):
            name_cls(**kwargs)


class TestBehaviour:
    def test_is_frozen(self, name_cls):
        obj = name_cls(name="main")
        with pytest.raises(AttributeError):
            obj.name = "other"

    def test_equal_and_hashable(self, name_cls):
        a = name_cls(name="main", suffix="dev")
        b = name_cls.from_string("main_dev")

        assert a == b
        assert len({a, b}) == 1

    def test_catalog_and_schema_are_different_types(self):
        assert CatalogName(name="main") != SchemaName(name="main")