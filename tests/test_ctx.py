import pytest
from sentry_sdk import get_isolation_scope

from ktx import ctx_bind, get_current_ctx, get_current_ctx_or_none
from ktx.adapters.sentry import SentryDataAdapter
from ktx.ctx import Context, ContextFactory


class TestGeneralContext:
    def test_make(self):
        ctx = Context("some-ktx-id")
        assert ctx.ktx_id() == "some-ktx-id"
        assert ctx.get_data() == {}
        assert get_current_ctx_or_none() is None

    def test_set_get(self):
        ctx = Context("some-ktx-id")
        ctx.set("attr1", "val1")
        ctx.set("attr2", "val2")

        assert ctx.get("attr1") == "val1"
        assert ctx.get("attr2") == "val2"

        assert ctx.get_data() == {
            "attr1": "val1",
            "attr2": "val2",
        }

        with pytest.raises(TypeError):
            ctx.get_data()["qwe"] = "qweqwe"  # type: ignore[index]

    def test_ctx_manager(self):
        assert get_current_ctx_or_none() is None

        ctx = Context("some-ktx-id")
        with ctx_bind(ctx) as ctx:
            assert get_current_ctx_or_none() is ctx
            assert get_current_ctx_or_none(Context) is ctx

        assert get_current_ctx_or_none() is None

    def test_ctx_manager_with_sentry(self):
        assert get_current_ctx_or_none() is None

        ctx = Context(
            "some-ktx-id",
            adapters=[
                SentryDataAdapter(),
            ],
        )
        with ctx_bind(ctx) as ctx:
            assert get_current_ctx_or_none() is ctx
            assert get_current_ctx_or_none(Context) is ctx

            ctx.set("attr1", "val1")
            ctx.set("_attr2", "val2")

            assert get_isolation_scope()._extras["attr1"] == "val1"
            assert "_attr2" not in get_isolation_scope()._extras

        assert get_current_ctx_or_none() is None

    def test_copy_data(self):
        ctx1 = Context("some-ktx-id")
        ctx1.set("attr1", "val1")
        ctx1.set("attr2", "val2")

        ctx2 = Context("some-ktx-id2", data=ctx1.get_data())

        assert ctx2.get("attr1") == "val1"
        assert ctx2.get("attr2") == "val2"


class TestContextFactory:
    def test_create_context(self):
        factory = ContextFactory()
        ctx = factory.create("some-ktx-id")
        assert isinstance(ctx, Context)
        assert ctx.ktx_id() == "some-ktx-id"

    def test_inherit_data(self):
        factory = ContextFactory(inherit_data=True)

        with ctx_bind(factory.create("id1")) as parent_ctx:
            parent_ctx.set("attr1", "val1")
            parent_ctx.set("attr2", "val2")

            with ctx_bind(factory.create("id2")) as child_ctx:
                assert child_ctx.get("attr1") == "val1"
                assert child_ctx.get("attr2") == "val2"

                child_ctx.set("attr2", "val3")
                assert child_ctx.get("attr2") == "val3"

            assert parent_ctx.get("attr2") == "val2"

    def test_create_default(self):
        factory = ContextFactory()
        ctx = factory.create()
        assert ctx.ktx_id() != ""

    def test_create_custom_ktx_id_maker(self):
        def ktx_id_maker() -> str:
            return "custom-ktx-id"

        factory = ContextFactory(ktx_id_maker=ktx_id_maker)
        ctx = factory.create()
        assert ctx.ktx_id() == "custom-ktx-id"

    def test_create_with_sentry_adapter(self):
        factory = ContextFactory(adapters=[SentryDataAdapter()])
        ctx = factory.create()

        ctx.set("attr1", "val1")
        ctx.set("_attr2", "val2")

        assert get_isolation_scope()._extras["attr1"] == "val1"
        assert "_attr2" not in get_isolation_scope()._extras


class TestContextBind:
    def test_basic(self):
        ctx = Context("id1")

        assert get_current_ctx_or_none() is None

        with ctx_bind(ctx):
            assert get_current_ctx_or_none() is ctx

        assert get_current_ctx_or_none() is None

    def test_get(self):
        ctx = Context("id1")

        with ctx_bind(ctx):
            assert get_current_ctx() is ctx

    def test_get_without_bind(self):
        with pytest.raises(RuntimeError) as e:
            _ = get_current_ctx()

        assert str(e.value) == "no context found in current task"

    def test_get_wrong_type(self):
        class _CustomContext(Context):
            pass

        ctx = Context("id1")

        with pytest.raises(RuntimeError) as e:
            with ctx_bind(ctx):
                _ = get_current_ctx(_CustomContext)

        assert (
            str(e.value)
            == "current context is not an instance of <class 'tests.test_ctx.TestContextBind.test_get_wrong_type.<locals>._CustomContext'> but <class 'ktx.ctx.Context'>"
        )

    def test_bind_unbind(self):
        ctx = Context("id1")

        assert get_current_ctx_or_none() is None

        b = ctx_bind(ctx)

        assert b.ctx is ctx

        b.bind()
        assert get_current_ctx_or_none() is ctx

        b.unbind()
        assert get_current_ctx_or_none() is None
