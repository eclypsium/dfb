from typing import List, Tuple
from you_shall_not_parse.base_classes import Severity

RADON_AMOUNT = 3
ALL_AMOUNT: int = RADON_AMOUNT
ALL_EXAMPLES = ["examples/radon.json"]

RADON_EXPECTED: Tuple[List[Tuple[str, Severity, str, str, str, str]], str] = ([
    ('radon', Severity.MEDIUM, 'parsers/sarif.py', 'SarifHandlerparse_rules', 'B6', 41),
    ('radon', Severity.MEDIUM, 'parsers/sarif.py', 'SarifHandler', 'A5', 11),
    ('radon', Severity.MEDIUM, 'parsers/sarif.py', 'SarifHandlerhandle', 'A5', 12),
], "examples/radon.json")
