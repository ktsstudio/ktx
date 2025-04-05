from collections.abc import Mapping, Sequence
from typing import Any

from immutabledict import immutabledict

from .abc import (
    AbstractContext,
    AbstractContextDataAdapter,
    AbstractContextFactory,
    KtxIdMaker,
)
from .ktxid import ktxid_uuid4
from .vars import get_current_ctx_or_none


class Context(AbstractContext):
    __slots__ = [
        "_ktx_id",
        "_data",
        "_adapters",
    ]

    def __init__(
        self,
        ktx_id: str,
        *,
        data: Mapping[str, Any] | None = None,
        adapters: Sequence[AbstractContextDataAdapter] | None = None,
    ):
        self._ktx_id = ktx_id
        self._data = dict(data) if data is not None else {}
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


class ContextFactory(AbstractContextFactory[Context]):
    __slots__ = [
        "_ktx_id_maker",
        "_inherit_data",
        "_adapters",
    ]

    def __init__(
        self,
        *,
        ktx_id_maker: KtxIdMaker | None = None,
        inherit_data: bool = True,
        adapters: Sequence[AbstractContextDataAdapter] | None = None,
    ):
        self._ktx_id_maker = ktx_id_maker or ktxid_uuid4
        self._inherit_data = inherit_data
        self._adapters = adapters

    def create(self, ktx_id: str | None = None) -> Context:
        if ktx_id is None:
            ktx_id = self._ktx_id_maker()

        data = None
        if self._inherit_data:
            parent_ctx = get_current_ctx_or_none()
            if parent_ctx is not None:
                data = parent_ctx.get_data()

        return Context(ktx_id, data=data, adapters=self._adapters)
