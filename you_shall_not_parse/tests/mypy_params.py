from typing import List, Tuple
from you_shall_not_parse.base_classes import Severity

MYPY_AMOUNT: int = 3
ALL_AMOUNT: int = MYPY_AMOUNT
ALL_EXAMPLES = ["examples/mypy.xml", "examples/empty_mypy.xml"]

MYPY_EXPECTED = (
    [
        ("mypy", Severity.HIGH, 'src/abram/raw_data.py', 'error', 'Function is missing a type annotation  [no-untyped-def]', '24'),
        ("mypy", Severity.HIGH,  'src/abram/raw_data.py', 'error', 'Call to untyped function "input_checks" in typed context  [no-untyped-call]', '31'),
        ("mypy", Severity.HIGH,  'src/abram/raw_data.py', 'error', 'Function is missing a return type annotation  [no-untyped-def]', '68'),
        ("mypy", Severity.NOTE,  'src/abram/raw_data.py', 'note', 'Use "None" if function does not return a value', '68')

    ],
    "examples/mypy.xml"
)

MYPY_EXPECTED_2 = (
    [],
    "examples/empty_mypy.xml"
)
