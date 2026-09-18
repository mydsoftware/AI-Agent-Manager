from __future__ import annotations

from unittest.mock import Mock, patch
from urllib.parse import urlparse

from adapters.github_adapter import GitHubAPIClient


def test_get_file_encodes_ref_and_path_without_losing_slashes():
    client = GitHubAPIClient(token="test-token")
    response = Mock()
    response.read.return_value = b"{}"
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)

    with patch("adapters.github_adapter.urlopen", return_value=response) as mocked:
        client.get_file("mydsoftware/AI-Agent-Manager", "docs/a b#c.txt", "feature/security hardening")

    request = mocked.call_args.args[0]
    parsed = urlparse(request.full_url)
    assert parsed.path.endswith("/contents/docs/a%20b%23c.txt")
    assert parsed.query == "ref=feature%2Fsecurity+hardening"


def test_workflow_runs_encodes_branch_and_workflow_id():
    client = GitHubAPIClient(token="test-token")
    response = Mock()
    response.read.return_value = b'{"workflow_runs": []}'
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)

    with patch("adapters.github_adapter.urlopen", return_value=response) as mocked:
        client.workflow_runs(
            "mydsoftware/AI-Agent-Manager",
            branch="feature/security hardening",
            workflow="ci/security workflow.yml",
        )

    request = mocked.call_args.args[0]
    parsed = urlparse(request.full_url)
    assert "/actions/workflows/ci%2Fsecurity%20workflow.yml/runs" in parsed.path
    assert parsed.query == "per_page=10&branch=feature%2Fsecurity+hardening"


def test_compare_encodes_refs_with_slashes_and_special_characters():
    client = GitHubAPIClient(token="test-token")
    response = Mock()
    response.read.return_value = b"{}"
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)

    with patch("adapters.github_adapter.urlopen", return_value=response) as mocked:
        client.compare("mydsoftware/AI-Agent-Manager", "release/v1.0", "feature/a b")

    request = mocked.call_args.args[0]
    assert "/compare/release%2Fv1.0...feature%2Fa%20b" in request.full_url


def test_ci_log_redacts_token_and_common_secret_formats():
    token = "ghp_abcdefghijklmnopqrstuvwxyz1234567890"
    raw = (
        f"Authorization: Bearer {token}\n"
        "token=super-secret-value\n"
        "api_key: another-secret\n"
        "github_pat_abcdefghijklmnopqrstuvwxyz1234567890"
    )

    redacted = GitHubAPIClient._redact_log(raw, token)

    assert token not in redacted
    assert "super-secret-value" not in redacted
    assert "another-secret" not in redacted
    assert "github_pat_abcdefghijklmnopqrstuvwxyz1234567890" not in redacted
    assert "[REDACTED]" in redacted


def test_invalid_repository_is_rejected_before_network_request():
    client = GitHubAPIClient(token="test-token")

    with patch("adapters.github_adapter.urlopen") as mocked:
        try:
            client.get_repository("owner/repo/extra")
        except ValueError as error:
            assert "owner/name" in str(error)
        else:
            raise AssertionError("invalid repository should raise ValueError")

    mocked.assert_not_called()
