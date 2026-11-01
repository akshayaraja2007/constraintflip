
#!/usr/bin/env python3

import heapq
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"


def write_case(task_dir, name, input_text, output_text):
    tests_dir = task_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    (tests_dir / f"{name}.in").write_text(input_text, encoding="utf-8")
    (tests_dir / f"{name}.out").write_text(output_text, encoding="utf-8")


# =========================================================
# COMMON ORACLE
# =========================================================

def count_subarrays(arr, target):
    ans = 0

    for left in range(len(arr)):
        total = 0

        for right in range(left, len(arr)):
            total += arr[right]

            if total == target:
                ans += 1

    return ans


# =========================================================
# T01: POSITIVE SUBARRAY SUM
# =========================================================

def make_t01_cases():
    task_dir = TASKS_DIR / "T01_positive_subarray"

    cases = [
        ("t01_basic_1", "5 3\n1 2 3 1 1\n", "2\n"),
        ("t01_all_ones", "5 5\n1 1 1 1 1\n", "1\n"),
        ("t01_no_match", "5 20\n1 2 3 4 5\n", "0\n"),
        ("t01_one_match", "6 10\n1 2 3 4 5 6\n", "1\n"),
        ("t01_overlapping", "6 6\n1 2 3 1 2 3\n", "4\n"),
        ("t01_target_total", "4 10\n1 2 3 4\n", "1\n"),
        ("t01_target_too_large", "4 100\n1 2 3 4\n", "0\n"),
        ("t01_repeated_large", "6 13\n5 5 3 5 5 5\n", "3\n"),
    ]

    rnd = random.Random(20261101)

    for i in range(200):
        n = rnd.randint(1, 25)
        arr = [rnd.randint(1, 25) for _ in range(n)]
        target = rnd.randint(1, 200)

        ans = count_subarrays(arr, target)

        inp = f"{n} {target}\n"
        inp += " ".join(map(str, arr)) + "\n"

        cases.append((f"t01_rand_{i}", inp, f"{ans}\n"))

    for name, inp, out in cases:
        write_case(task_dir, name, inp, out)


# =========================================================
# T02: SIGNED SUBARRAY SUM
# =========================================================

def make_t02_cases():
    task_dir = TASKS_DIR / "T02_signed_subarray"

    cases = [
        ("t02_basic_1", "4 0\n1 -1 2 -2\n", "3\n"),
        ("t02_zero_target", "5 0\n0 0 0 0 0\n", "15\n"),
        ("t02_large_negative", "5 -5\n-2 -3 1 4 -5\n", "3\n"),
        ("t02_prefix_repeat", "6 0\n1 -1 1 -1 1 -1\n", "9\n"),
        ("t02_mixed", "5 3\n1 2 -1 3 1\n", "3\n"),
    ]

    rnd = random.Random(20261102)

    for i in range(200):
        n = rnd.randint(1, 25)
        arr = [rnd.randint(-25, 25) for _ in range(n)]
        target = rnd.randint(-100, 100)

        ans = count_subarrays(arr, target)

        inp = f"{n} {target}\n"
        inp += " ".join(map(str, arr)) + "\n"

        cases.append((f"t02_rand_{i}", inp, f"{ans}\n"))

    for name, inp, out in cases:
        write_case(task_dir, name, inp, out)


# =========================================================
# T03: STATIC RANGE SUM
# =========================================================

