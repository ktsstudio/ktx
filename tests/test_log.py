import uuid

import pytest

from ktx import ctx_bind
from ktx.bind import ctx_user_bind
from ktx.ctx import Context
from ktx.log import ktx_add_log, ktx_add_user_log
from ktx.user import ContextUser


@pytest.fixture
def event_dict() -> dict[str, str]:
    return {"some": "value"}


@pytest.fixture
def ctx() -> Context:
    return Context("some-trace-id")


@pytest.fixture
def user() -> ContextUser:
    return ContextUser()


class TestLog:
    def test_event_dict_no_ctx(self, event_dict: dict[str, str]):
        assert ktx_add_log(event_dict) == event_dict
        assert ktx_add_user_log(event_dict) == event_dict

    def test_event_dict_direct_ctx(self, event_dict: dict[str, str], ctx: Context):
        ctx.set("attr1", "value1")
        assert ktx_add_log(event_dict, ctx) == {
            **event_dict,
            "ktx_id": "some-trace-id",
            "data_attr1": "value1",
        }

    def test_event_dict_indirect_ctx(self, event_dict: dict[str, str], ctx: Context):
        with ctx_bind(ctx) as ctx:
            ctx.set("attr1", "value1")

            assert ktx_add_log(event_dict) == {
                **event_dict,
                "ktx_id": "some-trace-id",
                "data_attr1": "value1",
            }

    def test_event_dict_direct_ctx_no_private(
        self, event_dict: dict[str, str], ctx: Context
    ):
        ctx.set("attr1", "value1")
        ctx.set("_attr2", "value2")
        assert ktx_add_log(event_dict, ctx) == {
            **event_dict,
            "ktx_id": "some-trace-id",
            "data_attr1": "value1",
        }

    def test_log_private(self, event_dict: dict[str, str], ctx: Context):
        ctx.set("attr1", "value1")
        ctx.set("_attr2", "value2")
        assert ktx_add_log(event_dict, ctx, log_private=True) == {
            **event_dict,
            "ktx_id": "some-trace-id",
            "data_attr1": "value1",
            "data__attr2": "value2",
        }

    def test_str_value(self, event_dict: dict[str, str], ctx: Context):
        val = uuid.uuid4()
        ctx.set("attr1", val)
        assert ktx_add_log(event_dict, ctx) == {
            **event_dict,
            "ktx_id": "some-trace-id",
            "data_attr1": str(val),
        }

    def test_str_value_different_prefix(self, event_dict: dict[str, str], ctx: Context):
        val = uuid.uuid4()
        ctx.set("attr1", val)
        assert ktx_add_log(event_dict, ctx, data_key_prefix="something_") == {
            **event_dict,
            "ktx_id": "some-trace-id",
            "something_attr1": str(val),
        }

    def test_none_values(self, event_dict: dict[str, str], ctx: Context):
        ctx.set("attr1", None)
        assert ktx_add_log(event_dict, ctx) == {
            **event_dict,
            "ktx_id": "some-trace-id",
        }


class TestLogUser:
    def test_user_log(self, event_dict: dict[str, str], user: ContextUser):
        user.set_id(uuid.uuid4())
        user.set_username("some-username")
        user.set_email("test@example.com")
        user.set_ip_address("127.0.0.1")

        assert ktx_add_user_log(event_dict, user) == {
            **event_dict,
            "user_id": str(user.get_id()),
            "user_username": "some-username",
            "user_email": "test@example.com",
            "user_ip_address": "127.0.0.1",
        }

    def test_user_log_indirect(self, event_dict: dict[str, str], user: ContextUser):
        with ctx_user_bind(user) as user:
            user.set_id(uuid.uuid4())
            user.set_username("some-username")
            user.set_email("test@example.com")
            user.set_ip_address("127.0.0.1")

            assert ktx_add_user_log(event_dict) == {
                **event_dict,
                "user_id": str(user.get_id()),
                "user_username": "some-username",
                "user_email": "test@example.com",
                "user_ip_address": "127.0.0.1",
            }

    def test_user_log_custom_prefix(
        self, event_dict: dict[str, str], user: ContextUser
    ):
        user.set_id(uuid.uuid4())
        user.set_username("some-username")
        user.set_email("test@example.com")
        user.set_ip_address("127.0.0.1")

        assert ktx_add_user_log(event_dict, user, user_key_prefix="u_") == {
            **event_dict,
            "u_id": str(user.get_id()),
            "u_username": "some-username",
            "u_email": "test@example.com",
            "u_ip_address": "127.0.0.1",
        }

    def test_user_id_non_str(self, event_dict: dict[str, str], user: ContextUser):
        user.set_id(uuid.uuid4())

        assert ktx_add_user_log(event_dict, user) == {
            **event_dict,
            "user_id": str(user.get_id()),
        }
