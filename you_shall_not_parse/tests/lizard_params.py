from typing import List, Tuple
from you_shall_not_parse.base_classes import Severity

lizard_AMOUNT: int = 2
ALL_AMOUNT: int = lizard_AMOUNT

ALL_EXAMPLES = ["examples/complexity.csv"]

LIZARD_EXPECTED = (
    [
        ("lizard", Severity.HIGH, 'tests/test_complexity_functions.py', 'high-complexity', "Function 'complexity_7_function' has high cyclomatic complexity: 7", "6"),
        ("lizard", Severity.HIGH,  'tests/test_complexity_functions.py', 'high-complexity', "Function 'complexity_5_function' has high cyclomatic complexity: 5", "35"),
    ],
    'examples/complexity.csv',
)

