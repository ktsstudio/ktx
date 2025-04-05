# ktx - Shared context library

[![Build](https://github.com/ktsstudio/ktx/actions/workflows/actions.yaml/badge.svg?branch=main)](https://github.com/ktsstudio/ktx/actions)
[![PyPI](https://img.shields.io/pypi/v/ktx.svg)](https://pypi.python.org/pypi/ktx)

ktx is a Context library aimed to simplify a process of creating and managing shared data in Python.

## Quick start

Context example:

```python
from ktx import ctx_bind
from ktx.ctx import ContextFactory

ctx_factory = ContextFactory()

with ctx_bind(ctx_factory.create()) as ctx:
    ctx.set("some_attribute", "value1")
```

ContextUser example:

```python
from ktx import ctx_user_bind
from ktx.user import ContextUserFactory

user_factory = ContextUserFactory()

with ctx_user_bind(user_factory.create()) as user:
    user.set_id(42)
    user.set_email("foo@example.com")
    user.set_username("foo")
    user.set_ip_address("127.0.0.1")

    # then you can get all this data through getter methods:
    print(user.get_id())
    print(user.get_email())
    print(user.get_username())
    print(user.get_ip_address())
```

## Sentry integration

There's a Sentry integration in the `ktx` library that allows all key-value pairs be propagated to Sentry events:
```python
from ktx.ctx import ContextFactory
from ktx.adapters.sentry import SentryDataAdapter

factory = ContextFactory(adapters=[SentryDataAdapter()])
ctx = factory.create()

ctx.set("attr1", "val1")
ctx.set("_attr2", "val2")  # private fields don't get sent to Sentry

# attr1 will be in Sentry event's extras, and _attr2 will not be
```

The similar situation is with `ContextUser`:

```python
from ktx.user import ContextUserFactory
from ktx.adapters.sentry import SentryUserAdapter

factory = ContextUserFactory(adapters=[SentryUserAdapter()])
user = factory.create()

user.set_id(42)
user.set_email("foo@example.com")
user.set_username("foo")
user.set_ip_address("127.0.0.1")

# Sentry will receive user object with all proper fields set
```

## Introduction

### Context

You may set created Context object as *current* for current thread or asyncio.Task:

```python
from ktx import ctx_bind, get_current_ctx
from ktx.ctx import ContextFactory

ctx_factory = ContextFactory()

with ctx_bind(ctx_factory.create()) as ctx:
    ctx.set("some_attribute", "value1")

    assert get_current_ctx() is ctx
```

But also (thanks for `ContextVar`) context is available in any place of current coroutine in asyncio-world (note that asyncio-context is copied in the creating of new tasks):

````python
import asyncio

from ktx import get_current_ctx, ctx_bind
from ktx.ctx import ContextFactory


async def f1():
    ctx = get_current_ctx()
    assert ctx.get("some_attribute") == "value1"


async def main():
    ctx_factory = ContextFactory()

    with ctx_bind(ctx_factory.create()) as ctx:
        ctx.set("some_attribute", "value1")

        task1 = asyncio.create_task(f1())
        await asyncio.sleep(1)

    await task1
````

There exists an abstract interface (Protocol) for any "kind of Contex", so you may implement your own Context classes by implementing `ktx.abc.Context` protocol:


## API

### Context

Context provides the following methods:

- `set(key: str, value: Any) -> Any`: set value by key
- `get(key: str) -> Any`: get value by key
- `get_data() -> Mapping[str, Any]`: get all shared data
- `ktx_id() -> str`: get unique id of context

## Data Inheritance

This is best described using the following snippet:

```python
from ktx import ctx_bind
from ktx.ctx import ContextFactory

ctx_factory = ContextFactory()

with ctx_bind(ctx_factory.create()) as parent_ctx:
    parent_ctx.set("attr1", "val1")
    parent_ctx.set("attr2", "val2")

    with ctx_bind(ctx_factory.create()) as child_ctx:
        assert child_ctx.get("attr1") == "val1"
        assert child_ctx.get("attr2") == "val2"

        child_ctx.set("attr2", "val3")
        assert child_ctx.get("attr2") == "val3"

    assert parent_ctx.get("attr2") == "val2"
```


## Logging

### Structlog
There is a helper function `ktx.log.ktx_add_log` useful for [structlog](https://structlog.org/) processors that propagates all Context-specific attributes to a logging event dict.

## Custom context

It is possible to define a custom Context class in order to better support strong typing. You would need to implement `ktx.abc.`Context protocol and then you may use it with `ctx_bind` functions as usual.

Note that you would need to implement general `get()` and `set()` methods for arbitrary fields as they may be accessed by other libraries which are using `Context`.

And the `get_data()` method must return all *shared* data of this context so it will be available during logging. For example:

```python
from typing import Mapping, Any

from ktx.abc import AbstractContext


class MyContext(AbstractContext):  # Note that inheritance from the protocol is not required.
    def __init__(self, ktx_id: str, *, custom_field: str):
        self.custom_field = custom_field

        self._ktx_id = ktx_id
        self._data: dict[str, Any] = {}

    def ktx_id(self) -> str:
        return self._ktx_id

    def get_data(self) -> Mapping[str, Any]:
        return {
            **self._data,
            "custom_field": self.custom_field,
        }

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any):
        self._data[key] = value
```

Also you may benefit from extending included `Context` class:
```python
from typing import Mapping, Any

from ktx.ctx import Context

class MyContext(Context):  # Note that inheritance from the protocol is not required.
    def __init__(self, ktx_id: str, *, custom_field: str):
        super().__init__(ktx_id)
        self.custom_field = custom_field
```


And then you may use this `MyContext` in safe manner like this:

```python
from ktx import ctx_bind, get_current_ctx

with ctx_bind(MyContext("id1")) as ctx:
    ctx.custom_field = "value1"

    assert get_current_ctx(MyContext) is ctx
```

