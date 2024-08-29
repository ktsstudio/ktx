import time
from threading import Thread

from ktx import ctx_wrap, get_current_ctx_or_none
from ktx.simple import SimpleContext


class TestThreads:
    def test_thread(self):
        ctx = SimpleContext()

        called1 = False
        called2 = False

        assert get_current_ctx_or_none() is None

        def f_thread1():
            nonlocal called1
            called1 = True
            ctx_in_thread = get_current_ctx_or_none()
            assert ctx_in_thread is not None

            ctx_in_thread.set("key1", "value1")
            assert ctx_in_thread.get_data() == {"key1": "value1"}

        def f_thread2():
            nonlocal called2
            called2 = True
            ctx_in_thread = get_current_ctx_or_none()
            assert ctx_in_thread is not None

            ctx_in_thread.set("key2", "value2")
            assert ctx_in_thread.get_data() == {"key2": "value2"}

        with ctx_wrap(ctx):
            assert get_current_ctx_or_none() is ctx
            thread1 = Thread(target=f_thread1)
            thread2 = Thread(target=f_thread2)
            thread1.start()
            thread2.start()

            time.sleep(1)

            thread1.join()
            thread2.join()

        assert called1
        assert called2
