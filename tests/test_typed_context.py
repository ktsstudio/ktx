from typing import TYPE_CHECKING

import pytest

from ktx import ctx_bind
from ktx.ctx import Context, ContextFactory

if TYPE_CHECKING:
    from typing_extensions import assert_type


class OrderContext(Context):
    order_id: int | None = None
    user_id: int | None = None


class ChildContext(OrderContext):
    line_id: str | None = None


if TYPE_CHECKING:
    typed_ctx = ContextFactory(context_type=OrderContext).create()
    assert_type(typed_ctx, OrderContext)
    assert_type(typed_ctx.order_id, int | None)
    assert_type(typed_ctx.user_id, int | None)
    assert_type(ContextFactory().create(), Context)


def test_annotated_fields_share_data_with_get_and_set() -> None:
    ctx = OrderContext("id")
    ctx.order_id = 42
    ctx.user_id = None

    assert ctx.get_data() == {
        "order_id": 42,
        "user_id": None,
    }

    ctx.set("order_id", 43)
    ctx.set("user_id", 7)
    assert ctx.order_id == 43
    assert ctx.user_id == 7


def test_explicit_none_defaults() -> None:
    ctx = OrderContext("id")
    assert ctx.order_id is None
    assert ctx.user_id is None
    assert ctx.get_data() == {"order_id": None, "user_id": None}


def test_child_fields_and_factory_preserve_context_type_and_inheritance() -> None:
    factory = ContextFactory(context_type=ChildContext)
    parent = factory.create("parent")
    parent.order_id = 42

    with ctx_bind(parent):
        child = factory.create("child")

    child.line_id = "line-1"
    assert isinstance(child, ChildContext)
    assert child.order_id == 42
    assert child.line_id == "line-1"
    assert child.user_id is None
    assert parent.get("line_id") is None


def test_annotated_fields_do_not_validate_runtime_types() -> None:
    ctx = OrderContext("id")
    ctx.set("order_id", "wrong")
    assert ctx.order_id == "wrong"


def test_annotated_fields_support_defaults_per_instance() -> None:
    class DefaultContext(Context):
        order_id: int | None = 42
        tags: list[str] | None = []
        user_id: int | None = None

    first = DefaultContext("first")
    second = DefaultContext("second", data={"order_id": 7})
    assert first.get_data() == {"order_id": 42, "tags": [], "user_id": None}
    assert second.get_data() == {"order_id": 7, "tags": [], "user_id": None}
    assert first.tags is not None
    first.tags.append("only-first")
    assert second.tags == []

    class ChildDefaultContext(DefaultContext):
        order_id: int | None = 99

    assert ChildDefaultContext("child").get_data() == {
        "order_id": 99,
        "tags": [],
        "user_id": None,
    }

    class ResetDefaultContext(DefaultContext):
        order_id: int | None = None

    assert ResetDefaultContext("reset").order_id is None


def test_annotated_fields_require_explicit_defaults() -> None:
    with pytest.raises(TypeError, match="requires an explicit default"):

        class MissingDefaultContext(Context):
            order_id: int | None

    with pytest.raises(TypeError, match="requires an explicit default"):

        class MissingOverrideDefaultContext(OrderContext):
            order_id: int | None


def test_annotated_fields_cannot_shadow_context_methods() -> None:
    with pytest.raises(TypeError, match="shadows a Context member"):

        class ShadowContext(Context):
            get: str  # type: ignore[assignment]
