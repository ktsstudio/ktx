from contextvars import ContextVar, Token
from typing import TypeVar, overload

from .abc import Context

_CurrentCtx: ContextVar = ContextVar("CurrentCtx")


def attach_current_ctx(ctx: Context) -> Token:
    return _CurrentCtx.set(ctx)


def detach_current_ctx(token: Token):
    return _CurrentCtx.reset(token)


ContextT = TypeVar("ContextT", bound=Context)


@overload
def get_current_ctx_or_none(tp: None = None) -> Context | None: ...


@overload
def get_current_ctx_or_none(tp: type[ContextT] | None = None) -> ContextT | None: ...


def get_current_ctx_or_none(
    tp: type[ContextT] | None = None,
) -> ContextT | Context | None:
    return _CurrentCtx.get(None)


@overload
def get_current_ctx(tp: None = None) -> Context: ...


@overload
def get_current_ctx(tp: type[ContextT] | None = None) -> ContextT: ...


def get_current_ctx(tp: type[ContextT] | None = None) -> ContextT | Context:
    ctx = get_current_ctx_or_none()
    if ctx is None:
        raise RuntimeError("no context found in current task")

    if tp is not None and not isinstance(ctx, tp):
        raise RuntimeError(
            f"current context is not an instance of {tp} but {type(ctx)}"
        )

    return ctx
