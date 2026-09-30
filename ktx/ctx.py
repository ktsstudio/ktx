from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, ClassVar, Generic, TypeVar, cast, overload

from immutabledict import immutabledict

from .abc import (
    AbstractContext,
    AbstractContextDataAdapter,
    AbstractContextFactory,
    KtxIdMaker,
)
from .ktxid import ktxid_uuid4
from .vars import get_current_ctx_or_none


def _data_property(name: str) -> property:
    def getter(self: "Context") -> Any:
        return self.get(name)

    def setter(self: "Context", value: Any) -> None:
        self.set(name, value)

    return property(getter, setter)


class Context(AbstractContext):
    _context_defaults: ClassVar[dict[str, Any]] = {}
    __slots__ = [
        "_ktx_id",
        "_data",
        "_adapters",
    ]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        defaults = dict(cls._context_defaults)
        for name in cls.__dict__.get("__annotations__", {}):
            if name.startswith("_"):
                continue
            if hasattr(Context, name):
                raise TypeError(f"context field {name!r} shadows a Context member")
            if name not in cls.__dict__:
                raise TypeError(f"context field {name!r} requires an explicit default")
            defaults[name] = cls.__dict__[name]
            setattr(cls, name, _data_property(name))
        cls._context_defaults = defaults

    def __init__(
        self,
        ktx_id: str,
        *,
        data: Mapping[str, Any] | None = None,
        adapters: Sequence[AbstractContextDataAdapter] | None = None,
    ):
        self._ktx_id = ktx_id
        self._data: dict[str, Any] = deepcopy(self._context_defaults)
        if data is not None:
            self._data.update(data)
        self._adapters = adapters

    def ktx_id(self) -> str:
        return self._ktx_id

    def get_data(self) -> Mapping[str, Any]:
        return immutabledict(self._data)

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        if self._adapters is not None:
            for adapter in self._adapters:
                adapter.set(key, value)


ContextT = TypeVar("ContextT", bound=Context)


class ContextFactory(Generic[ContextT], AbstractContextFactory[ContextT]):
    __slots__ = [
        "_ktx_id_maker",
        "_inherit_data",
        "_adapters",
        "_context_type",
    ]

    @overload
    def __init__(
        self: "ContextFactory[Context]",
        *,
        ktx_id_maker: KtxIdMaker | None = None,
        inherit_data: bool = True,
        adapters: Sequence[AbstractContextDataAdapter] | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self: "ContextFactory[ContextT]",
        *,
        context_type: type[ContextT],
        ktx_id_maker: KtxIdMaker | None = None,
        inherit_data: bool = True,
        adapters: Sequence[AbstractContextDataAdapter] | None = None,
    ) -> None: ...

    def __init__(
        self,
        *,
        context_type: type[ContextT] | None = None,
        ktx_id_maker: KtxIdMaker | None = None,
        inherit_data: bool = True,
        adapters: Sequence[AbstractContextDataAdapter] | None = None,
    ):
        self._context_type = cast(type[ContextT], context_type or Context)
        self._ktx_id_maker = ktx_id_maker or ktxid_uuid4
        self._inherit_data = inherit_data
        self._adapters = adapters

    def create(self, ktx_id: str | None = None) -> ContextT:
        if ktx_id is None:
            ktx_id = self._ktx_id_maker()

        data = None
        if self._inherit_data:
            parent_ctx = get_current_ctx_or_none()
            if parent_ctx is not None:
                data = parent_ctx.get_data()

        return self._context_type(ktx_id, data=data, adapters=self._adapters)
