
from graders.correctness import (
    validate_topological_order,
    validate_lexicographic_topological_order,
)

# T07: Any valid topological ordering.
T07_INPUT = """4 4
1 2
1 3
2 4
3 4
"""

t07_tests = [
    ("1 2 3 4", True),
    ("1 3 2 4", True),
    ("2 1 3 4", False),
    ("4 3 2 1", False),
    ("4 1 2 3", False),
    ("1 2 3", False),
    ("1 2 3 4 4", False),
    ("1 2 2 4", False),
    ("1 2 3 X", False),
    ("IMPOSSIBLE", False),
]

print("T07 VALIDATION")

for output, expected in t07_tests:
    actual = validate_topological_order("T07", T07_INPUT, output)
    status = "PASS" if actual == expected else "FAIL"
    print(f"{status}: {output!r} -> {actual}, expected {expected}")


# T08: Lexicographically smallest topological ordering.
T08_INPUT = """5 4
1 3
2 3
3 5
4 5
"""

t08_tests = [
    ("1 2 3 4 5", True),
    ("1 2 4 3 5", False),
    ("1 2 3 5 4", False),
    ("1 2 3 4 5\n", True),
    ("IMPOSSIBLE", False),
]

print("\nT08 VALIDATION")

for output, expected in t08_tests:
    actual = validate_lexicographic_topological_order(
        "T08",
        T08_INPUT,
        output,
    )
    status = "PASS" if actual == expected else "FAIL"
    print(f"{status}: {output!r} -> {actual}, expected {expected}")


# Cyclic graph: IMPOSSIBLE must be accepted.
CYCLIC_INPUT = """3 3
1 2
2 3
3 1
"""

print("\nCYCLE VALIDATION")

print(
    "T07:",
    validate_topological_order("T07", CYCLIC_INPUT, "IMPOSSIBLE"),
)

print(
    "T08:",
    validate_lexicographic_topological_order(
        "T08",
        CYCLIC_INPUT,
        "IMPOSSIBLE",
    ),
)
