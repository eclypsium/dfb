import pytest
from typing import Any
from you_shall_not_parse.parser import Parser
from you_shall_not_parse.observer import Observer
from you_shall_not_parse.base_classes import IssueTupleType

from tests.sarif_params import TRIVY_EXPECTED
from tests.golangci_params import GOLANGCI_EXPECTED
from tests.npm_params import NPM_EXPECTED
from tests.pipaudit_params import PIPAUDIT_EXPECTED, PIPAUDIT_ABRAM_EXPECTED
from tests.radon_params import RADON_EXPECTED
from tests.poetryaudit_params import POETRYAUDIT_EXPECTED
from tests.pylint_params import PYLINT_EXPECTED, PYLINT_ABRAM_EXPECTED
from tests.mypy_params import MYPY_EXPECTED, MYPY_EXPECTED_2
from tests.lizard_params import LIZARD_EXPECTED


class ExpectedObserver(Observer):
    index = 0

    def __init__(self, expected) -> None:
        self.expected = expected

    def add_issue(self, linter_name: str, issue: IssueTupleType) -> None:
        assert self.expected[self.index] == (linter_name, *issue)
        self.index += 1

@pytest.mark.parametrize(
    "expected",
    [
        (TRIVY_EXPECTED),
        (GOLANGCI_EXPECTED),
        (NPM_EXPECTED),
        (PIPAUDIT_EXPECTED),
        (PIPAUDIT_ABRAM_EXPECTED),
        (RADON_EXPECTED),
        (POETRYAUDIT_EXPECTED),
        (PYLINT_EXPECTED),
        (PYLINT_ABRAM_EXPECTED),
        (MYPY_EXPECTED),
        (MYPY_EXPECTED_2),
        (LIZARD_EXPECTED)
    ]
)
def test_parser(expected) -> None:
    parser = Parser()
    observer = ExpectedObserver(expected[0])
    parser.parse_from_filenames([expected[1]], observer)
