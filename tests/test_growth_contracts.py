import json

from manager.growth_contracts import parse_artifact


def test_growth_artifact_round_trip():
    artifact = parse_artifact(json.dumps({
        "type": "business_growth_result",
        "phase": "seo",
        "status": "ready",
        "keyword_clusters": ["پروانه کسب"],
    }, ensure_ascii=False))
    assert artifact.phase == "seo"
    assert artifact.payload["keyword_clusters"] == ["پروانه کسب"]
