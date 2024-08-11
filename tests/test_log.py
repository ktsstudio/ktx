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
        ctx.user.username = "some-username"
        assert ktx_add_log(event_dict, ctx) == {
            **event_dict,
            "uq_id": "some-trace-id",
            "data": {"attr1": "value1"},
            "user": {"username": "some-username"},
        }

    def test_event_dict_indirect_ctx(self):
        event_dict = {"some": "value"}
        with SimpleContext("some-trace-id") as ctx:
            ctx.data.attr1 = "value1"
            ctx.user.username = "some-username"

            assert ktx_add_log(event_dict) == {
                **event_dict,
                "uq_id": "some-trace-id",
                "data": {"attr1": "value1"},
                "user": {"username": "some-username"},
            }

    def test_event_dict_direct_ctx_no_private(self):
        event_dict = {"some": "value"}
        ctx = SimpleContext("some-trace-id")
        ctx.data.attr1 = "value1"
        ctx.data._attr2 = "value2"
        ctx.user.username = "some-username"
        assert ktx_add_log(event_dict, ctx) == {
            **event_dict,
            "uq_id": "some-trace-id",
            "data": {"attr1": "value1"},
            "user": {"username": "some-username"},
        }
