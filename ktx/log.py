from typing import Any, ItemsView, Iterator, MutableMapping, TypeVar

from .abc import AbstractData, Context
from .vars import get_current_ctx_or_none

DataT = TypeVar("DataT", bound=AbstractData)


def ktx_add_log(
    event_dict: MutableMapping[str, Any],
    ctx: Context[DataT] | None = None,
    *,
    log_private: bool = False,
) -> MutableMapping[str, Any]:
    if ctx is None:
        ctx = get_current_ctx_or_none()

    if ctx is None:
        # if still empty - return as is
        return event_dict

    data_dict = ctx.data.to_dict()

    data_dict_iter: Iterator[tuple[str, Any]] | ItemsView[str, Any]
    if not log_private:
        data_dict_iter = ((k, v) for k, v in data_dict.items() if not k.startswith("_"))
    else:
        data_dict_iter = data_dict.items()

    for k, v in data_dict_iter:
        event_dict[f"data_{k}"] = v

    if ctx.user.id is not None:
        event_dict["user_id"] = ctx.user.id
    if ctx.user.username is not None:
        event_dict["user_username"] = ctx.user.username
    if ctx.user.email is not None:
        event_dict["user_email"] = ctx.user.email
    if ctx.user.ip is not None:
        event_dict["user_ip"] = ctx.user.ip

    event_dict["uq_id"] = ctx.uq_id

    return event_dict
