from contextvars import Token
from typing import Generic, TypeVar

from .abc import AbstractBind, AbstractContext, AbstractContextUser
from .vars import (
    bind_current_ctx,
    bind_current_ctx_user,
    unbind_current_ctx,
    unbind_current_ctx_user,
)

ContextT = TypeVar("ContextT", bound=AbstractContext)
ContextUserT = TypeVar("ContextUserT", bound=AbstractContextUser)


class ContextBind(Generic[ContextT], AbstractBind[ContextT]):
    __slots__ = ["_ctx", "_token"]

    def __init__(self, ctx: ContextT):
        self._ctx = ctx
        self._token: Token | None = None

    @property
    def ctx(self) -> ContextT:
        return self._ctx

    def bind(self) -> ContextT:
        self._token = bind_current_ctx(self._ctx)
        return self._ctx

    def unbind(self) -> None:
        if self._token is not None:
            unbind_current_ctx(self._token)
            self._token = None


class ContextUserBind(Generic[ContextUserT], AbstractBind[ContextUserT]):
    __slots__ = ["_user", "_token"]

    def __init__(self, user: ContextUserT):
        self._user = user
        self._token: Token | None = None

    @property
    def user(self) -> ContextUserT:
        return self._user

    def bind(self) -> ContextUserT:
        self._token = bind_current_ctx_user(self._user)
        return self._user

    def unbind(self) -> None:
        if self._token is not None:
            unbind_current_ctx_user(self._token)
            self._token = None


def ctx_bind(ctx: ContextT) -> ContextBind[ContextT]:
    return ContextBind(ctx)


def ctx_user_bind(user: ContextUserT) -> ContextUserBind[ContextUserT]:
    return ContextUserBind(user)
