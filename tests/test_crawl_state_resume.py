from agents.public_site_scanner import PublicSiteScanner


def test_save_load_resume_preserves_queue_visited_and_failures(tmp_path):
    scanner = PublicSiteScanner()
    scanner.enqueue([
        "https://example.com/",
        "https://example.com/about#team",
        "https://example.com/contact",
    ])
    first = scanner.next_url()
    assert first == "https://example.com/"
    scanner.record_failure("https://example.com/broken", "HTTP 404")

    state_path = tmp_path / "crawl-state.json"
    scanner.save_state(state_path)

    restored = PublicSiteScanner()
    restored.load_state(state_path)

    assert "https://example.com/" in restored.visited
    assert list(restored.queue) == [
        "https://example.com/about",
        "https://example.com/contact",
    ]
    assert restored.failed["https://example.com/broken"] == "HTTP 404"
    assert restored.next_url() == "https://example.com/about"
