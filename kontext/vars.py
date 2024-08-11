from contextvars import ContextVar, Token

from .abc import Context

_CurrentCtx: ContextVar = ContextVar("CurrentCtx")


def attach_current_ctx(ctx: Context) -> Token:
    return _CurrentCtx.set(ctx)


def detach_current_ctx(token: Token):
    return _CurrentCtx.reset(token)


def get_current_ctx_or_none() -> Context | None:
    return _CurrentCtx.get(None)


def get_current_ctx() -> Context:
    ctx = get_current_ctx_or_none()
    if ctx is None:
        raise RuntimeError("no context found in current task")
    return ctx
