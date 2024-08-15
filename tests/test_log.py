import uuid

from ktx import ctx_wrap
from ktx.log import ktx_add_log
from ktx.simple import SimpleContext


class TestLog:
    def test_event_dict_no_ctx(self):
        event_dict = {"some": "value"}
        assert ktx_add_log(event_dict) == event_dict

    def test_event_dict_direct_ctx(self):
        event_dict = {"some": "value"}
        ctx = SimpleContext("some-trace-id")
        ctx.data.attr1 = "value1"
        ctx.get_user().username = "some-username"
        assert ktx_add_log(event_dict, ctx) == {
            **event_dict,
            "uq_id": "some-trace-id",
            "data_attr1": "value1",
            "user_username": "some-username",
        }

    def test_event_dict_indirect_ctx(self):
        event_dict = {"some": "value"}
        with ctx_wrap(SimpleContext("some-trace-id")) as ctx:
            ctx.data.attr1 = "value1"
            ctx.get_user().username = "some-username"

            assert ktx_add_log(event_dict) == {
                **event_dict,
                "uq_id": "some-trace-id",
                "data_attr1": "value1",
                "user_username": "some-username",
            }

    def test_event_dict_direct_ctx_no_private(self):
        event_dict = {"some": "value"}
        ctx = SimpleContext("some-trace-id")
        ctx.data.attr1 = "value1"
        ctx.data._attr2 = "value2"
        ctx.get_user().username = "some-username"
        assert ktx_add_log(event_dict, ctx) == {
            **event_dict,
            "uq_id": "some-trace-id",
            "data_attr1": "value1",
            "user_username": "some-username",
        }

    def test_str_value(self):
        event_dict = {"some": "value"}
        ctx = SimpleContext("some-trace-id")

        val = uuid.uuid4()
        ctx.data.attr1 = val
        assert ktx_add_log(event_dict, ctx) == {
            **event_dict,
            "uq_id": "some-trace-id",
            "data_attr1": str(val),
        }

    def test_none_values(self):
        event_dict = {"some": "value"}
        ctx = SimpleContext("some-trace-id")

        ctx.data.attr1 = None
        assert ktx_add_log(event_dict, ctx) == {
            **event_dict,
            "uq_id": "some-trace-id",
        }

    def test_user_id_non_str(self):
        event_dict = {"some": "value"}
        ctx = SimpleContext("some-trace-id")

        ctx.get_user().id = uuid.uuid4()
        assert ktx_add_log(event_dict, ctx) == {
            **event_dict,
            "uq_id": "some-trace-id",
            "user_id": str(ctx.get_user().id),
        }
