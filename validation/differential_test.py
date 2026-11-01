#!/usr/bin/env python3
import itertools
import os
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = ROOT / 'reference'
TASKS_DIR = ROOT / 'tasks'


class TaskOracle:
    @staticmethod
    def t01(inp: str) -> str:
        s = inp.strip().split()
        n, k = map(int, s[:2])
        arr = list(map(int, s[2:2 + n]))
        ans = 0
        for l in range(n):
            cur = 0
            for r in range(l, n):
                cur += arr[r]
                if cur == k:
                    ans += 1
        return str(ans) + '\n'

    @staticmethod
    def t02(inp: str) -> str:
        s = inp.strip().split()
        n, k = map(int, s[:2])
        arr = list(map(int, s[2:2 + n]))
        ans = 0
        for l in range(n):
            cur = 0
            for r in range(l, n):
                cur += arr[r]
                if cur == k:
                    ans += 1
        return str(ans) + '\n'

    @staticmethod
    def t03(inp: str) -> str:
        lines = [ln.strip() for ln in inp.strip().splitlines() if ln.strip()]
        n, q = map(int, lines[0].split())
        arr = list(map(int, lines[1].split()))
        out = []
        for i in range(2, 2 + q):
            l, r = map(int, lines[i].split())
            out.append(str(sum(arr[l - 1:r])))
        return '\n'.join(out) + '\n'

    @staticmethod
    def t04(inp: str) -> str:
        lines = [ln.strip() for ln in inp.strip().splitlines() if ln.strip()]
        n, q = map(int, lines[0].split())
        arr = list(map(int, lines[1].split()))
        out = []
        for ln in lines[2:]:
            parts = ln.split()
            if parts[0] == 'Q':
                l, r = map(int, parts[1:])
                out.append(str(sum(arr[l - 1:r])))
            else:
                _, x, v = parts
                arr[int(x) - 1] = int(v)
        return '\n'.join(out) + '\n'

    @staticmethod
    def t05(inp: str) -> str:
        lines = [ln.strip() for ln in inp.strip().splitlines() if ln.strip()]
        n, m, src = map(int, lines[0].split())
        g = [[] for _ in range(n + 1)]
        for ln in lines[1:1 + m]:
            u, v, w = map(int, ln.split())
            g[u].append((v, w))
        INF = 10**18
        dist = [INF] * (n + 1)
        dist[src] = 0
        for _ in range(n - 1):
            changed = False
            for u in range(1, n + 1):
                if dist[u] == INF:
                    continue
                for v, w in g[u]:
                    nd = dist[u] + w
                    if nd < dist[v]:
                        dist[v] = nd
                        changed = True
            if not changed:
                break
        out = []
        for i in range(1, n + 1):
            out.append(str(-1 if dist[i] == INF else dist[i]))
        return '\n'.join(out) + '\n'

    @staticmethod
    def t06(inp: str) -> str:
        lines = [ln.strip() for ln in inp.strip().splitlines() if ln.strip()]
        n, m, src = map(int, lines[0].split())
        g = [[] for _ in range(n + 1)]
        indeg = [0] * (n + 1)
        for ln in lines[1:1 + m]:
            u, v, w = map(int, ln.split())
            g[u].append((v, w))
            indeg[v] += 1
        q = [i for i in range(1, n + 1) if indeg[i] == 0]
        topo = []
        while q:
            u = q.pop(0)
            topo.append(u)
            for v, _ in g[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        dist = [None] * (n + 1)
        dist[src] = 0
        for u in topo:
            if dist[u] is None:
                continue
            for v, w in g[u]:
                nd = dist[u] + w
                if dist[v] is None or nd < dist[v]:
                    dist[v] = nd
        out = []
        for i in range(1, n + 1):
            if dist[i] is None:
                out.append('UNREACHABLE')
            else:
                out.append(str(dist[i]))
        return '\n'.join(out) + '\n'

    @staticmethod
    def t07(inp: str) -> str:
        lines = [ln.strip() for ln in inp.strip().splitlines() if ln.strip()]
        n, m = map(int, lines[0].split())
        g = [[] for _ in range(n + 1)]
        indeg = [0] * (n + 1)
        for ln in lines[1:1 + m]:
            u, v = map(int, ln.split())
            g[u].append(v)
            indeg[v] += 1
        q = [i for i in range(1, n + 1) if indeg[i] == 0]
        order = []
        while q:
            u = q.pop(0)
            order.append(u)
            for v in g[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        if len(order) != n:
            return 'IMPOSSIBLE\n'
        return ' '.join(map(str, order)) + '\n'

    @staticmethod
    def t08(inp: str) -> str:
        lines = [ln.strip() for ln in inp.strip().splitlines() if ln.strip()]
        n, m = map(int, lines[0].split())
        g = [[] for _ in range(n + 1)]
        indeg = [0] * (n + 1)
        for ln in lines[1:1 + m]:
            u, v = map(int, ln.split())
            g[u].append(v)
            indeg[v] += 1
        heap = [i for i in range(1, n + 1) if indeg[i] == 0]
        import heapq
        heapq.heapify(heap)
        order = []
        while heap:
            u = heapq.heappop(heap)
            order.append(u)
            for v in sorted(g[u]):
                indeg[v] -= 1
                if indeg[v] == 0:
                    heapq.heappush(heap, v)
        if len(order) != n:
            return 'IMPOSSIBLE\n'
        return ' '.join(map(str, order)) + '\n'


def run_ref(task_id: str, case_in: str) -> str:
    exe = REFERENCE_DIR / f'{task_id}.exe'
    if not exe.exists():
        compile_proc = subprocess.run(['g++', '-std=c++17', '-O2', str(REFERENCE_DIR / f'{task_id}.cpp'), '-o', str(exe)], capture_output=True, text=True)
        if compile_proc.returncode != 0:
            raise RuntimeError(f'compile failed for {task_id}: {compile_proc.stderr}')
    proc = subprocess.run([str(exe)], input=case_in, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f'runtime failure for {task_id}: {proc.stderr}')
    return proc.stdout


def check_case(task_id: str, case_in: str, expected: str):
    actual = run_ref(task_id, case_in)
    if actual.strip() != expected.strip():
        raise AssertionError(f'{task_id} mismatch:\nIN={case_in!r}\nEXPECTED={expected!r}\nACTUAL={actual!r}')


def random_cases():
    rnd = random.Random(20261109)
    cases = []
    # T01: positive exact-sum subarray counts
    for _ in range(1000):
        n = rnd.randint(1, 12)
        arr = [rnd.randint(1, 30) for _ in range(n)]
        k = rnd.randint(1, 100)
        cases.append(("T01", f"{n} {k}\n" + ' '.join(map(str, arr)) + '\n'))
    cases.append(("T01", "5 5\n1 1 1 1 1\n"))
    cases.append(("T01", "6 10\n1 2 3 4 5 6\n"))
    cases.append(("T01", "5 20\n1 2 3 4 5\n"))
    cases.append(("T01", "6 6\n1 2 3 1 2 3\n"))
    for _ in range(1000):
        n = rnd.randint(1, 12)
        arr = [rnd.randint(-30, 30) for _ in range(n)]
        k = rnd.randint(-100, 100)
        cases.append(("T02", f"{n} {k}\n" + ' '.join(map(str, arr)) + '\n'))
    # T03-T08 follow
    for _ in range(1000):
        n = rnd.randint(1, 12)
        arr = [rnd.randint(-30, 30) for _ in range(n)]
        q = rnd.randint(1, 10)
        lines = [f"{n} {q}", ' '.join(map(str, arr))]
        for _ in range(q):
            l = rnd.randint(1, n)
            r = rnd.randint(l, n)
            lines.append(f"{l} {r}")
        cases.append(("T03", '\n'.join(lines) + '\n'))
    for _ in range(1000):
        n = rnd.randint(1, 10)
        arr = [rnd.randint(-20, 20) for _ in range(n)]
        q = rnd.randint(1, 20)
        lines = [f"{n} {q}", ' '.join(map(str, arr))]
        for _ in range(q):
            op = rnd.choice(['Q', 'U'])
            if op == 'Q':
                l = rnd.randint(1, n)
                r = rnd.randint(l, n)
                lines.append(f"Q {l} {r}")
            else:
                x = rnd.randint(1, n)
                v = rnd.randint(-50, 50)
                arr[x - 1] = v
                lines.append(f"U {x} {v}")
        cases.append(("T04", '\n'.join(lines) + '\n'))
    for _ in range(1000):
        n = rnd.randint(1, 8)
        m = rnd.randint(0, 12)
        src = rnd.randint(1, n)
        lines = [f"{n} {m} {src}"]
        for _ in range(m):
            u = rnd.randint(1, n)
            v = rnd.randint(1, n)
            w = rnd.randint(0, 30)
            lines.append(f"{u} {v} {w}")
        cases.append(("T05", '\n'.join(lines) + '\n'))
    for _ in range(1000):
        n = rnd.randint(1, 8)
        edges = []
        for u in range(1, n + 1):
            for v in range(u + 1, n + 1):
                if rnd.random() < 0.35:
                    edges.append((u, v, rnd.randint(-10, 15)))
        src = rnd.randint(1, n)
        lines = [f"{n} {len(edges)} {src}"]
        for u, v, w in edges:
            lines.append(f"{u} {v} {w}")
        cases.append(("T06", '\n'.join(lines) + '\n'))
    for _ in range(1000):
        n = rnd.randint(1, 8)
        edges = []
        for u in range(1, n + 1):
            for v in range(u + 1, n + 1):
                if rnd.random() < 0.35:
                    edges.append((u, v))
        if not edges and n > 1:
            edges = [(1, 2)]
        lines = [f"{n} {len(edges)}"]
        lines.extend(f"{u} {v}" for u, v in edges)
        cases.append(("T07", '\n'.join(lines) + '\n'))
    for _ in range(1000):
        n = rnd.randint(1, 8)
        edges = []
        for u in range(1, n + 1):
            for v in range(u + 1, n + 1):
                if rnd.random() < 0.35:
                    edges.append((u, v))
        if not edges and n > 1:
            edges = [(1, 2)]
        lines = [f"{n} {len(edges)}"]
        lines.extend(f"{u} {v}" for u, v in edges)
        cases.append(("T08", '\n'.join(lines) + '\n'))
    return cases


def main():
    total = 0
    task_counts = {}
    for task_id, case_in in random_cases():
        task_counts[task_id] = task_counts.get(task_id, 0) + 1
        expected = getattr(TaskOracle, task_id.lower())(case_in)
        check_case(task_id, case_in, expected)
        total += 1
    print(f'validated {total} random differential cases')
    print('task case counts: ' + ', '.join(f'{k}:{v}' for k, v in sorted(task_counts.items())))


if __name__ == '__main__':
    main()
