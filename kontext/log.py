from typing import Any, MutableMapping, TypeVar

from .abc import AbstractData, Context
from .vars import get_current_ctx_or_none

DataT = TypeVar("DataT", bound=AbstractData)


def kontext_add_log(
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
    if not log_private:
        data_dict = {k: v for k, v in data_dict.items() if not k.startswith("_")}

    user_dict = {}
    if ctx.user.id is not None:
        user_dict["id"] = ctx.user.id
    if ctx.user.username is not None:
        user_dict["username"] = ctx.user.username
    if ctx.user.email is not None:
        user_dict["email"] = ctx.user.email
    if ctx.user.ip is not None:
        user_dict["ip"] = ctx.user.ip

    event_dict["uq_id"] = ctx.uq_id
    event_dict["data"] = data_dict

    if len(user_dict) > 0:
        event_dict["user"] = user_dict

    return event_dict
