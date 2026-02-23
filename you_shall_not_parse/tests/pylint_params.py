from typing import List, Tuple
from you_shall_not_parse.base_classes import Severity

PYLINT_AMOUNT: int = 3
ALL_AMOUNT: int = PYLINT_AMOUNT
ALL_EXAMPLES = ["examples/pylint.json"]

PYLINT_EXPECTED = (
    [
        ("pylint", Severity.HIGH, "abram/abram_engine.py", "import-error", "Unable to import 'abram_preprocessor.main'", "21"),
        ("pylint", Severity.HIGH, "abram/abram_engine.py", "import-error", "Unable to import 'cdt_lib_engine.evaluator'", "22"),
        ("pylint", Severity.LOW, "abram/abram_engine.py", "too-few-public-methods", "Too few public methods (1/2)", "68"),
    ],
    "examples/pylint.json"
)

PYLINT_ABRAM_EXPECTED = (

    [
        ("pylint", Severity.LOW, "abram/abram_base_types.py", "missing-module-docstring", "Missing module docstring", "1"),
        ("pylint", Severity.LOW, "abram/abram_collection.py", "missing-module-docstring", "Missing module docstring", "1"),
        ("pylint", Severity.LOW, "abram/abram_collection.py", "missing-function-docstring", "Missing function or method docstring", "24"),
        ("pylint", Severity.MEDIUM, "abram/abram_collection.py", "protected-access", "Access to a protected member _iterate_collection of a client class", "26"),
    ],
    "examples/pylint-abram.json"
)
