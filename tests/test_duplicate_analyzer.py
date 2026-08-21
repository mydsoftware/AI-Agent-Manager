from agents.duplicate_analyzer import DuplicateAnalyzer
from agents.public_site_scanner import PageObservation


def test_pages_with_same_canonical_are_grouped():
    observations = [
        PageObservation(url="https://example.com/a", status=200, canonical_url="https://example.com/main"),
        PageObservation(url="https://example.com/b", status=200, canonical_url="https://example.com/main"),
        PageObservation(url="https://example.com/c", status=200, canonical_url="https://example.com/other"),
    ]

    groups = DuplicateAnalyzer().analyze(observations)

    assert len(groups) == 1
    assert groups[0].canonical_url == "https://example.com/main"
    assert groups[0].urls == ("https://example.com/a", "https://example.com/b")


def test_url_identity_prevents_false_duplicate():
    observations = [
        PageObservation(url="https://www.example.com/a/", status=200),
        PageObservation(url="https://example.com/a#section", status=200),
    ]

    groups = DuplicateAnalyzer().analyze(observations)

    assert len(groups) == 0
