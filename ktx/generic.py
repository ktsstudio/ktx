import uuid
from contextlib import AbstractContextManager
from contextvars import Token
from typing import Generic, TypeVar

import typing_inspect

from ktx._meta import PY311, has_open_telemetry, has_sentry
from ktx.abc import AbstractData, Context
from ktx.user import ContextUser
from ktx.vars import attach_current_ctx, detach_current_ctx, get_current_ctx_or_none

if has_sentry:
    from sentry_sdk import Scope, new_scope

if PY311:
    from typing import Self
else:
    from typing_extensions import Self


def _get_uuid_uq_id() -> str:
    return uuid.uuid4().hex


if has_open_telemetry:
    from opentelemetry import trace

    def _get_uq_id() -> str:
        trace_id = trace.get_current_span().get_span_context().trace_id
        if trace_id != 0:
            return hex(trace_id)

        return _get_uuid_uq_id()

else:
    _get_uq_id = _get_uuid_uq_id

DataT = TypeVar("DataT", bound=AbstractData)


class GenericContext(Context[DataT], Generic[DataT]):
    __slots__ = [
        "_uq_id",
        "_user",
        "_data",
        "_token",
    ]

    if has_sentry:
        __slots__.append("_sentry_scope_cm")

    def __init__(
        self,
        uq_id: str | None = None,
        *,
        inherit_user: bool = True,
        inherit_data: bool = True,
        user: ContextUser | None = None,
        data: DataT | None = None,
    ):
        self._uq_id = uq_id or _get_uq_id()
        self._user = user or ContextUser()

        data = data or self._make_default_data()
        assert data is not None, "data cannot be None"
        self._data = data

        self._token: Token | None = None
        if has_sentry:
            self._sentry_scope_cm: AbstractContextManager["Scope"] | None = None

        if inherit_user or inherit_data:
            parent_ctx = get_current_ctx_or_none()
            if parent_ctx is not None:
                if inherit_data:
                    if type(self._data) is not type(parent_ctx.data):
                        raise ValueError(
                            f"cannot inherit data from type {type(parent_ctx.data)} to different type {type(self._data)}"
                        )

                    self._data.copy_from(parent_ctx.data)

                if inherit_user:
                    self._user.copy_from(parent_ctx.user)

    def _make_default_data(self) -> DataT:
        bases = typing_inspect.get_generic_bases(self.__class__)

        generic_args = []
        for b in bases:
            if typing_inspect.is_generic_type(b):
                generic_args = typing_inspect.get_args(b)

        if not generic_args or len(generic_args) == 0:
            raise ValueError("data type is not specified or couldn't deduce it")

        for data_type in generic_args:
            if issubclass(data_type, AbstractData):
                return data_type()

        raise ValueError(
            "data is expected to be a subclass of AbstractData - cannot find appropriate generic arg"
        )

    @property
    def uq_id(self) -> str:
        return self._uq_id

    @property
    def data(self) -> DataT:
        return self._data

    @property
    def user(self) -> ContextUser:
        return self._user

    if has_sentry:

        def __enter__(self) -> Self:
            self._token = attach_current_ctx(self)

            self._sentry_scope_cm = new_scope()
            scope = self._sentry_scope_cm.__enter__()
            scope.set_tag("uq_id", self.uq_id)
            scope.set_extra("uq_id", self.uq_id)

            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self._token is not None:
                detach_current_ctx(self._token)
                self._token = None

            if self._sentry_scope_cm is not None:
                self._sentry_scope_cm.__exit__(exc_type, exc_val, exc_tb)
                self._sentry_scope_cm = None

    else:

        def __enter__(self) -> Self:
            self._token = attach_current_ctx(self)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self._token is not None:
                detach_current_ctx(self._token)
                self._token = None
