from api.app import create_manager_app


def test_manager_app_factory_builds_flask_app():
    app = create_manager_app()
    assert app is not None
    assert app.url_map is not None
    assert "/api/wordpress/connection/check" in {rule.rule for rule in app.url_map.iter_rules()}
