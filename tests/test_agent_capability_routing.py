from agents.developer_agent import DeveloperAgent
from manager.task import Task


class FakeResponse:
    content = "ok"


class FakeLLM:
    def __init__(self) -> None:
        self.model = None

    def complete(self, messages, model, **kwargs):
        self.model = model
        return FakeResponse()


def test_developer_agent_uses_vision_model_for_vision_task() -> None:
    llm = FakeLLM()
    agent = DeveloperAgent(llm=llm)
    task = Task("vision-1", "تحلیل تصویر", "تصویر را بررسی کن", "developer", capability="vision")

    assert agent.run(task) == "ok"
    assert llm.model == "qwen3-vl-4b-instruct"


def test_developer_agent_uses_coder_model_for_coding_task() -> None:
    llm = FakeLLM()
    agent = DeveloperAgent(llm=llm)
    task = Task("code-1", "کدنویسی", "کد بنویس", "developer", capability="coder")

    assert agent.run(task) == "ok"
    assert llm.model == "qwen2.5-coder-7b"
