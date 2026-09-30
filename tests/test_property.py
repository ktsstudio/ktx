from typing import TYPE_CHECKING, Any

import pytest

from ktx import KtxProperty
from ktx.ctx import Context

if TYPE_CHECKING:
    from typing_extensions import assert_type


class OrderContext(Context):
    order_id: KtxProperty[int] = KtxProperty[int]()
    user_id: KtxProperty[int | None] = KtxProperty[int | None]()
    external_id: KtxProperty[str | None] = KtxProperty[str | None](alias="legacy_id")


if TYPE_CHECKING:
    assert_type(OrderContext("id").order_id, int)
    assert_type(OrderContext("id").user_id, int | None)


def test_descriptor_and_underlying_context_share_values() -> None:
    ctx = OrderContext("id")
    assert OrderContext.order_id is OrderContext.__dict__["order_id"]
    assert ctx.user_id is None

    ctx.order_id = 42
    ctx.external_id = "external"
    assert ctx.get("order_id") == 42
    assert ctx.get("legacy_id") == "external"

    ctx.set("order_id", 43)
    ctx.set("legacy_id", "other")
    assert ctx.order_id == 43
    assert ctx.external_id == "other"


def test_missing_required_field_and_wrong_types_raise() -> None:
    ctx = OrderContext("id")
    with pytest.raises(AttributeError, match="order_id"):
        _ = ctx.order_id
    with pytest.raises(TypeError, match="order_id"):
        ctx.order_id = "wrong"  # type: ignore[assignment]

    ctx.set("order_id", "wrong")
    with pytest.raises(TypeError, match="order_id"):
        _ = ctx.order_id


def test_unparameterized_or_uncheckable_property_is_rejected() -> None:
    with pytest.raises(TypeError, match="must be parameterized"):

        class UntypedContext(Context):
            value: KtxProperty[Any] = KtxProperty()

    with pytest.raises(TypeError, match="cannot be checked"):

        class NestedContext(Context):
            value = KtxProperty[list[int]]()
