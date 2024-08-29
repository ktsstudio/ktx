import uuid
from collections.abc import Mapping
from typing import Any

from immutabledict import immutabledict

from ._meta import has_open_telemetry, has_sentry
from .abc import Context
from .user import ContextUser
from .vars import get_current_ctx_or_none

if has_sentry:
    import sentry_sdk


def _get_uuid_uq_id() -> str:
    return uuid.uuid4().hex


if has_open_telemetry:
    from opentelemetry import trace
    from opentelemetry.trace import format_trace_id

    def _get_uq_id() -> str:
        trace_id = trace.get_current_span().get_span_context().trace_id
        if trace_id != 0:
            return format_trace_id(trace_id)

        return _get_uuid_uq_id()

else:
    _get_uq_id = _get_uuid_uq_id


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
        "_uq_id",
        "_user",
        "_data",
    ]

    def __init__(
        self,
        uq_id: str | None = None,
        *,
        inherit_user: bool = True,
        inherit_data: bool = True,
        user: ContextUser | None = None,
        data: SimpleContextData | None = None,
    ):
        self._uq_id = uq_id or _get_uq_id()
        self._user = user or ContextUser()
        self._data = data or SimpleContextData()

        if inherit_user or inherit_data:
            parent_ctx = get_current_ctx_or_none()
            if parent_ctx is not None:
                if inherit_data:
                    self._data.copy_from(parent_ctx.get_data())

                if inherit_user:
                    self._user.copy_from(parent_ctx.get_user())

    def uq_id(self) -> str:
        return self._uq_id

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
