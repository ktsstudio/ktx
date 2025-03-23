import uuid
from collections.abc import Mapping
from typing import Any, Protocol

from immutabledict import immutabledict

from ._meta import has_sentry
from .abc import Context
from .user import ContextUser
from .vars import get_current_ctx_or_none

if has_sentry:
    import sentry_sdk


class KtxIdMaker(Protocol):
    def __call__(self) -> str: ...


def _get_uuid_ktx_id() -> str:
    return uuid.uuid4().hex


class SimpleContextData:
    def __repr__(self):
        return f"<SimpleContextDataObject keys_count={len(self.__dict__)}>"

    def clear(self):
        self.__dict__.clear()

    def __getattr__(self, item):
        return None

    if has_sentry:

        def __setattr__(self, key, value):
            super().__setattr__(key, value)

            if not key.startswith("_"):
                scope = sentry_sdk.get_current_scope()
                scope.set_extra(key, value)

    def to_dict(self) -> Mapping[str, Any]:
        return immutabledict(self.__dict__)

    def copy_from(self, other: Mapping[str, Any]) -> None:
        for key, value in other.items():
            setattr(self, key, value)


class SimpleContext(Context):
    __slots__ = [
        "_ktx_id",
        "_user",
        "_data",
    ]

    def __init__(
        self,
        ktx_id: str | None = None,
        *,
        inherit_user: bool = True,
        inherit_data: bool = True,
        user: ContextUser | None = None,
        data: SimpleContextData | None = None,
        ktx_id_maker: KtxIdMaker | None = None,
    ):
        ktx_id_maker = ktx_id_maker or _get_uuid_ktx_id
        self._ktx_id = ktx_id or ktx_id_maker()
        self._user = user or ContextUser()
        self._data = data or SimpleContextData()

        if inherit_user or inherit_data:
            parent_ctx = get_current_ctx_or_none()
            if parent_ctx is not None:
                if inherit_data:
                    self._data.copy_from(parent_ctx.get_data())

                if inherit_user:
                    self._user.copy_from(parent_ctx.get_user())

    def ktx_id(self) -> str:
        return self._ktx_id

    @property
    def data(self) -> SimpleContextData:
        return self._data

    def get_data(self) -> Mapping[str, Any]:
        return self._data.to_dict()

    def get_user(self) -> ContextUser:
        return self._user

    def get(self, key: str) -> Any:
        return getattr(self._data, key)

    def set(self, key: str, value: Any):
        setattr(self._data, key, value)
