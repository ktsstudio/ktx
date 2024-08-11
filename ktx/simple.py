from typing import Any, Mapping, Self

import sentry_sdk
from immutabledict import immutabledict

from ._meta import has_sentry
from .abc import AbstractData
from .generic import GenericContext


class SimpleContextDataObject(AbstractData):
    def __repr__(self):
        return f"<SimpleContextDataObject keys_count={len(self.__dict__)}>"

    def clear(self):
        self.__dict__.clear()

    def __getattr__(self, item):
        return None

    if has_sentry:

        def __setattr__(self, key, value):
            super().__setattr__(key, value)

            if not key.startswith("_"):
                scope = sentry_sdk.get_current_scope()
                scope.set_extra(key, value)

    def to_dict(self) -> Mapping[str, Any]:
        return immutabledict(self.__dict__)

    def copy_from(self, other: Self) -> None:
        for key, value in other.__dict__.items():
            setattr(self, key, value)


class SimpleContext(GenericContext[SimpleContextDataObject]):
    pass
