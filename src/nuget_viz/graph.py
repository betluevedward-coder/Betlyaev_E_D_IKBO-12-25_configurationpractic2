"""Graph algorithms: BFS, Cycle Detection, Topological Sort."""
from collections import deque


def build_bfs_graph(
    root_pkg: str,
    test_graph: dict[str, list[str]] | None,
    repo_url: str,
    version: str,
    fetcher_func,
) -> dict[str, list[str]]:
    """Builds a dependency graph using BFS without recursion."""
    graph = {}
    queue = deque([root_pkg])
    visited = set()

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        graph[current] = []

        if test_graph is not None:
            deps = test_graph.get(current, [])
        else:
            try:
                from .fetcher import parse_nuspec
                xml = fetcher_func(repo_url, current, version)
                deps = parse_nuspec(xml)
            except Exception:
                deps = []

        for dep in deps:
            if dep not in visited:
                queue.append(dep)
            graph[current].append(dep)

    return graph


def _build_reversed_graph(
    graph: dict[str, list[str]]
) -> tuple[dict[str, list[str]], dict[str, int]]:
    """Builds a reversed graph and calculates in-degrees."""
    rev_graph = {node: [] for node in graph}
    in_degree = {node: 0 for node in graph}

    for node, deps in graph.items():
        for dep in deps:
            if dep not in rev_graph:
                rev_graph[dep] = []
                in_degree[dep] = 0
            rev_graph[dep].append(node)
            in_degree[node] += 1
    return rev_graph, in_degree


def _process_queue(
    rev_graph: dict[str, list[str]], in_degree: dict[str, int]
) -> list[str]:
    """Processes the queue for topological sorting."""
    queue = deque([n for n in in_degree if in_degree[n] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in rev_graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return order


def get_loading_order(graph: dict[str, list[str]]) -> list[str]:
    """Determines dependency loading order (Topological Sort)."""
    rev_graph, in_degree = _build_reversed_graph(graph)
    order = _process_queue(rev_graph, in_degree)

    if len(order) != len(in_degree):
        raise ValueError("Cyclic dependency detected! Cannot load.")
    return order
