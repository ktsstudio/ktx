import pytest
from sentry_sdk import isolation_scope, new_scope


@pytest.fixture(autouse=True, scope="function")
def sentry_scope():
    with isolation_scope():
        with new_scope():
            yield
