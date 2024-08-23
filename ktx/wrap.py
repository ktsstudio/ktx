from contextlib import AbstractContextManager
from contextvars import Token
from typing import Generic, TypeVar

from ._meta import has_sentry
from .abc import AbstractContextWrap, Context
from .vars import attach_current_ctx, detach_current_ctx

if has_sentry:
    from sentry_sdk import Scope, new_scope

ContextT = TypeVar("ContextT", bound=Context)


class ContextWrap(Generic[ContextT], AbstractContextWrap[ContextT]):
    __slots__ = ["_ctx", "_token"]

    if has_sentry:
        __slots__.append("_sentry_scope_cm")

    def __init__(self, ctx: ContextT):
        self._ctx = ctx
        self._token: Token | None = None

        if has_sentry:
            self._sentry_scope_cm: AbstractContextManager["Scope"] | None = None

    @property
    def ctx(self) -> ContextT:
        return self._ctx

    def attach(self) -> ContextT:
        self._token = attach_current_ctx(self._ctx)

        if has_sentry:
            self._sentry_scope_cm = new_scope()
            if self._sentry_scope_cm is not None:
                scope = self._sentry_scope_cm.__enter__()
                scope.set_tag("uq_id", self._ctx.uq_id())
                scope.set_extra("uq_id", self._ctx.uq_id())

        return self._ctx

    def detach(self) -> None:
        if self._token is not None:
            detach_current_ctx(self._token)
            self._token = None

        if self._sentry_scope_cm is not None:
            self._sentry_scope_cm.__exit__(None, None, None)
            self._sentry_scope_cm = None


def ctx_wrap(ctx: ContextT) -> ContextWrap[ContextT]:
    return ContextWrap(ctx)
