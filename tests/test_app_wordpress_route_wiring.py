from api.app import app


def test_main_flask_app_registers_wordpress_connection_route():
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/api/wordpress/connection/check" in routes