def make_t03_cases():
    task_dir = TASKS_DIR / "T03_static_range_sum"

    cases = [
        (
            "t03_basic",
            "5 3\n1 2 3 4 5\n1 3\n2 5\n3 3\n",
            "6\n14\n3\n",
        ),
        ("t03_single", "1 1\n-7\n1 1\n", "-7\n"),
        (
            "t03_full",
            "4 2\n-2 3 -1 4\n1 4\n4 4\n",
            "4\n4\n",
        ),
    ]

    rnd = random.Random(20261103)

    for i in range(200):
        n = rnd.randint(1, 30)
        arr = [rnd.randint(-50, 50) for _ in range(n)]
        q = rnd.randint(1, 20)

        lines = [f"{n} {q}", " ".join(map(str, arr))]
        outputs = []

        for _ in range(q):
            left = rnd.randint(1, n)
            right = rnd.randint(left, n)

            outputs.append(str(sum(arr[left - 1:right])))
            lines.append(f"{left} {right}")

        inp = "\n".join(lines) + "\n"
        out = "\n".join(outputs) + "\n"

        cases.append((f"t03_rand_{i}", inp, out))

    for name, inp, out in cases:
        write_case(task_dir, name, inp, out)


# =========================================================
# T04: DYNAMIC RANGE SUM
# =========================================================

def make_t04_cases():
    task_dir = TASKS_DIR / "T04_dynamic_range_sum"

    cases = [
        (
            "t04_basic",
            "5 6\n1 2 3 4 5\nQ 1 5\nU 3 10\nQ 2 4\nQ 1 5\nU 5 1\nQ 3 5\n",
            "15\n16\n22\n15\n",
        ),
        (
            "t04_repeated",
            "5 6\n5 5 5 5 5\nQ 1 5\nU 2 0\nQ 1 5\nU 4 -10\nQ 2 4\nQ 1 1\n",
            "25\n20\n-5\n5\n",
        ),
        (
            "t04_negative",
            "4 4\n1 -2 3 -4\nU 2 10\nQ 1 4\nU 4 -1\nQ 2 4\n",
            "10\n12\n",
        ),
    ]

    rnd = random.Random(20261104)

    for i in range(200):
        n = rnd.randint(1, 20)
        arr = [rnd.randint(-20, 20) for _ in range(n)]
        q = rnd.randint(1, 30)

        lines = [f"{n} {q}", " ".join(map(str, arr))]
        outputs = []

        for _ in range(q):
            operation = rnd.choice(["U", "Q"])

            if operation == "U":
                index = rnd.randint(1, n)
                value = rnd.randint(-50, 50)

                arr[index - 1] = value
                lines.append(f"U {index} {value}")

            else:
                left = rnd.randint(1, n)
                right = rnd.randint(left, n)

                outputs.append(str(sum(arr[left - 1:right])))
                lines.append(f"Q {left} {right}")

        inp = "\n".join(lines) + "\n"
        out = "\n".join(outputs) + "\n"

        cases.append((f"t04_rand_{i}", inp, out))

    for name, inp, out in cases:
        write_case(task_dir, name, inp, out)


# =========================================================
# T05: DIJKSTRA
# =========================================================

def dijkstra_oracle(n, edges, source):
    graph = [[] for _ in range(n + 1)]

    for u, v, weight in edges:
        graph[u].append((v, weight))

    inf = 10**30

    dist = [inf] * (n + 1)
    dist[source] = 0

    pq = [(0, source)]

    while pq:
        current_dist, u = heapq.heappop(pq)

        if current_dist != dist[u]:
            continue

        for v, weight in graph[u]:
            candidate = current_dist + weight

            if candidate < dist[v]:
                dist[v] = candidate
                heapq.heappush(pq, (candidate, v))

    return [
        str(-1 if dist[v] == inf else dist[v])
        for v in range(1, n + 1)
    ]


