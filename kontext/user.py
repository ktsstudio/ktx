from typing import Any

from ._meta import has_sentry

if has_sentry:
    from sentry_sdk import get_isolation_scope

    def sentry_set_user_key(key: str, value: Any):
        scope = get_isolation_scope()
        if scope._user is None:
            scope._user = {}
        scope._user[key] = value

    def sentry_set_user(user: dict[str, Any]):
        scope = get_isolation_scope()
        scope.set_user(user)

else:

    def sentry_set_user_key(key: str, value: Any):
        pass

    def sentry_set_user(user: dict[str, Any]):
        pass


class ContextUser:
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
    ):
        self._id = id
        self._email = email
        self._username = username
        self._ip = ip

    def copy_from(self, other: "ContextUser") -> None:
        self._id = other.id
        self._email = other.email
        self._username = other.username
        self._ip = other.ip

    def set_sentry_user(self):
        sentry_set_user(
            {
                "id": self._id,
                "email": self._email,
                "username": self._username,
                "ip_address": self._ip,
            }
        )

    @property
    def id(self) -> Any:
        return self._id

    @id.setter
    def id(self, value: Any):
        self._id = value
        self._post_apply_user_key("id", value)
        sentry_set_user_key("id", value)

    @property
    def email(self) -> str | None:
        return self._email

    @email.setter
    def email(self, value: str | None):
        self._email = value
        self._post_apply_user_key("email", value)
        sentry_set_user_key("email", value)

    @property
    def username(self) -> str | None:
        return self._username

    @username.setter
    def username(self, value: str | None):
        self._username = value
        self._post_apply_user_key("username", value)
        sentry_set_user_key("username", value)

    @property
    def ip(self) -> str | None:
        return self._ip

    @ip.setter
    def ip(self, value: str | None):
        self._ip = value
        self._post_apply_user_key("ip", value)
        sentry_set_user_key("ip_address", value)

    def _post_apply_user_key(self, key: str, value: Any):
        pass
