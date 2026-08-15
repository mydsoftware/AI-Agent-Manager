from manager.api_guard import APIGuard


class AuthStub:
    def validate(self, key):
        return key == "ok"


def test_api_guard_delegates_authentication():
    guard = APIGuard(AuthStub())
    assert guard.authorized("ok") is True
    assert guard.authorized("wrong") is False
    assert guard.authorized(None) is False
