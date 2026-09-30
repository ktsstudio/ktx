from typing import Any, Generic, TypeVar, cast, get_args, overload

from .abc import AbstractContext

ValueT = TypeVar("ValueT")


class KtxProperty(Generic[ValueT]):
    """Typed descriptor for a value stored in an :class:`AbstractContext`.

    Use ``KtxProperty[T]()`` so that ``T`` can be checked at runtime. A missing
    value returns ``None`` only when ``T`` permits it; otherwise it raises
    ``AttributeError``. Parameterized containers such as ``list[int]`` are not
    supported because ``isinstance`` cannot validate their contents.
    """

    def __init__(self, *, alias: str | None = None) -> None:
        self._key = alias
        self._value_type: Any = None
        self._allows_none = False

    def __set_name__(self, owner: type[Any], name: str) -> None:
        if self._key is None:
            self._key = name

        args = get_args(getattr(self, "__orig_class__", None))
        if len(args) != 1:
            raise TypeError(
                "KtxProperty must be parameterized, e.g. KtxProperty[int]()"
            )

        self._value_type = args[0]
        if self._value_type is Any:
            self._allows_none = True
            return
        try:
            self._allows_none = isinstance(None, self._value_type)
        except TypeError as exc:
            raise TypeError(
                f"KtxProperty[{self._value_type!r}] cannot be checked at runtime"
            ) from exc

    @overload
    def __get__(
        self, instance: None, owner: type[Any] | None = None
    ) -> "KtxProperty[ValueT]": ...

    @overload
    def __get__(
        self, instance: AbstractContext, owner: type[Any] | None = None
    ) -> ValueT: ...

    def __get__(
        self, instance: AbstractContext | None, owner: type[Any] | None = None
    ) -> "KtxProperty[ValueT] | ValueT":
        if instance is None:
            return self
        key = self._require_key()
        if key not in instance.get_data() and not self._allows_none:
            raise AttributeError(f"context field {key!r} has not been set")
        value = instance.get(key)
        self._check_value(value)
        return cast(ValueT, value)

    def __set__(self, instance: AbstractContext, value: ValueT) -> None:
        self._check_value(value)
        instance.set(self._require_key(), value)

    def _require_key(self) -> str:
        if self._key is None:
            raise RuntimeError("KtxProperty is not bound to a context class")
        return self._key

    def _check_value(self, value: Any) -> None:
        if self._value_type is not Any and not isinstance(value, self._value_type):
            raise TypeError(
                f"context field {self._require_key()!r} requires {self._value_type!r}, "
                f"got {type(value).__name__}"
            )
