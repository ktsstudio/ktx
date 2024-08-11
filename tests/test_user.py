from sentry_sdk import get_isolation_scope

from ktx.user import ContextUser


class TestContextUser:
    def test_user_create(self):
        user = ContextUser()
        assert user.id is None
        assert user.username is None
        assert user.email is None
        assert user.ip is None

    def test_user_set_id(self):
        user = ContextUser()
        user.id = 1
        assert user.id == 1

        scope = get_isolation_scope()
        assert scope._user == {
            "id": 1,
        }

    def test_user_set_username(self):
        user = ContextUser()
        user.username = "test"
        assert user.username == "test"

        scope = get_isolation_scope()
        assert scope._user == {
            "username": "test",
        }

    def test_user_set_email(self):
        user = ContextUser()
        user.email = "test@example.com"
        assert user.email == "test@example.com"

        scope = get_isolation_scope()
        assert scope._user == {"email": "test@example.com"}

    def test_user_set_ip(self):
        user = ContextUser()
        user.ip = "100.200.30.40"
        assert user.ip == "100.200.30.40"

        scope = get_isolation_scope()
        assert scope._user == {"ip_address": "100.200.30.40"}

    def test_user_set_all(self):
        user = ContextUser()
        user.id = 1
        user.username = "test"
        user.email = "test@example.com"
        user.ip = "100.200.30.40"

        scope = get_isolation_scope()
        assert scope._user == {
            "id": 1,
            "username": "test",
            "email": "test@example.com",
            "ip_address": "100.200.30.40",
        }
