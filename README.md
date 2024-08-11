from typing import Anyfrom typing import Mapping

# ktx

## Introduction

ktx is a Context library aimed to simplify a process of creating and managing shared data in Python.

Quick example:

```python

from ktx.simple import SimpleContext

with SimpleContext() as ctx:
    ctx.data.some_attribute = "value1"

```

While within the context manager the Context is available using `ktx.get_current_context()` function:

```python
from ktx import get_current_ctx
from ktx.simple import SimpleContext

with SimpleContext() as ctx:
    ctx.data.some_attribute = "value1"

    ctx2 = get_current_ctx()
    assert ctx2 is ctx
```

But also (thanks for `ContextVar`) is available in any place of current courotine in asyncio-world (note that asyncio-context is copied in the creating of new tasks):

````python
import asyncio

from ktx import get_current_ctx
from ktx.simple import SimpleContext


async def f1():
    ctx = get_current_ctx()
    assert ctx.data.some_attribute == "value1"


async def main():
    with SimpleContext() as ctx:
        ctx.data.some_attribute = "value1"
        task1 = asyncio.create_task(f1())
        await asyncio.sleep(1)

    await task1
````

There exists an abstract interface (Protocol) for any "kind of Contex", so you may implement your own Context classes by implementing `ktx.abc.Context` protocol:

## Data Inheritance

This is best described using the following snippet:

```python
from ktx.simple import SimpleContext

with SimpleContext() as parent_ctx:
    parent_ctx.data.attr1 = "val1"
    parent_ctx.data.attr2 = "val2"

    with SimpleContext() as child_ctx:
        assert child_ctx.data.attr1 == "val1"
        assert child_ctx.data.attr2 == "val2"

        child_ctx.data.attr2 = "val3"
        assert child_ctx.data.attr2 == "val3"

    assert parent_ctx.data.attr2 == "val2"
```



## Logging

There is a helper function `ktx.log.ktx_add_log` that propagates all Context-specific attributes to a logging event dict.

## Custom data

It is possible to define a custom data class in order to better support strong typing. You need to define 2 functions - one for converting data to dict and second - for copying data from another similar object. For example:

```python
from typing import Mapping, Any, Self

from ktx.abc import AbstractData
from ktx.generic import GenericContext


class MyData(AbstractData):
    some_attribute: str | None

    def __init__(self):
        self.some_attribute = None

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "some_attribute": self.some_attribute
        }

    def copy_from(self, other: Self) -> None:
        self.some_attribute = other.some_attribute


class MyContext(GenericContext[MyData]):
    pass

```


And then you may use this `MyContext` in safe manner like this:

```python
with MyContext() as ctx:
    ctx.data.some_attribute = "value1"
```

