from collections.abc import ItemsView, Iterator, MutableMapping
from typing import Any

from .abc import Context
from .vars import get_current_ctx_or_none


def ktx_add_log(
    event_dict: MutableMapping[str, Any],
    ctx: Context | None = None,
    *,
    log_private: bool = False,
) -> MutableMapping[str, Any]:
    if ctx is None:
        ctx = get_current_ctx_or_none()

    if ctx is None:
        # if still empty - return as is
        return event_dict

    data_dict = ctx.get_data()

    data_dict_iter: Iterator[tuple[str, Any]] | ItemsView[str, Any]
    if not log_private:
        data_dict_iter = ((k, v) for k, v in data_dict.items() if not k.startswith("_"))
    else:
        data_dict_iter = data_dict.items()

    for k, v in data_dict_iter:
        if v is not None:
            event_dict[f"data_{k}"] = str(v)

    user = ctx.get_user()
    if user.id is not None:
        event_dict["user_id"] = str(user.id)
    if user.username is not None:
        event_dict["user_username"] = user.username
    if user.email is not None:
        event_dict["user_email"] = user.email
    if user.ip is not None:
        event_dict["user_ip"] = user.ip

    event_dict["uq_id"] = ctx.uq_id()

    return event_dict
