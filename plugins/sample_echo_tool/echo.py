"""Sample plugin entrypoint."""

PLUGIN_TYPE = "tool"
PLUGIN_NAME = "echo"


def run(text: str) -> str:
    return f"echo:{text}"
