from collections.abc import Mapping
from typing import Any, Protocol, TypeVar, runtime_checkable


@runtime_checkable
class AbstractContext(Protocol):
    def ktx_id(self) -> str: ...

    def get_data(self) -> Mapping[str, Any]: ...

    def get(self, key: str) -> Any: ...

    def set(self, key: str, value: Any) -> None: ...


@runtime_checkable
class AbstractContextDataAdapter(Protocol):
    def set(self, key: str, value: Any) -> None: ...


@runtime_checkable
class AbstractContextUser(Protocol):
    def get_id(self) -> Any:
        return None  # pragma: no cover

    def get_username(self) -> str | None:
        return None  # pragma: no cover

    def get_email(self) -> str | None:
        return None  # pragma: no cover

    def get_ip_address(self) -> str | None:
        return None  # pragma: no cover

    def set_id(self, value: Any) -> None:
        pass  # pragma: no cover

    def set_username(self, value: Any) -> None:
        pass  # pragma: no cover

    def set_email(self, value: str) -> None:
        pass  # pragma: no cover

    def set_ip_address(self, value: str) -> None:
        pass  # pragma: no cover


ContextT = TypeVar("ContextT", bound=AbstractContext, covariant=True)
ContextUserT = TypeVar("ContextUserT", bound=AbstractContextUser, covariant=True)


@runtime_checkable
class AbstractContextFactory(Protocol[ContextT]):
    def create(self, ktx_id: str | None = None) -> ContextT: ...


@runtime_checkable
class AbstractContextUserFactory(Protocol[ContextUserT]):
    def create(self) -> ContextUserT: ...


T = TypeVar("T", covariant=True)


@runtime_checkable
class AbstractBind(Protocol[T]):
    def bind(self) -> T: ...

    def unbind(self) -> None: ...

    def __enter__(self) -> T:
        return self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()


class KtxIdMaker(Protocol):
    def __call__(self) -> str: ...
