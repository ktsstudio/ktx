# ktx - Shared context library

[![Build](https://github.com/ktsstudio/ktx/actions/workflows/actions.yaml/badge.svg?branch=main)](https://github.com/ktsstudio/ktx/actions)
[![PyPI](https://img.shields.io/pypi/v/ktx.svg)](https://pypi.python.org/pypi/ktx)

## Introduction

ktx is a Context library aimed to simplify a process of creating and managing shared data in Python.

Quick example:

```python
from ktx.simple import SimpleContext

ctx = SimpleContext()
ctx.data.some_attribute = "value1"
```

You may also set created Context object as *current* for current thread or asyncio.Task:

```python
from ktx import ctx_wrap, get_current_ctx
from ktx.simple import SimpleContext

with ctx_wrap(SimpleContext()) as ctx:
    ctx.data.some_attribute = "value1"

    ctx2 = get_current_ctx()
    assert ctx2 is ctx
```

But also (thanks for `ContextVar`) context is available in any place of current coroutine in asyncio-world (note that asyncio-context is copied in the creating of new tasks):

````python
import asyncio

from ktx import get_current_ctx
from ktx.simple import SimpleContext


async def f1():
    ctx = get_current_ctx()
    assert ctx.get("some_attribute") == "value1"


async def main():
    with SimpleContext() as ctx:
        ctx.data.some_attribute = "value1"
        task1 = asyncio.create_task(f1())
        await asyncio.sleep(1)

    await task1
````

There exists an abstract interface (Protocol) for any "kind of Contex", so you may implement your own Context classes by implementing `ktx.abc.Context` protocol:

## API

Context provides the following methods:

- `set(key: str, value: Any) -> Any`: set value by key
- `get(key: str) -> Any`: get value by key
- `get_data() -> Mapping[str, Any]`: get all shared data
- `get_user() -> ContextUser`: get user object
- `uq_id() -> str`: get unique id of context

## Data Inheritance

This is best described using the following snippet:

```python
from ktx import ctx_wrap
from ktx.simple import SimpleContext

with ctx_wrap(SimpleContext()) as parent_ctx:
    parent_ctx.data.attr1 = "val1"
    parent_ctx.data.attr2 = "val2"

    with ctx_wrap(SimpleContext()) as child_ctx:
        assert child_ctx.data.attr1 == "val1"
        assert child_ctx.data.attr2 == "val2"

        child_ctx.data.attr2 = "val3"
        assert child_ctx.data.attr2 == "val3"

    assert parent_ctx.data.attr2 == "val2"
```


## Logging

### Structlog
There is a helper function `ktx.log.ktx_add_log` useful for [structlog](https://structlog.org/) processors that propagates all Context-specific attributes to a logging event dict.

## Custom context

It is possible to define a custom Context class in order to better support strong typing. You would need to implement `ktx.abc.`Context protocol and then you may use it with `ctx_wrap` functions as usual.

Note that you would need to implement general `get()` and `set()` methods for arbitrary fields as they may be accessed by other libraries which are using `Context`.

And the `get_data()` method must return all *shared* data of this context so it will be available during logging. For example:

```python
from typing import Mapping, Any

from ktx.user import ContextUser
from ktx.abc import Context


class MyContext(Context):  # Note that inheritance is not required.
    def __init__(self, uq_id: str, *, custom_field: str):
        self.custom_field = custom_field

        self._uq_id = uq_id
        self._data: dict[str, Any] = {}
        self._user = ContextUser()

    def uq_id(self) -> str:
        return self._uq_id

    def get_data(self) -> Mapping[str, Any]:
        return {
            **self._data,
            "custom_field": self.custom_field,
        }

    def get_user(self) -> ContextUser:
        return self._user

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any):
        self._data[key] = value
```


And then you may use this `MyContext` in safe manner like this:

```python
from ktx import ctx_wrap, get_current_ctx

with ctx_wrap(MyContext()) as ctx:
    ctx.custom_field = "value1"

    assert get_current_ctx(MyContext) is ctx
```

