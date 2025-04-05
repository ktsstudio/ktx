from collections.abc import Sequence
from typing import Any

from .abc import (
    AbstractContextDataAdapter,
    AbstractContextUser,
    AbstractContextUserFactory,
)


class ContextUser(AbstractContextUser):
    __slots__ = [
        "_id",
        "_email",
        "_username",
        "_ip",
    ]

    def __init__(
        self,
        *,
        id: Any = None,
        email: str | None = None,
        username: str | None = None,
        ip: str | None = None,
        adapters: Sequence[AbstractContextDataAdapter] | None = None,
    ):
        self._id = id
        self._email = email
        self._username = username
        self._ip = ip
        self._adapters = adapters

    def get_id(self) -> Any:
        return self._id

    def get_username(self) -> str | None:
        return self._username

    def get_email(self) -> str | None:
        return self._email

    def get_ip_address(self) -> str | None:
        return self._ip

    def set_id(self, value: Any) -> None:
        self._id = value
        self._post_apply_user_key("id", value)

    def set_email(self, value: str | None) -> None:
        self._email = value
        self._post_apply_user_key("email", value)

    def set_username(self, value: str | None) -> None:
        self._username = value
        self._post_apply_user_key("username", value)

    def set_ip_address(self, value: str | None) -> None:
        self._ip = value
        self._post_apply_user_key("ip_address", value)

    def _post_apply_user_key(self, key: str, value: Any):
        if self._adapters is not None:
            for adapter in self._adapters:
                adapter.set(key, value)


class ContextUserFactory(AbstractContextUserFactory[ContextUser]):
    __slots__ = [
        "_adapters",
    ]

    def __init__(
        self,
        *,
        adapters: Sequence[AbstractContextDataAdapter] | None = None,
    ):
        self._adapters = adapters

    def create(self) -> ContextUser:
        return ContextUser(adapters=self._adapters)
