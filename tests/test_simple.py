import pytest
from sentry_sdk import get_current_scope, new_scope

from ktx import ctx_wrap, get_current_ctx_or_none
from ktx.simple import SimpleContext, SimpleContextData
from ktx.user import ContextUser


class TestSimpleData:
    def test_set(self):
        data = SimpleContextData()
        data.attr1 = "val1"
        data.attr2 = "val2"

        assert data.attr1 == "val1"
        assert data.attr2 == "val2"

    def test_to_dict(self):
        data = SimpleContextData()
        data.attr1 = "val1"
        data.attr2 = "val2"

        d = data.to_dict()

        assert d == {
            "attr1": "val1",
            "attr2": "val2",
        }

    def test_copy_from_other(self):
        data1 = SimpleContextData()
        data1.attr1 = "val1"
        data1.attr2 = "val2"

        data2 = SimpleContextData()
        data2.attr2 = "val3"
        data2.attr3 = "val4"

        data1.copy_from(data2.to_dict())

        assert data1.to_dict() == {
            "attr1": "val1",
            "attr2": "val3",
            "attr3": "val4",
        }

    def test_to_dict_immutable(self):
        data1 = SimpleContextData()
        data1.attr1 = "val1"
        data1.attr2 = "val2"

        d = data1.to_dict()
        with pytest.raises(TypeError):
            d["qwe"] = "qweqwe"  # type: ignore[index]

    def test_sentry_scope(self):
        with new_scope():
            data1 = SimpleContextData()
            data1.attr1 = "val1"
            data1.attr2 = "val2"
            data1._private = "val3"

            scope = get_current_scope()
            assert scope._extras["attr1"] == "val1"
            assert scope._extras["attr2"] == "val2"
            assert "_private" not in scope._extras


class TestSimple:
    def test_make(self):
        ctx = SimpleContext("some-trace-id")
        assert ctx.uq_id() == "some-trace-id"
        assert ctx.get_user() is not None
        assert isinstance(ctx.get_user(), ContextUser)

        assert get_current_ctx_or_none() is None

    def test_make_empty_trace(self):
        ctx = SimpleContext()
        assert ctx.uq_id() is not None
        assert ctx.uq_id() != "0x0"
        assert isinstance(ctx.uq_id(), str)

    def test_make_with_user_data(self):
        user = ContextUser(username="some-username")

        data = SimpleContextData()

        ctx = SimpleContext("some-trace-id", user=user, data=data)
        assert ctx.uq_id() == "some-trace-id"
        assert ctx.get_user() is user
        assert ctx.data is data

    def test_ctx_manager(self):
        assert get_current_ctx_or_none() is None
        assert "uq_id" not in get_current_scope()._tags

        with ctx_wrap(SimpleContext()) as ctx:
            assert get_current_ctx_or_none() is ctx
            assert get_current_ctx_or_none(SimpleContext) is ctx

            assert get_current_scope()._tags["uq_id"] == ctx.uq_id()

        assert get_current_ctx_or_none() is None
        assert "uq_id" not in get_current_scope()._tags

    def test_inherit(self):
        with ctx_wrap(SimpleContext()) as parent_ctx:
            parent_ctx.data.attr1 = "val1"
            parent_ctx.data.attr2 = "val2"

            with ctx_wrap(SimpleContext()) as child_ctx:
                assert child_ctx.data.attr1 == "val1"
                assert child_ctx.data.attr2 == "val2"

                child_ctx.data.attr2 = "val3"
                assert child_ctx.data.attr2 == "val3"

            assert parent_ctx.data.attr2 == "val2"