def make_t05_cases():
    task_dir = TASKS_DIR / "T05_dijkstra"

    cases = [
        (
            "t05_basic",
            "4 5 1\n1 2 2\n1 3 5\n2 3 1\n2 4 3\n3 4 1\n",
            "0\n2\n3\n4\n",
        ),
        (
            "t05_disconnected",
            "4 2 1\n2 3 4\n4 3 2\n",
            "0\n-1\n-1\n-1\n",
        ),
        (
            "t05_zero_weight",
            "3 3 1\n1 2 0\n2 3 0\n1 3 5\n",
            "0\n0\n0\n",
        ),
    ]

    rnd = random.Random(20261105)

    for i in range(200):
        n = rnd.randint(1, 10)
        m = rnd.randint(0, 18)
        source = rnd.randint(1, n)

        edges = []

        for _ in range(m):
            u = rnd.randint(1, n)
            v = rnd.randint(1, n)
            weight = rnd.randint(0, 30)
            edges.append((u, v, weight))

        lines = [f"{n} {len(edges)} {source}"]

        for u, v, weight in edges:
            lines.append(f"{u} {v} {weight}")

        inp = "\n".join(lines) + "\n"
        out = "\n".join(
            dijkstra_oracle(n, edges, source)
        ) + "\n"

        cases.append((f"t05_rand_{i}", inp, out))

    for name, inp, out in cases:
        write_case(task_dir, name, inp, out)


# =========================================================
# T06: DAG SHORTEST PATH
# =========================================================

def dag_shortest_path_oracle(n, edges, source):
    graph = [[] for _ in range(n + 1)]
    indegree = [0] * (n + 1)

    for u, v, weight in edges:
        graph[u].append((v, weight))
        indegree[v] += 1

    queue = [
        v for v in range(1, n + 1)
        if indegree[v] == 0
    ]

    topo = []

    while queue:
        u = queue.pop()

        topo.append(u)

        for v, weight in graph[u]:
            indegree[v] -= 1

            if indegree[v] == 0:
                queue.append(v)

    if len(topo) != n:
        raise ValueError("Generated graph is not a DAG")

    inf = 10**30

    dist = [inf] * (n + 1)
    dist[source] = 0

    for u in topo:
        if dist[u] == inf:
            continue

        for v, weight in graph[u]:
            candidate = dist[u] + weight

            if candidate < dist[v]:
                dist[v] = candidate

    return [
        "UNREACHABLE" if dist[v] == inf else str(dist[v])
        for v in range(1, n + 1)
    ]


def make_t06_cases():
    task_dir = TASKS_DIR / "T06_dag_shortest_path"

    cases = [
        (
            "t06_basic",
            "4 4 1\n1 2 2\n1 3 -1\n2 3 3\n2 4 -4\n",
            "0\n2\n-1\n-2\n",
        ),
        (
            "t06_negative_shortest_minus1",
            "3 3 1\n1 2 -1\n2 3 -1\n1 3 -2\n",
            "0\n-1\n-2\n",
        ),
        (
            "t06_unreachable",
            "4 2 1\n2 3 5\n3 4 -2\n",
            "0\nUNREACHABLE\nUNREACHABLE\nUNREACHABLE\n",
        ),
    ]

    rnd = random.Random(20261106)

    for i in range(200):
        n = rnd.randint(1, 10)

        order = list(range(1, n + 1))
        rnd.shuffle(order)

        edges = []

        for index, u in enumerate(order[:-1]):
            for v in order[index + 1:]:
                if rnd.random() < 0.3:
                    weight = rnd.randint(-12, 15)
                    edges.append((u, v, weight))

        source = rnd.randint(1, n)

        lines = [f"{n} {len(edges)} {source}"]

        for u, v, weight in edges:
            lines.append(f"{u} {v} {weight}")

        inp = "\n".join(lines) + "\n"
        out = "\n".join(
            dag_shortest_path_oracle(n, edges, source)
        ) + "\n"

        cases.append((f"t06_rand_{i}", inp, out))

    for name, inp, out in cases:
        write_case(task_dir, name, inp, out)


# =========================================================
# T07: ANY VALID TOPOLOGICAL ORDER
# =========================================================

