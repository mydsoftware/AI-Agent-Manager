from pathlib import Path

from agents.wordpress_installer_agent import WordPressInstallerAgent


def test_installer_prepares_deployment_files(tmp_path: Path):
    package = tmp_path / "site.zip"
    package.write_bytes(b"PK")
    result = WordPressInstallerAgent().prepare(str(package), str(tmp_path / "deploy"))
    assert result.prepared is True
    assert Path(result.install_script_path).exists()
    assert Path(result.instructions_path).exists()
