from api.wordpress_connection_route import handle_wordpress_connection_check


class FakeApi:
    def post_check(self, payload):
        return type("Response", (), {"status": 200, "body": {"reachable": True, "authenticated": True, "writer_endpoint_available": True, "message": "موفق"}})()


def test_route_accepts_valid_json():
    status, body = handle_wordpress_connection_check(b'{"site_url":"https://example.com"}', FakeApi())
    assert status == 200
    assert body["authenticated"] is True


def test_route_rejects_invalid_json():
    status, body = handle_wordpress_connection_check(b"not-json", FakeApi())
    assert status == 400
    assert "JSON" in body["message"]


def test_route_rejects_non_object_json():
    status, body = handle_wordpress_connection_check(b"[]", FakeApi())
    assert status == 400
