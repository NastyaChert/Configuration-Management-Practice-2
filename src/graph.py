"""Модуль построения графа зависимостей методом рекурсивного DFS."""

from typing import Callable

ResolverFn = Callable[[str, str], list[tuple[str, str]]]
GraphMap = dict[str, list[str]]


class DependencyGraph:
    """Хранит граф зависимостей и выполняет обход DFS с рекурсией."""

    def __init__(self, max_depth: int, resolver: ResolverFn) -> None:
        """Инициализирует построитель графа."""
        self.max_depth = max_depth
        self.resolver = resolver
        self.adjacency: GraphMap = {}
        self.cycles: list[tuple[str, str]] = []
        self.load_order: list[str] = []
        self._visited: set[str] = set()
        self._visiting: set[str] = set()

    def build(self, root_pkg: str, root_ver: str) -> GraphMap:
        """Запускает построение графа от корневого пакета."""
        self._dfs(root_pkg, root_ver, depth=0)
        return self.adjacency

    def _dfs(self, pkg: str, ver: str, depth: int) -> None:
        """Рекурсивно обходит зависимости в глубину."""
        self.adjacency.setdefault(pkg, [])
        if depth >= self.max_depth:
            if pkg not in self._visited:
                self._visited.add(pkg)
                self.load_order.append(pkg)
            return

        self._visiting.add(pkg)
        for dep_name, dep_ver in self.resolver(pkg, ver):
            if dep_name not in self.adjacency[pkg]:
                self.adjacency[pkg].append(dep_name)
            if dep_name in self._visiting:
                self.cycles.append((pkg, dep_name))
                continue
            if dep_name not in self._visited:
                self._dfs(dep_name, dep_ver, depth + 1)

        self._visiting.remove(pkg)
        if pkg not in self._visited:
            self._visited.add(pkg)
            self.load_order.append(pkg)