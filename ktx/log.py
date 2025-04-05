from collections.abc import ItemsView, Iterator, MutableMapping
from typing import Any

from .abc import AbstractContext, AbstractContextUser
from .vars import get_current_ctx_or_none, get_current_ctx_user_or_none


def ktx_add_log(
    event_dict: MutableMapping[str, Any],
    ctx: AbstractContext | None = None,
    *,
    log_private: bool = False,
    data_key_prefix: str = "data_",
) -> MutableMapping[str, Any]:
    if ctx is None:
        ctx = get_current_ctx_or_none()

    if ctx is None:
        # if still empty - return as is
        return event_dict

    event_dict["ktx_id"] = ctx.ktx_id()

    data_dict = ctx.get_data()

    if data_dict:
        data_dict_iter: Iterator[tuple[str, Any]] | ItemsView[str, Any]
        if not log_private:
            data_dict_iter = (
                (k, v) for k, v in data_dict.items() if not k.startswith("_")
            )
        else:
            data_dict_iter = data_dict.items()

        for k, v in data_dict_iter:
            if v is not None:
                event_dict[f"{data_key_prefix}{k}"] = str(v)

    return event_dict


def ktx_add_user_log(
    event_dict: MutableMapping[str, Any],
    user: AbstractContextUser | None = None,
    *,
    user_key_prefix: str = "user_",
) -> MutableMapping[str, Any]:
    if user is None:
        user = get_current_ctx_user_or_none()

    if user is None:
        # if still empty - return as is
        return event_dict

    if val := user.get_id():
        event_dict[f"{user_key_prefix}id"] = str(val)

    if val := user.get_username():
        event_dict[f"{user_key_prefix}username"] = val

    if val := user.get_email():
        event_dict[f"{user_key_prefix}email"] = val

    if val := user.get_ip_address():
        event_dict[f"{user_key_prefix}ip_address"] = val

    return event_dict
