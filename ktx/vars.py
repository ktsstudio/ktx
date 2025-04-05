from contextvars import ContextVar, Token
from typing import TypeVar, overload

from .abc import AbstractContext, AbstractContextUser

_CurrentCtx: ContextVar = ContextVar("CurrentCtx")
_CurrentCtxUser: ContextVar = ContextVar("CurrentCtxUser")


def bind_current_ctx(ctx: AbstractContext) -> Token:
    return _CurrentCtx.set(ctx)


def unbind_current_ctx(token: Token):
    return _CurrentCtx.reset(token)


def bind_current_ctx_user(user: AbstractContextUser) -> Token:
    return _CurrentCtxUser.set(user)


def unbind_current_ctx_user(token: Token):
    return _CurrentCtxUser.reset(token)


ContextT = TypeVar("ContextT", bound=AbstractContext)
ContextUserT = TypeVar("ContextUserT", bound=AbstractContextUser)


@overload
def get_current_ctx_or_none(tp: None = None) -> AbstractContext | None: ...


@overload
def get_current_ctx_or_none(tp: type[ContextT] | None = None) -> ContextT | None: ...


def get_current_ctx_or_none(
    tp: type[ContextT] | None = None,
) -> ContextT | AbstractContext | None:
    return _CurrentCtx.get(None)


@overload
def get_current_ctx(tp: None = None) -> AbstractContext: ...


@overload
def get_current_ctx(tp: type[ContextT] | None = None) -> ContextT: ...


def get_current_ctx(tp: type[ContextT] | None = None) -> ContextT | AbstractContext:
    ctx = get_current_ctx_or_none()
    if ctx is None:
        raise RuntimeError("no context found in current task")

    if tp is not None and not isinstance(ctx, tp):
        raise RuntimeError(
            f"current context is not an instance of {tp} but {type(ctx)}"
        )

    return ctx


@overload
def get_current_ctx_user_or_none(tp: None = None) -> AbstractContextUser | None: ...


@overload
def get_current_ctx_user_or_none(
    tp: type[ContextUserT] | None = None,
) -> ContextUserT | None: ...


def get_current_ctx_user_or_none(
    tp: type[ContextUserT] | None = None,
) -> ContextUserT | AbstractContextUser | None:
    return _CurrentCtxUser.get(None)


@overload
def get_current_ctx_user(tp: None = None) -> AbstractContextUser: ...


@overload
def get_current_ctx_user(tp: type[ContextUserT] | None = None) -> ContextUserT: ...


def get_current_ctx_user(
    tp: type[ContextUserT] | None = None,
) -> ContextUserT | AbstractContextUser:
    user = get_current_ctx_user_or_none()
    if user is None:
        raise RuntimeError("no context user found in current task")

    if tp is not None and not isinstance(user, tp):
        raise RuntimeError(
            f"current context user is not an instance of {tp} but {type(user)}"
        )

    return user
