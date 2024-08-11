from typing import Any, Mapping, Protocol, Self, TypeVar, runtime_checkable

from .user import ContextUser


@runtime_checkable
class AbstractData(Protocol):
    def to_dict(self) -> Mapping[str, Any]: ...

    def copy_from(self, other: Self) -> None: ...


DataT = TypeVar("DataT", bound=AbstractData, covariant=True)


@runtime_checkable
class Context(Protocol[DataT]):
    @property
    def uq_id(self) -> str: ...

    @property
    def data(self) -> DataT: ...

    @property
    def user(self) -> ContextUser: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type, exc_val, exc_tb): ...
