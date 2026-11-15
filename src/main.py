"""Главный модуль запуска CLI-приложения."""

import sys
from src.cli import AppConfig, parse_args
from src.fetcher import get_nuget_dependencies, load_test_repo
from src.graph import DependencyGraph
from src.visualizer import to_ascii_tree, to_graphviz


def create_resolver(config: AppConfig):
    """Создаёт функцию получения зависимостей для выбранного режима."""
    if config.test_mode:
        test_data = load_test_repo(config.repo)
        return lambda pkg, _: [(dep, "") for dep in test_data.get(pkg, [])]
    return lambda pkg, ver: get_nuget_dependencies(config.repo, pkg, ver)


def run() -> int:
    """Выполняет основной сценарий работы утилиты."""
    try:
        config = parse_args()
    except (ValueError, FileNotFoundError) as exc:
        print(f"Ошибка параметров: {exc}", file=sys.stderr)
        return 1

    try:
        resolver = create_resolver(config)
        dep_graph = DependencyGraph(config.max_depth, resolver)
adjacency = dep_graph.build(config.package, config.version)
except RuntimeError as exc:
print(f"Ошибка выполнения: {exc}", file=sys.stderr)
return 1
if config.load_order:
print("Порядок загрузки зависимостей:")
print(" -> ".join(dep_graph.load_order))
return 0
print(to_graphviz(config.package, adjacency))
if config.ascii_tree:
print("\nASCII-дерево зависимостей:")
print(to_ascii_tree(config.package, adjacency))
return 0
if name == "main":
sys.exit(run())