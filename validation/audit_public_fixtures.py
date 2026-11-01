
import heapq
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"


# ---------- T01 and T02: Exact subarray sum ----------
def oracle_subarray_sum(data):
    tokens = list(map(int, data.split()))
    n, k = tokens[0], tokens[1]
    arr = tokens[2:2 + n]

    ans = 0
    for left in range(n):
        current = 0
        for right in range(left, n):
            current += arr[right]
            if current == k:
                ans += 1

    return str(ans)


# ---------- T03: Static range sum ----------
def oracle_t03(data):
    lines = [line.split() for line in data.strip().splitlines()]
    n, q = map(int, lines[0])
    arr = list(map(int, lines[1]))

    answers = []
    for i in range(2, 2 + q):
        left, right = map(int, lines[i])
        answers.append(str(sum(arr[left - 1:right])))

    return "\n".join(answers)


# ---------- T04: Range sum with point updates ----------
def oracle_t04(data):
    lines = [line.split() for line in data.strip().splitlines()]
    n, q = map(int, lines[0])
    arr = list(map(int, lines[1]))

    answers = []

    for line in lines[2:2 + q]:
        if line[0] == "Q":
            left, right = map(int, line[1:])
            answers.append(str(sum(arr[left - 1:right])))

        elif line[0] == "U":
            index, value = map(int, line[1:])
            arr[index - 1] = value

    return "\n".join(answers)


# ---------- T05: Nonnegative shortest paths ----------
def oracle_t05(data):
    tokens = list(map(int, data.split()))
    n, m, src = tokens[:3]

    edges = []
    pos = 3

    for _ in range(m):
        u, v, w = tokens[pos:pos + 3]
        edges.append((u, v, w))
        pos += 3

    INF = 10**30
    dist = [INF] * (n + 1)
    dist[src] = 0

    # Bellman-Ford, independent of Dijkstra reference.
    for _ in range(n - 1):
        changed = False

        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True

        if not changed:
            break

    return "\n".join(
        "-1" if dist[i] == INF else str(dist[i])
        for i in range(1, n + 1)
    )


# ---------- T06: DAG shortest paths, negative edges allowed ----------
def oracle_t06(data):
    tokens = list(map(int, data.split()))
    n, m, src = tokens[:3]

    edges = []
    pos = 3

    for _ in range(m):
        u, v, w = tokens[pos:pos + 3]
        edges.append((u, v, w))
        pos += 3

    INF = 10**30
    dist = [INF] * (n + 1)
    dist[src] = 0

    # Bellman-Ford works for this DAG, including negative edges.
    for _ in range(n - 1):
        changed = False

        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True

        if not changed:
            break

    return "\n".join(
        "UNREACHABLE" if dist[i] == INF else str(dist[i])
        for i in range(1, n + 1)
    )


# ---------- Topological sorting helpers ----------
def read_graph(data):
    tokens = list(map(int, data.split()))
    n, m = tokens[:2]

    graph = [[] for _ in range(n + 1)]
    indegree = [0] * (n + 1)

    pos = 2
    for _ in range(m):
        u, v = tokens[pos:pos + 2]
        pos += 2

        graph[u].append(v)
        indegree[v] += 1

    return n, graph, indegree


def lexicographic_topo(data):
    n, graph, indegree = read_graph(data)

    heap = [
        i for i in range(1, n + 1)
        if indegree[i] == 0
    ]
    heapq.heapify(heap)

    order = []

    while heap:
        u = heapq.heappop(heap)
        order.append(u)

        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                heapq.heappush(heap, v)

    if len(order) != n:
        return None

    return order


# ---------- T07: Any valid topological ordering ----------
def validate_topological(data, output):
    n, graph, _ = read_graph(data)
    tokens = output.split()

    if len(tokens) == 1 and tokens[0].upper() == "IMPOSSIBLE":
        return lexicographic_topo(data) is None

    try:
        order = list(map(int, tokens))
    except ValueError:
        return False

    if len(order) != n or sorted(order) != list(range(1, n + 1)):
        return False

    position = [0] * (n + 1)

    for i, vertex in enumerate(order):
        position[vertex] = i

    for u in range(1, n + 1):
        for v in graph[u]:
            if position[u] >= position[v]:
                return False

    return True


# ---------- T08: Lexicographically smallest topological ordering ----------
def validate_t08(data, output):
    expected = lexicographic_topo(data)
    tokens = output.split()

    if expected is None:
        return len(tokens) == 1 and tokens[0].upper() == "IMPOSSIBLE"

    try:
        actual = list(map(int, tokens))
    except ValueError:
        return False

    return actual == expected


# ---------- Main audit ----------
def main():
    passed = 0
    failed = 0
    total = 0

    print("=" * 65)
    print("CONSTRAINTFLIP PUBLIC FIXTURE AUDIT")
    print("=" * 65)

    for task_id in [f"T{i:02d}" for i in range(1, 9)]:
        task_dirs = sorted(
            p for p in TASKS_DIR.iterdir()
            if p.is_dir() and p.name.startswith(task_id + "_")
        )

        if not task_dirs:
            print(f"\n{task_id}: TASK DIRECTORY MISSING")
            failed += 1
            continue

        task_dir = task_dirs[0]
        test_files = sorted((task_dir / "tests").glob("*.in"))

        print(f"\n--- {task_id} ---")

        if not test_files:
            print("FAIL: No public test fixtures found")
            failed += 1
            continue

        task_passed = 0
        task_failed = 0

        for input_file in test_files:
            total += 1
            output_file = input_file.with_suffix(".out")

            try:
                if not output_file.exists():
                    raise FileNotFoundError("Missing .out file")

                data = input_file.read_text(encoding="utf-8")
                actual = output_file.read_text(encoding="utf-8").strip()

                if task_id in ("T01", "T02"):
                    expected = oracle_subarray_sum(data)
                    valid = actual == expected

                elif task_id == "T03":
                    expected = oracle_t03(data)
                    valid = actual == expected

                elif task_id == "T04":
                    expected = oracle_t04(data)
                    valid = actual == expected

                elif task_id == "T05":
                    expected = oracle_t05(data)
                    valid = actual.split() == expected.split()

                elif task_id == "T06":
                    expected = oracle_t06(data)
                    valid = actual.split() == expected.split()

                elif task_id == "T07":
                    expected = "valid topological ordering"
                    valid = validate_topological(data, actual)

                elif task_id == "T08":
                    expected = "lexicographically smallest ordering"
                    valid = validate_t08(data, actual)

                else:
                    valid = False
                    expected = "unsupported task"

                if valid:
                    task_passed += 1
                    passed += 1
                    print(f"PASS: {input_file.name}")

                else:
                    task_failed += 1
                    failed += 1
                    print(f"FAIL: {input_file.name}")
                    print(f"  Existing output: {actual!r}")
                    print(f"  Oracle result:   {expected!r}")

            except Exception as exc:
                task_failed += 1
                failed += 1
                print(f"ERROR: {input_file.name}: {exc}")

        print(
            f"{task_id} result: "
            f"{task_passed} passed, {task_failed} failed"
        )

    print("\n" + "=" * 65)
    print("FINAL AUDIT SUMMARY")
    print("=" * 65)
    print(f"Total fixtures: {total}")
    print(f"Passed:         {passed}")
    print(f"Failed:         {failed}")

    if failed == 0 and total > 0:
        print("\nAUDIT RESULT: PASS")
    else:
        print("\nAUDIT RESULT: FAIL")
        sys_exit = 1
        raise SystemExit(sys_exit)


if __name__ == "__main__":
    main()
