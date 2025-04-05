from typing import Any

from ktx._meta import has_sentry
from ktx.abc import AbstractContextDataAdapter

if not has_sentry:
    raise ImportError("Sentry integration is not available.")  # pragma: no cover

from sentry_sdk import get_isolation_scope, set_extra, set_user


class SentryDataAdapter(AbstractContextDataAdapter):
    def __init__(self, *, ignore_prefix: str | None = "_"):
        self._ignore_prefix = ignore_prefix

    def set(self, key: str, value: Any) -> None:
        if self._ignore_prefix and key.startswith(self._ignore_prefix):
            return

        set_extra(key, value)


class SentryUserAdapter(AbstractContextDataAdapter):
    def set(self, key: str, value: Any) -> None:
        self._sentry_set_user_key(key, value)

    @staticmethod
    def _sentry_set_user_key(key: str, value: Any) -> None:
        user = get_isolation_scope()._user or {}

        user[key] = value
        set_user(user)
