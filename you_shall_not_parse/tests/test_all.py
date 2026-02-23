import json
import pytest
from you_shall_not_parse.parser import Parser
from you_shall_not_parse.observers.database_observer import DBObserver
from you_shall_not_parse.observers.sarif_observer import SarifObserver
import tests.sarif_params as sarif
import tests.pipaudit_params as pipaudit
import tests.golangci_params as golangci
import tests.npm_params as npm
import tests.radon_params as radon
import tests.poetryaudit_params as poetryaudit
from typing import List, Tuple

LINTERS_DATA: List[Tuple[str, int, List[str]]] = [
    ("Bandit", sarif.BANDIT_AMOUNT, [sarif.ALL_EXAMPLES[0]]),
    ("gitleaks", sarif.GITLEAKS_AMOUNT, [sarif.ALL_EXAMPLES[1]]),
    ("ESLint", sarif.ESLINT_AMOUNT, [sarif.ALL_EXAMPLES[2]]),
    ("semgrep", sarif.SEMGREP_AMOUNT, [sarif.ALL_EXAMPLES[3]]),
    ("Trivy", sarif.TRIVY_AMOUNT, [sarif.ALL_EXAMPLES[4]]),
    ("pip-audit", pipaudit.ALL_AMOUNT, pipaudit.ALL_EXAMPLES),
    ("golangci", golangci.ALL_AMOUNT, golangci.ALL_EXAMPLES),
    ("npm", npm.ALL_AMOUNT, npm.ALL_EXAMPLES),
    ("radon", radon.ALL_AMOUNT, radon.ALL_EXAMPLES),
    ("poetry-audit", poetryaudit.ALL_AMOUNT, poetryaudit.ALL_EXAMPLES),
]
ALL_AMOUNT: int = sum(i for _, i, _ in LINTERS_DATA)
LINTERS_AMOUNT: int = len(LINTERS_DATA)
ALL_EXAMPLES: list[str] = [file for (_, _, files) in LINTERS_DATA for file in files]

@pytest.fixture
def parser() -> Parser:
    return Parser()

@pytest.mark.parametrize(
    "parser, all_examples, all_amount, linters_amount",
    [
        (Parser(), sarif.ALL_EXAMPLES, sarif.ALL_AMOUNT, sarif.LINTERS_AMOUNT),
        (Parser(), pipaudit.ALL_EXAMPLES, pipaudit.ALL_AMOUNT, 1),
        (Parser(), golangci.ALL_EXAMPLES, golangci.ALL_AMOUNT, 1),
        (Parser(), npm.ALL_EXAMPLES, npm.ALL_AMOUNT, 1),
        (Parser(), radon.ALL_EXAMPLES, radon.ALL_AMOUNT, 1),
        (Parser(), poetryaudit.ALL_EXAMPLES, poetryaudit.ALL_AMOUNT, 1),
        (Parser(), ALL_EXAMPLES, ALL_AMOUNT, LINTERS_AMOUNT)
    ]
)
# pylint:disable=redefined-outer-name
def test_all_examples_with_user_files(parser,
                                      all_examples,
                                      all_amount,
                                      linters_amount) -> None:
    observer = DBObserver()
    for file_name in all_examples:
        parser.parse_from_filenames([file_name], observer)
    database = observer.get_database()
    assert len(database.query("SELECT * FROM issues")) == all_amount
    assert len(database.query("SELECT DISTINCT linter_name FROM issues")) == linters_amount

@pytest.mark.parametrize(
    "parser, all_examples, all_amount, linters_amount",
    [
        (Parser(), sarif.ALL_EXAMPLES, sarif.ALL_AMOUNT, sarif.LINTERS_AMOUNT),
        (Parser(), pipaudit.ALL_EXAMPLES, pipaudit.ALL_AMOUNT, 1),
        (Parser(), golangci.ALL_EXAMPLES, golangci.ALL_AMOUNT, 1),
        (Parser(), npm.ALL_EXAMPLES, npm.ALL_AMOUNT, 1),
        (Parser(), radon.ALL_EXAMPLES, radon.ALL_AMOUNT, 1),
        (Parser(), poetryaudit.ALL_EXAMPLES, poetryaudit.ALL_AMOUNT, 1),
        (Parser(), ALL_EXAMPLES, ALL_AMOUNT, LINTERS_AMOUNT)
    ]
)
# pylint:disable=redefined-outer-name
def test_all_examples_with_str(parser,
                                      all_examples,
                                      all_amount,
                                      linters_amount) -> None:
    observer = DBObserver()
    for file_name in all_examples:
        with open(file_name, 'r', encoding='utf-8') as fd:
            to_parse = fd.read()
            parser.parse_from_str(to_parse, observer)
    database = observer.get_database()
    assert len(database.query("SELECT * FROM issues")) == all_amount
    assert len(database.query("SELECT DISTINCT linter_name FROM issues")) == linters_amount


@pytest.mark.parametrize(
    "parser, all_examples, all_amount, linters_amount",
    [
        (Parser(), sarif.ALL_EXAMPLES, sarif.ALL_AMOUNT, sarif.LINTERS_AMOUNT),
        (Parser(), pipaudit.ALL_EXAMPLES, pipaudit.ALL_AMOUNT, 1),
        (Parser(), golangci.ALL_EXAMPLES, golangci.ALL_AMOUNT, 1),
        (Parser(), npm.ALL_EXAMPLES, npm.ALL_AMOUNT, 1),
        (Parser(), radon.ALL_EXAMPLES, radon.ALL_AMOUNT, 1),
        (Parser(), poetryaudit.ALL_EXAMPLES, poetryaudit.ALL_AMOUNT, 1),
        (Parser(), ALL_EXAMPLES, ALL_AMOUNT, LINTERS_AMOUNT)
    ]
)
# pylint:disable=redefined-outer-name
def test_passing_lists(parser,
                       all_examples,
                       all_amount,
                       linters_amount) -> None:
    observer = DBObserver()
    parser.parse_from_filenames(all_examples, observer)
    database = observer.get_database()
    expected_issues = all_amount
    assert len(database.query("SELECT * FROM issues")) == expected_issues
    assert len(database.query("SELECT DISTINCT linter_name FROM issues")) == linters_amount


def test_sarif_observer(parser) -> None:
    observer = SarifObserver()
    parser.parse_from_filenames(["examples/trivy.sarif"], observer)
    expected = json.loads(open("tests/trivy_expected.sarif", 'r', encoding='utf-8').read())
    assert expected == observer.get_sarif_json()
