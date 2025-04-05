import pytest
from sentry_sdk import get_isolation_scope

from ktx.adapters.sentry import SentryUserAdapter
from ktx.bind import ctx_user_bind
from ktx.user import ContextUser, ContextUserFactory
from ktx.vars import get_current_ctx_user, get_current_ctx_user_or_none


class TestContextUser:
    def test_user_create(self):
        user = ContextUser()
        assert user.get_id() is None
        assert user.get_username() is None
        assert user.get_email() is None
        assert user.get_ip_address() is None

    def test_user_set_id(self):
        user = ContextUser()
        user.set_id(1)
        assert user.get_id() == 1

    def test_user_set_username(self):
        user = ContextUser()
        user.set_username("test")
        assert user.get_username() == "test"

    def test_user_set_email(self):
        user = ContextUser()
        user.set_email("test@example.com")
        assert user.get_email() == "test@example.com"

    def test_user_set_ip(self):
        user = ContextUser()
        user.set_ip_address("100.200.30.40")
        assert user.get_ip_address() == "100.200.30.40"

    def test_user_with_sentry_adapter(self):
        user = ContextUser(adapters=[SentryUserAdapter()])
        user.set_id(1)
        user.set_username("test")
        user.set_email("test@example.com")
        user.set_ip_address("100.200.30.40")

        scope = get_isolation_scope()
        assert scope._user == {
            "id": 1,
            "username": "test",
            "email": "test@example.com",
            "ip_address": "100.200.30.40",
        }


class TestContextUserFactory:
    def test_user_factory_create(self):
        factory = ContextUserFactory()
        user = factory.create()
        assert isinstance(user, ContextUser)
        assert user.get_id() is None
        assert user.get_username() is None
        assert user.get_email() is None
        assert user.get_ip_address() is None

    def test_user_factory_create_with_sentry_adapter(self):
        factory = ContextUserFactory(adapters=[SentryUserAdapter()])
        user = factory.create()
        assert isinstance(user, ContextUser)

        user.set_id(2)
        user.set_username("test1")
        user.set_email("test1@example.com")
        user.set_ip_address("100.200.30.41")

        scope = get_isolation_scope()
        assert scope._user == {
            "id": 2,
            "username": "test1",
            "email": "test1@example.com",
            "ip_address": "100.200.30.41",
        }


class TestUserBind:
    def test_user_bind(self):
        assert get_current_ctx_user_or_none() is None

        with ctx_user_bind(ContextUser()) as user:
            assert get_current_ctx_user_or_none() is user
            assert get_current_ctx_user_or_none(ContextUser) is user

        assert get_current_ctx_user_or_none() is None


class TestContextUserBind:
    def test_basic(self):
        user = ContextUser()

        assert get_current_ctx_user_or_none() is None

        with ctx_user_bind(user):
            assert get_current_ctx_user_or_none() is user

        assert get_current_ctx_user_or_none() is None

    def test_get(self):
        user = ContextUser()

        with ctx_user_bind(user):
            assert get_current_ctx_user() is user

    def test_get_without_bind(self):
        with pytest.raises(RuntimeError) as e:
            _ = get_current_ctx_user()

        assert str(e.value) == "no context user found in current task"

    def test_get_wrong_type(self):
        class _CustomContext(ContextUser):
            pass

        user = ContextUser()

        with pytest.raises(RuntimeError) as e:
            with ctx_user_bind(user):
                _ = get_current_ctx_user(_CustomContext)

        assert (
            str(e.value)
            == "current context user is not an instance of <class 'tests.test_user.TestContextUserBind.test_get_wrong_type.<locals>._CustomContext'> but <class 'ktx.user.ContextUser'>"
        )

    def test_bind_unbind(self):
        user = ContextUser()

        assert get_current_ctx_user_or_none() is None

        b = ctx_user_bind(user)

        assert b.user is user

        b.bind()
        assert get_current_ctx_user_or_none() is user

        b.unbind()
        assert get_current_ctx_user_or_none() is None
