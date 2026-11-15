"""Модульные тесты для проверки графа зависимостей и визуализации."""
import unittest
from src.graph import DependencyGraph
from src.visualizer import to_ascii_tree, to_graphviz
class TestDependencyGraph(unittest.TestCase):
"""Набор тестов для алгоритма DFS, циклов и порядка загрузки."""
def setUp(self) -> None:
"""Подготавливает тестовый граф с ромбовидной структурой и циклом."""
self.repo = {
"A": ["B", "C"],
"B": ["D"],
"C": ["A", "D"],
"D": [],
}
self.resolver = lambda pkg, _: [(d, "") for d in self.repo.get(pkg, [])]
def test_dfs_and_cycle_detection(self) -> None:
"""Проверяет построение графа и корректную обработку цикла."""
dg = DependencyGraph(max_depth=5, resolver=self.resolver)
adj = dg.build("A", "")
self.assertEqual(adj["A"], ["B", "C"])
self.assertIn(("C", "A"), dg.cycles)
def test_load_order(self) -> None:
"""Проверяет топологический порядок загрузки зависимостей."""
dg = DependencyGraph(max_depth=5, resolver=self.resolver)
dg.build("A", "")
self.assertEqual(dg.load_order, ["D", "B", "C", "A"])
def test_max_depth_limit(self) -> None:
"""Проверяет ограничение глубины анализа."""
dg = DependencyGraph(max_depth=1, resolver=self.resolver)
adj = dg.build("A", "")
self.assertEqual(adj["B"], [])
def test_visualizers(self) -> None:
"""Проверяет вывод в Graphviz и ASCII-дерево."""
dg = DependencyGraph(max_depth=3, resolver=self.resolver)
adj = dg.build("A", "")
dot = to_graphviz("A", adj)
tree = to_ascii_tree("A", adj)
self.assertIn('"A" -> "B";', dot)
self.assertIn("└── C", tree)
if name == "main":
unittest.main()