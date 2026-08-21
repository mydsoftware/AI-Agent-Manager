def test_wordpress_connection_http_api_imports_api_from_correct_module():
    from agents.wordpress_connection_http_api import WordPressConnectionHttpApi
    from agents.wordpress_connection_api import WordPressConnectionApi

    api = WordPressConnectionHttpApi()
    assert isinstance(api.api, WordPressConnectionApi)
