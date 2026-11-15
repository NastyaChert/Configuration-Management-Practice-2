"""Модуль визуализации графа зависимостей в форматах Graphviz и ASCII."""

GraphMap = dict[str, list[str]]


def to_graphviz(root: str, graph: GraphMap) -> str:
    """Формирует текстовое описание графа на языке Graphviz DOT."""
    lines = ["digraph Dependencies {", '  rankdir=LR;', f'  "{root}";']
    for src, targets in graph.items():
        for dst in targets:
            lines.append(f'  "{src}" -> "{dst}";')
    lines.append("}")
    return "\n".join(lines)


def to_ascii_tree(root: str, graph: GraphMap) -> str:
    """Формирует строковое представление зависимостей в виде ASCII-дерева."""
    lines = [root]
    _build_tree_lines(root, graph, "", {root}, lines)
    return "\n".join(lines)


def _build_tree_lines(
    node: str,
    graph: GraphMap,
    prefix: str,
    path: set[str],
    lines: list[str],
) -> None:
    """Рекурсивно добавляет ветви ASCII-дерева с защитой от циклов."""
    children = graph.get(node, [])
    last_idx = len(children) - 1
    for idx, child in enumerate(children):
        is_last = idx == last_idx
        connector = "└── " if is_last else "├── "
        if child in path:
            lines.append(f"{prefix}{connector}{child} (cycle)")
            continue
        lines.append(f"{prefix}{connector}{child}")
        next_prefix = prefix + ("    " if is_last else "│   ")
        _build_tree_lines(child, graph, next_prefix, path | {child}, lines)