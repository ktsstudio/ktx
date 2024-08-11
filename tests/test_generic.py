import pytest
from sentry_sdk import get_current_scope

from ktx import get_current_ctx_or_none
from ktx.abc import AbstractData
from ktx.generic import GenericContext
from ktx.simple import SimpleContext, SimpleContextDataObject
from ktx.user import ContextUser


class Bar(AbstractData):
    pass


class BarContext(GenericContext[Bar]):
    pass


class TestGeneric:
    def test_make(self):
        ctx = SimpleContext("some-trace-id")
        assert ctx.uq_id == "some-trace-id"
        assert ctx.user is not None
        assert isinstance(ctx.user, ContextUser)
        assert ctx._token is None

        assert get_current_ctx_or_none() is None

    def test_make_empty_trace(self):
        ctx = SimpleContext()
        assert ctx.uq_id is not None
        assert ctx.uq_id != "0x0"
        assert isinstance(ctx.uq_id, str)

    def test_make_with_user_data(self):
        user = ContextUser(username="some-username")

        data = SimpleContextDataObject()

        ctx = SimpleContext("some-trace-id", user=user, data=data)
        assert ctx.uq_id == "some-trace-id"
        assert ctx.user is user
        assert ctx.data is data

    def test_ctx_manager(self):
        assert get_current_ctx_or_none() is None
        assert "uq_id" not in get_current_scope()._tags

        with SimpleContext() as ctx:
            assert get_current_ctx_or_none() is ctx

            assert get_current_scope()._tags["uq_id"] == ctx.uq_id

        assert get_current_ctx_or_none() is None
        assert "uq_id" not in get_current_scope()._tags

    def test_inherit(self):
        with SimpleContext() as parent_ctx:
            parent_ctx.data.attr1 = "val1"
            parent_ctx.data.attr2 = "val2"

            with SimpleContext() as child_ctx:
                assert child_ctx.data.attr1 == "val1"
                assert child_ctx.data.attr2 == "val2"

                child_ctx.data.attr2 = "val3"
                assert child_ctx.data.attr2 == "val3"

            assert parent_ctx.data.attr2 == "val2"

    def test_inherit_invalid_type(self):
        with SimpleContext() as parent_ctx:
            parent_ctx.data.attr1 = "val1"
            parent_ctx.data.attr2 = "val2"

            with pytest.raises(ValueError) as e:
                with BarContext():
                    raise RuntimeError("unreachable")

            assert (
                str(e.value)
                == "cannot inherit data from type <class 'ktx.simple.SimpleContextDataObject'> to different type <class 'tests.test_generic.Bar'>"
            )