def topological_order_oracle(n, edges):
    graph = [[] for _ in range(n + 1)]
    indegree = [0] * (n + 1)

    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1

    queue = [
        v for v in range(1, n + 1)
        if indegree[v] == 0
    ]

    order = []

    while queue:
        u = queue.pop(0)
        order.append(u)

        for v in graph[u]:
            indegree[v] -= 1

            if indegree[v] == 0:
                queue.append(v)

    if len(order) != n:
        return "IMPOSSIBLE\n"

    return " ".join(map(str, order)) + "\n"


def make_t07_cases():
    task_dir = TASKS_DIR / "T07_topological_order"

    cases = [
        (
            "t07_basic",
            "4 4\n1 2\n1 3\n2 4\n3 4\n",
            "1 2 3 4\n",
        ),
        (
            "t07_cycle",
            "3 3\n1 2\n2 3\n3 1\n",
            "IMPOSSIBLE\n",
        ),
        (
            "t07_disconnected",
            "4 1\n2 3\n",
            "1 2 3 4\n",
        ),
    ]

    rnd = random.Random(20261107)

    for i in range(200):
        n = rnd.randint(1, 8)
        edges = []

        for u in range(1, n + 1):
            for v in range(u + 1, n + 1):
                if rnd.random() < 0.3:
                    edges.append((u, v))

        if not edges and n > 1:
            edges = [(1, 2)]

        lines = [f"{n} {len(edges)}"]

        for u, v in edges:
            lines.append(f"{u} {v}")

        inp = "\n".join(lines) + "\n"
        out = topological_order_oracle(n, edges)

        cases.append((f"t07_rand_{i}", inp, out))

    for name, inp, out in cases:
        write_case(task_dir, name, inp, out)


# =========================================================
# T08: LEXICOGRAPHIC TOPOLOGICAL ORDER
# =========================================================

def lexicographic_topological_oracle(n, edges):
    graph = [[] for _ in range(n + 1)]
    indegree = [0] * (n + 1)

    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1

    pq = []

    for v in range(1, n + 1):
        if indegree[v] == 0:
            heapq.heappush(pq, v)

    order = []

    while pq:
        u = heapq.heappop(pq)
        order.append(u)

        for v in graph[u]:
            indegree[v] -= 1

            if indegree[v] == 0:
                heapq.heappush(pq, v)

    if len(order) != n:
        return "IMPOSSIBLE\n"

    return " ".join(map(str, order)) + "\n"


def make_t08_cases():
    task_dir = TASKS_DIR / "T08_lexicographic_topological"

    cases = [
        (
            "t08_basic",
            "4 4\n1 2\n1 3\n2 4\n3 4\n",
            "1 2 3 4\n",
        ),
        (
            "t08_cycle",
            "3 3\n1 2\n2 3\n3 1\n",
            "IMPOSSIBLE\n",
        ),
        (
            "t08_many_roots",
            "5 4\n1 3\n2 3\n3 5\n4 5\n",
            "1 2 3 4 5\n",
        ),
    ]

    rnd = random.Random(20261108)

    for i in range(200):
        n = rnd.randint(1, 8)
        edges = []

        for u in range(1, n + 1):
            for v in range(u + 1, n + 1):
                if rnd.random() < 0.35:
                    edges.append((u, v))

        if not edges and n > 1:
            edges = [(1, 2)]

        lines = [f"{n} {len(edges)}"]

        for u, v in edges:
            lines.append(f"{u} {v}")

        inp = "\n".join(lines) + "\n"
        out = lexicographic_topological_oracle(n, edges)

        cases.append((f"t08_rand_{i}", inp, out))

    for name, inp, out in cases:
        write_case(task_dir, name, inp, out)


# =========================================================
# MAIN
# =========================================================

def main():
    generators = [
        make_t01_cases,
        make_t02_cases,
        make_t03_cases,
        make_t04_cases,
        make_t05_cases,
        make_t06_cases,
        make_t07_cases,
        make_t08_cases,
    ]

    for generator in generators:
        generator()
        print(f"Generated: {generator.__name__}")

    print("\nHidden tests generated successfully.")


if __name__ == "__main__":
    main()
