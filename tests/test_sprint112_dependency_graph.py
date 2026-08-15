import pytest

from manager.dependency_graph import DependencyGraph
from manager.task import Task


def test_dependency_graph_rejects_cycle():
    a = Task("a", "A", "A", "developer", depends_on=["b"])
    b = Task("b", "B", "B", "developer", depends_on=["a"])
    with pytest.raises(ValueError, match="چرخه"):
        DependencyGraph([a, b])


def test_dependency_graph_reports_ready_tasks():
    a = Task("a", "A", "A", "developer")
    b = Task("b", "B", "B", "developer", depends_on=["a"])
    graph = DependencyGraph([a, b])
    assert [task.id for task in graph.ready({"a", "b"})] == ["a"]
