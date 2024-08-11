import pytest
from sentry_sdk import get_current_scope, new_scope

from ktx.simple import SimpleContextDataObject


class TestSimpleData:
    def test_set(self):
        data = SimpleContextDataObject()
        data.attr1 = "val1"
        data.attr2 = "val2"

        assert data.attr1 == "val1"
        assert data.attr2 == "val2"

    def test_to_dict(self):
        data = SimpleContextDataObject()
        data.attr1 = "val1"
        data.attr2 = "val2"

        d = data.to_dict()

        assert d == {
            "attr1": "val1",
            "attr2": "val2",
        }

    def test_copy_from_other(self):
        data1 = SimpleContextDataObject()
        data1.attr1 = "val1"
        data1.attr2 = "val2"

        data2 = SimpleContextDataObject()
        data2.attr2 = "val3"
        data2.attr3 = "val4"

        data1.copy_from(data2)

        assert data1.to_dict() == {
            "attr1": "val1",
            "attr2": "val3",
            "attr3": "val4",
        }

    def test_to_dict_immutable(self):
        data1 = SimpleContextDataObject()
        data1.attr1 = "val1"
        data1.attr2 = "val2"

        d = data1.to_dict()
        with pytest.raises(TypeError):
            d["qwe"] = "qweqwe"  # type: ignore[index]

    def test_sentry_scope(self):
        with new_scope():
            data1 = SimpleContextDataObject()
            data1.attr1 = "val1"
            data1.attr2 = "val2"
            data1._private = "val3"

            scope = get_current_scope()
            assert scope._extras["attr1"] == "val1"
            assert scope._extras["attr2"] == "val2"
            assert "_private" not in scope._extras
