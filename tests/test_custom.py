from typing import Any, Mapping

from ktx import ctx_bind
from ktx._meta import PY311
from ktx.abc import AbstractContext
from ktx.user import ContextUser

if PY311:
    from typing import assert_type  # type: ignore[attr-defined]  # pragma: no cover
else:
    from typing_extensions import assert_type  # pragma: no cover


class CustomContext(AbstractContext):
    def __init__(self, *, custom_field: str):
        self._custom_field = custom_field
        self._data: dict[str, Any] = {}
        self._user = ContextUser()

    def ktx_id(self) -> str:
        return "uqid"  # pragma: no cover

    def get_data(self) -> Mapping[str, Any]:
        return {
            **self._data,
            "custom_field": self._custom_field,
        }

    def get(self, key: str) -> Any:
        return self._data.get(key)  # pragma: no cover

    def set(self, key: str, value: Any):
        self._data[key] = value


class TestCustomContext:
    def test_custom_context(self):
        ctx = CustomContext(custom_field="value1")
        ctx.set("attr1", "value2")
        ctx.set("attr2", "value3")

        assert ctx.get_data() == {
            "custom_field": "value1",
            "attr1": "value2",
            "attr2": "value3",
        }

    def test_custom_wrap(self):
        with ctx_bind(CustomContext(custom_field="value1")) as ctx:
            assert_type(ctx, CustomContext)
            assert isinstance(ctx, CustomContext)

            ctx.set("attr1", "value2")
            ctx.set("attr2", "value3")

            assert ctx.get_data() == {
                "custom_field": "value1",
                "attr1": "value2",
                "attr2": "value3",
            }
