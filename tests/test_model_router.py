from manager.model_router import ModelRouter


def test_default_models_match_local_stack() -> None:
    router = ModelRouter()
    assert router.resolve("developer") == "qwen3.5-9b"
    assert router.resolve("coder") == "qwen2.5-coder-7b"
    assert router.resolve("vision") == "qwen3-vl-4b-instruct"
    assert router.resolve("embedding") == "text-embedding-nomic-embed-text-v1.5"


def test_overrides_take_precedence() -> None:
    router = ModelRouter({"coder": "custom-coder"})
    assert router.resolve("coder") == "custom-coder"
