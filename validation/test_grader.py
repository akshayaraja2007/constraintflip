
#!/usr/bin/env python3

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"
VALIDATION_DIR = ROOT / "validation"

# Ensure imports work whether this script is run directly
# from validation or through the main project directory.
sys.path.insert(0, str(ROOT))


def compile_cpp(src: Path, out: Path):
    return subprocess.run(
        ["g++", "-std=c++17", "-O2", str(src), "-o", str(out)],
        capture_output=True,
        text=True,
        timeout=15,
    )


def run_program(exe: Path, inp: str, timeout: float = 5.0):
    return subprocess.run(
        [str(exe)],
        input=inp,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def get_task_dir(task_id: str):
    task_dir = next(
        (
            p for p in TASKS_DIR.iterdir()
            if p.is_dir() and p.name.startswith(f"{task_id}_")
        ),
        None,
    )

    assert task_dir is not None, f"Missing task directory for {task_id}"
    return task_dir


# ============================================================
# REFERENCE SOLUTION VALIDATION
# ============================================================

def test_ref_solution(task_id: str):
    from graders.correctness import check_task_output

    src = ROOT / "reference" / f"{task_id}.cpp"
    exe = ROOT / "reference" / f"{task_id}.exe"

    cp = compile_cpp(src, exe)

    assert cp.returncode == 0, (
        f"Compilation failed for {task_id}:\n{cp.stderr}"
    )

    task_dir = get_task_dir(task_id)
    tests = sorted((task_dir / "tests").glob("*.in"))

    assert tests, f"No test fixtures found for {task_id}"

    passed = 0

    for test_file in tests:
        inp = test_file.read_text(encoding="utf-8")
        expected_file = test_file.with_suffix(".out")

        assert expected_file.exists(), (
            f"Missing expected output: {expected_file}"
        )

        expected = expected_file.read_text(encoding="utf-8")

        out = run_program(exe, inp)

        assert out.returncode == 0, (
            f"Runtime failure for {task_id} on {test_file.name}:\n"
            f"{out.stderr}"
        )

        result = check_task_output(
            task_id,
            inp,
            expected,
            out.stdout,
        )

        if not result["correct"]:
            raise AssertionError(
                f"{task_id} reference mismatch: {test_file.name}\n"
                f"Expected: {expected!r}\n"
                f"Actual:   {out.stdout!r}\n"
                f"Validator: {result['validator_used']}"
            )

        passed += 1

    print(f"{task_id}: {passed} reference fixtures passed")


# ============================================================
# ALTERNATIVE VALID SOLUTION TEST
# ============================================================

def test_alt_valid_solution(
    task_id: str,
    source: str,
    inp: str,
    expected: str,
):
    temp_src = VALIDATION_DIR / f"alt_valid_{task_id}.cpp"
    temp_exe = VALIDATION_DIR / f"alt_valid_{task_id}.exe"

    temp_src.write_text(source, encoding="utf-8")

    cp = compile_cpp(temp_src, temp_exe)

    assert cp.returncode == 0, (
        f"Alternative solution compilation failed for {task_id}:\n"
        f"{cp.stderr}"
    )

    out = run_program(temp_exe, inp)

    assert out.returncode == 0, (
        f"Alternative solution runtime failed for {task_id}:\n"
        f"{out.stderr}"
    )

    assert " ".join(out.stdout.split()) == " ".join(expected.split()), (
        f"Alternative solution output mismatch for {task_id}\n"
        f"Expected: {expected!r}\n"
        f"Actual:   {out.stdout!r}"
    )

    print(f"PASS: Alternative valid solution {task_id}")


# ============================================================
# GRADER REJECTION TESTS: T01-T08
# ============================================================

def test_grader_rejects_wrong_outputs():
    from graders.correctness import check_task_output

    cases = [
        (
            "T01",
            "3 3\n1 2 3\n",
            "2\n",
            "0\n",
        ),
        (
            "T02",
            "3 0\n1 -1 0\n",
            "3\n",
            "2\n",
        ),
        (
            "T03",
            "3 2\n1 2 3\n1 3\n2 2\n",
            "6\n2\n",
            "6\n3\n",
        ),
        (
            "T04",
            "3 3\n1 2 3\nQ 1 3\nU 2 5\nQ 1 3\n",
            "6\n9\n",
            "6\n6\n",
        ),
        (
            "T05",
            "4 2 1\n1 2 2\n2 3 2\n",
            "0\n2\n4\n-1\n",
            "0\n2\n3\n-1\n",
        ),
        (
            "T06",
            "3 2 1\n1 2 2\n2 3 -3\n",
            "0\n2\n-1\n",
            "0\n2\n2\n",
        ),
        (
            "T07",
            "4 4\n1 2\n1 3\n2 4\n3 4\n",
            "1 2 3 4\n",
            "2 1 3 4\n",
        ),
        (
            "T08",
            "4 4\n1 2\n1 3\n2 4\n3 4\n",
            "1 2 3 4\n",
            "1 3 2 4\n",
        ),
    ]

    print("\nGRADER REJECTION TESTS")

    for task_id, inp, expected, wrong in cases:
        result = check_task_output(
            task_id,
            inp,
            expected,
            wrong,
        )

        assert not result["correct"], (
            f"{task_id} grader incorrectly accepted wrong output!\n"
            f"Output: {wrong!r}"
        )

        print(f"PASS: {task_id} rejected incorrect output")


# ============================================================
# COMPILATION FAILURE TEST
# ============================================================

def test_compile_failure():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        bad = temp_path / "bad_compile.cpp"
        exe = temp_path / "bad_compile.exe"

        bad.write_text(
            "int main() { return ; }\n",
            encoding="utf-8",
        )

        cp = compile_cpp(bad, exe)

        assert cp.returncode != 0, (
            "Compilation failure test unexpectedly succeeded"
        )

    print("PASS: Compilation failure detection")


# ============================================================
# RUNTIME ERROR TEST
# ============================================================

def test_runtime_error():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source = temp_path / "runtime_error.cpp"
        exe = temp_path / "runtime_error.exe"

        source.write_text(
            """
#include <cstdlib>

int main() {
    std::abort();
    return 0;
}
""",
            encoding="utf-8",
        )

        cp = compile_cpp(source, exe)

        assert cp.returncode == 0, (
            "Runtime error test program failed to compile:\n"
            + cp.stderr
        )

        try:
            out = run_program(exe, "", timeout=5.0)

        except subprocess.TimeoutExpired:
            raise AssertionError(
                "Runtime error test unexpectedly timed out"
            )

        assert out.returncode != 0, (
            "Runtime error test unexpectedly returned 0"
        )

    print("PASS: Runtime error detection")


# ============================================================
# TIMEOUT TEST
# ============================================================

def test_timeout():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source = temp_path / "timeout.cpp"
        exe = temp_path / "timeout.exe"

        source.write_text(
            """
int main() {
    while (true) {}
}
""",
            encoding="utf-8",
        )

        cp = compile_cpp(source, exe)

        assert cp.returncode == 0, (
            "Timeout test program failed to compile:\n"
            + cp.stderr
        )

        try:
            run_program(exe, "", timeout=1.0)

        except subprocess.TimeoutExpired:
            print("PASS: Timeout detection")
            return

    raise AssertionError(
        "Timeout test unexpectedly completed without timeout"
    )


# ============================================================
# T06 SENTINEL SAFETY
# ============================================================

def test_t06_sentinel_safety():
    inp = (
        "5 3 1\n"
        "1 2 1\n"
        "1 3 -2\n"
        "3 4 0\n"
    )

    # Vertex 4 is reachable through 1 -> 3 -> 4.
    expected = (
        "0\n"
        "1\n"
        "-2\n"
        "-2\n"
        "UNREACHABLE\n"
    )

    ref = ROOT / "reference" / "T06.exe"

    if not ref.exists():
        cp = compile_cpp(ROOT / "reference" / "T06.cpp", ref)
        assert cp.returncode == 0, cp.stderr

    out = run_program(ref, inp)

    assert out.returncode == 0, out.stderr

    assert " ".join(out.stdout.split()) == " ".join(expected.split()), (
        f"T06 sentinel safety failed:\n"
        f"Expected: {expected!r}\n"
        f"Actual: {out.stdout!r}"
    )

    print("PASS: T06 sentinel safety")


# ============================================================
# T07 SEMANTIC VALIDATION
# ============================================================

def test_t07_grader():
    from graders.correctness import validate_topological_order

    inp = (
        "4 4\n"
        "1 2\n"
        "1 3\n"
        "2 4\n"
        "3 4\n"
    )

    valid_orders = [
        "1 2 3 4\n",
        "1 3 2 4\n",
    ]

    invalid_orders = [
        "2 1 3 4\n",
        "4 3 2 1\n",
        "4 1 2 3\n",
        "1 2 2 4\n",
        "1 2 3\n",
        "1 2 3 4 4\n",
    ]

    for order in valid_orders:
        assert validate_topological_order("T07", inp, order), (
            f"T07 rejected valid ordering: {order!r}"
        )

    for order in invalid_orders:
        assert not validate_topological_order("T07", inp, order), (
            f"T07 accepted invalid ordering: {order!r}"
        )

    cyclic_input = (
        "3 3\n"
        "1 2\n"
        "2 3\n"
        "3 1\n"
    )

    assert validate_topological_order(
        "T07",
        cyclic_input,
        "IMPOSSIBLE",
    )

    print("PASS: T07 semantic validation")


# ============================================================
# T08 LEXICOGRAPHIC VALIDATION
# ============================================================

def test_t08_grader():
    from graders.correctness import (
        validate_lexicographic_topological_order,
    )

    inp = (
        "4 4\n"
        "1 2\n"
        "1 3\n"
        "2 4\n"
        "3 4\n"
    )

    correct = "1 2 3 4\n"
    wrong = "1 3 2 4\n"

    assert validate_lexicographic_topological_order(
        "T08",
        inp,
        correct,
    )

    assert not validate_lexicographic_topological_order(
        "T08",
        inp,
        wrong,
    )

    cyclic_input = (
        "3 3\n"
        "1 2\n"
        "2 3\n"
        "3 1\n"
    )

    assert validate_lexicographic_topological_order(
        "T08",
        cyclic_input,
        "IMPOSSIBLE",
    )

    print("PASS: T08 lexicographic validation")


# ============================================================
# ALTERNATIVE VALID SOLUTION: T01
# ============================================================

def test_t01_alt_valid_solution():
    source = r'''
#include <bits/stdc++.h>
using namespace std;

long long atMost(const vector<long long>& a, long long k) {
    if (k < 0) return 0;

    long long left = 0, sum = 0, ans = 0;

    for (long long right = 0; right < (long long)a.size(); ++right) {
        sum += a[right];

        while (left <= right && sum > k) {
            sum -= a[left++];
        }

        ans += right - left + 1;
    }

    return ans;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long n, k;
    cin >> n >> k;

    vector<long long> a(n);

    for (auto& x : a) cin >> x;

    cout << atMost(a, k) - atMost(a, k - 1) << '\n';
}
'''

    inp = "6 5\n1 2 3 4 5 1\n"
    expected = "2\n"

    test_alt_valid_solution("T01", source, inp, expected)


# ============================================================
# ALTERNATIVE VALID SOLUTION: T03
# ============================================================

def test_t03_alt_valid_solution():
    source = r'''
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;

    vector<long long> pref(n + 1, 0);

    for (int i = 1; i <= n; ++i) {
        long long x;
        cin >> x;
        pref[i] = pref[i - 1] + x;
    }

    while (q--) {
        int l, r;
        cin >> l >> r;
        cout << pref[r] - pref[l - 1] << '\n';
    }
}
'''

    inp = (
        "5 3\n"
        "1 2 3 4 5\n"
        "1 3\n"
        "2 5\n"
        "3 3\n"
    )

    expected = "6\n14\n3\n"

    test_alt_valid_solution("T03", source, inp, expected)


# ============================================================
# ALTERNATIVE VALID SOLUTION: T05
# ============================================================

def test_t05_alt_valid_solution():
    source = r'''
#include <bits/stdc++.h>
using namespace std;

struct Edge {
    int to;
    long long weight;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m, src;
    cin >> n >> m >> src;

    vector<vector<Edge>> graph(n + 1);

    for (int i = 0; i < m; ++i) {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        graph[u].push_back({v, w});
    }

    const long long INF = 4e18;

    vector<long long> dist(n + 1, INF);

    priority_queue<
        pair<long long, int>,
        vector<pair<long long, int>>,
        greater<pair<long long, int>>
    > pq;

    dist[src] = 0;
    pq.push({0, src});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (d != dist[u]) continue;

        for (const auto& e : graph[u]) {
            if (dist[e.to] > d + e.weight) {
                dist[e.to] = d + e.weight;
                pq.push({dist[e.to], e.to});
            }
        }
    }

    for (int i = 1; i <= n; ++i) {
        if (dist[i] == INF) cout << -1 << '\n';
        else cout << dist[i] << '\n';
    }
}
'''

    inp = (
        "4 5 1\n"
        "1 2 2\n"
        "1 3 5\n"
        "2 3 1\n"
        "2 4 3\n"
        "3 4 1\n"
    )

    expected = "0\n2\n3\n4\n"

    test_alt_valid_solution("T05", source, inp, expected)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("CONSTRAINTFLIP GRADER VALIDATION")
    print("=" * 60)

    print("\n1. REFERENCE SOLUTIONS")

    for task_id in [
        "T01", "T02", "T03", "T04",
        "T05", "T06", "T07", "T08",
    ]:
        test_ref_solution(task_id)

    print("\n2. ALTERNATIVE VALID SOLUTIONS")

    test_t01_alt_valid_solution()
    test_t03_alt_valid_solution()
    test_t05_alt_valid_solution()

    print("\n3. WRONG OUTPUT REJECTION")

    test_grader_rejects_wrong_outputs()

    print("\n4. SPECIAL VALIDATOR TESTS")

    test_t06_sentinel_safety()
    test_t07_grader()
    test_t08_grader()

    print("\n5. EXECUTION FAILURE TESTS")

    test_compile_failure()
    test_runtime_error()
    test_timeout()

    print("\n" + "=" * 60)
    print("ALL GRADER VALIDATION CHECKS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
