from pathlib import Path

from agents.public_site_scanner import PublicSiteScanner
from website_audit.pipeline import WebsiteAuditPipeline


class _FakeScanner(PublicSiteScanner):
    def scan(self, start_url: str, *, max_pages=None):
        self.observations = [
            self.build_observation(
                url=start_url,
                status=200,
                title="",
                meta_description="",
                h1_count=0,
                image_count=1,
                images_without_alt=1,
                load_time_ms=4500,
            )
        ]
        return self.generate_report()


def test_pipeline_writes_two_persian_files(tmp_path: Path):
    pipeline = WebsiteAuditPipeline(
        output_dir=tmp_path,
        scanner_factory=lambda: _FakeScanner(),
    )
    result = pipeline.run("https://germantechsat.ir", mode="pre_contract", access=False)

    assert result.language == "fa"
    assert result.problems_path.exists()
    assert result.solutions_path.exists()
    problems = result.problems_path.read_text(encoding="utf-8")
    solutions = result.solutions_path.read_text(encoding="utf-8")
    assert "گزارش مشکلات سایت" in problems
    assert "راه‌های اصلاح" in solutions
    assert "germantechsat.ir" in problems
    assert result.auto_fix_attempted is False
    assert "دسترسی مدیریتی" in result.auto_fix_message


def test_pipeline_rejects_access_in_pre_contract(tmp_path: Path):
    pipeline = WebsiteAuditPipeline(output_dir=tmp_path, scanner_factory=lambda: _FakeScanner())
    try:
        pipeline.run("https://example.com", mode="pre_contract", access=True)
        raise AssertionError("باید خطای دسترسی بدهد")
    except PermissionError as error:
        assert "قبل از قرارداد" in str(error)


def test_runner_agent_returns_json_with_file_paths(tmp_path: Path):
    import json
    from agents.website_audit_runner import WebsiteAuditRunnerAgent
    from manager.task import Task

    agent = WebsiteAuditRunnerAgent(
        pipeline=WebsiteAuditPipeline(output_dir=tmp_path, scanner_factory=lambda: _FakeScanner())
    )
    task = Task(
        id="1",
        title="ممیزی",
        description="URL: https://example.com\nحالت: pre_contract\nدسترسی: ندارد\nممیزی کامل",
        agent="website-audit",
    )
    payload = json.loads(agent.run(task))
    assert payload["language"] == "fa"
    assert "problems_file" in payload
    assert "solutions_file" in payload
    assert Path(payload["problems_file"]).exists()
