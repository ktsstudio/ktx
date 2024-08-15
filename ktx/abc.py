from collections.abc import Mapping
from typing import Any, Protocol, TypeVar, runtime_checkable

from .user import ContextUser


@runtime_checkable
class Context(Protocol):
    def uq_id(self) -> str: ...

    def get_data(self) -> Mapping[str, Any]: ...

    def get(self, key: str) -> Any: ...

    def set(self, key: str, value: Any): ...

    def get_user(self) -> ContextUser: ...


ContextT = TypeVar("ContextT", bound=Context, covariant=True)


@runtime_checkable
class AbstractContextWrap(Protocol[ContextT]):
    def attach(self) -> ContextT: ...

    def detach(self) -> None: ...

    def __enter__(self) -> ContextT:
        return self.attach()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.detach()
