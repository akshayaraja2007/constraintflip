
import heapq
from typing import Dict, List, Optional, Tuple


def normalize_output(text: str) -> str:
    """Normalize whitespace without changing token order."""
    return " ".join(text.split())


def compare_outputs(expected: str, actual: str) -> bool:
    return normalize_output(expected) == normalize_output(actual)


def _parse_graph(
    input_text: str,
) -> Optional[Tuple[int, List[List[int]], List[int]]]:
    """
    Parse a directed graph.

    Returns:
        (n, graph, indegree) if valid.
        None if the input is malformed.
    """
    tokens = input_text.split()

    if len(tokens) < 2:
        return None

    try:
        n = int(tokens[0])
        m = int(tokens[1])
    except ValueError:
        return None

    if n < 0 or m < 0:
        return None

    if len(tokens) != 2 + 2 * m:
        return None

    graph = [[] for _ in range(n + 1)]
    indegree = [0] * (n + 1)

    index = 2

    for _ in range(m):
        try:
            u = int(tokens[index])
            v = int(tokens[index + 1])
        except ValueError:
            return None

        index += 2

        if not (1 <= u <= n and 1 <= v <= n):
            return None

        graph[u].append(v)
        indegree[v] += 1

    return n, graph, indegree


def _compute_lexicographic_order(
    input_text: str,
) -> Optional[str]:
    """
    Compute the lexicographically smallest topological ordering.

    Returns None if the graph contains a cycle or input is invalid.
    """
    parsed = _parse_graph(input_text)

    if parsed is None:
        return None

    n, graph, indegree = parsed

    heap = [
        vertex
        for vertex in range(1, n + 1)
        if indegree[vertex] == 0
    ]

    heapq.heapify(heap)

    order = []

    while heap:
        vertex = heapq.heappop(heap)
        order.append(vertex)

        for neighbor in graph[vertex]:
            indegree[neighbor] -= 1

            if indegree[neighbor] == 0:
                heapq.heappush(heap, neighbor)

    if len(order) != n:
        return None

    return " ".join(map(str, order))


def validate_topological_order(
    task_id: str,
    input_text: str,
    output_text: str,
) -> bool:
    """
    Validate any correct topological ordering.

    Checks:
    1. Output contains exactly n vertices.
    2. Every vertex appears exactly once.
    3. Every directed edge u -> v has position[u] < position[v].
    4. IMPOSSIBLE is accepted only when the graph is cyclic.
    """
    parsed = _parse_graph(input_text)

    if parsed is None:
        return False

    n, graph, indegree = parsed
    output = output_text.strip()

    # Determine whether the graph is a DAG.
    remaining = indegree[:]

    queue = [
        vertex
        for vertex in range(1, n + 1)
        if remaining[vertex] == 0
    ]

    head = 0
    processed = 0

    while head < len(queue):
        vertex = queue[head]
        head += 1
        processed += 1

        for neighbor in graph[vertex]:
            remaining[neighbor] -= 1

            if remaining[neighbor] == 0:
                queue.append(neighbor)

    is_dag = processed == n

    if output.upper() == "IMPOSSIBLE":
        return not is_dag

    if not is_dag:
        return False

    try:
        order = list(map(int, output.split()))
    except ValueError:
        return False

    if len(order) != n:
        return False

    position = [0] * (n + 1)

    # Check that every vertex appears exactly once.
    for index, vertex in enumerate(order):
        if not (1 <= vertex <= n):
            return False

        if position[vertex] != 0:
            return False

        position[vertex] = index + 1

    # Check the direction of every edge.
    for u in range(1, n + 1):
        for v in graph[u]:
            if position[u] >= position[v]:
                return False

    return True


def validate_lexicographic_topological_order(
    task_id: str,
    input_text: str,
    output_text: str,
) -> bool:
    """
    Validate the lexicographically smallest topological ordering.

    Uses an independent heap-based reference computation.
    """
    expected = _compute_lexicographic_order(input_text)
    output = output_text.strip()

    if expected is None:
        return output.upper() == "IMPOSSIBLE"

    if output.upper() == "IMPOSSIBLE":
        return False

    try:
        actual_order = list(map(int, output.split()))
        expected_order = list(map(int, expected.split()))
    except ValueError:
        return False

    return actual_order == expected_order


def check_task_output(
    task_id: str,
    input_text: str,
    expected_text: str,
    actual_text: str,
) -> Dict[str, object]:

    actual = actual_text.strip()
    expected = expected_text.strip()

    if task_id == "T07":
        ok = validate_topological_order(
            task_id,
            input_text,
            actual,
        )

        return {
            "correct": ok,
            "validator_used": "validate_topological_order",
            "expected": expected,
            "actual": actual,
        }

    if task_id == "T08":
        ok = validate_lexicographic_topological_order(
            task_id,
            input_text,
            actual,
        )

        return {
            "correct": ok,
            "validator_used": "validate_lexicographic_topological_order",
            "expected": expected,
            "actual": actual,
        }

    ok = compare_outputs(expected, actual)

    return {
        "correct": ok,
        "validator_used": None,
        "expected": expected,
        "actual": actual,
    }
