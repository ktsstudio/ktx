from ktx import ctx_wrap, get_current_ctx_or_none
from ktx.simple import SimpleContext


class TestWrap:
    def test_basic(self):
        ctx = SimpleContext()

        assert get_current_ctx_or_none() is None

        with ctx_wrap(ctx):
            assert get_current_ctx_or_none() is ctx

        assert get_current_ctx_or_none() is None

    def test_attach_detach(self):
        ctx = SimpleContext()

        assert get_current_ctx_or_none() is None

        wrap = ctx_wrap(ctx)

        wrap.attach()
        assert get_current_ctx_or_none() is ctx

        wrap.detach()
        assert get_current_ctx_or_none() is None
