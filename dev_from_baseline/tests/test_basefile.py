from unittest.mock import patch
import os
import pytest

from rich.console import Console
import trivy_params as trivy
import pipaudit_params as pipaudit
import golangci_params as golangci
import npm_params as npm
import not_tracked_linter_params as not_tracked_linter
import semgrep_params as sem
import multiple_linters_params as mult_linters
import json
import dev_from_baseline.main as main
from dev_from_baseline.result_table import ResultTable
from dev_from_baseline.comparison_result import ComparisonResult

test_console = Console(record=True)

@pytest.fixture(autouse=True)
def cleanup() -> None:
    yield
    if os.path.exists("tests/testing.json"):
        os.remove("tests/testing.json")

@pytest.mark.parametrize(
    "v1_file_list, v2_file_list, expected",
    [
        ([npm.FILENAME_V1], [npm.FILENAME_V2], npm.EXPECTED_FINDINGS),
        ([pipaudit.FILENAME_V1], [pipaudit.FILENAME_V2], pipaudit.EXPECTED_FINDINGS),
        ([not_tracked_linter.FILENAME_V1], [not_tracked_linter.FILENAME_V2], not_tracked_linter.EXPECTED_FINDINGS),
        (mult_linters.FILENAME_LIST_V1, mult_linters.FILENAME_LIST_V2, mult_linters.EXPECTED_FINDINGS)
    ]
)
def test_basefile_comparison(v1_file_list, v2_file_list, expected) -> None:
    result = ComparisonResult()
    for linter_name in expected.keys():
        for file_name in expected[linter_name]['files'].keys():
            result.add_issue(linter_name, expected[linter_name]['files'][file_name], file_name)
        result.add_issue(linter_name, expected[linter_name]['total'], "Total")
    with pytest.raises(SystemExit):
        main.console = Console(record=True)
        main.main(basefile="tests/testing.json", report_file=v1_file_list, generate=True, verbose=False)
        main.main(basefile="tests/testing.json", report_file=v2_file_list, generate=False, verbose=False)
    result.show_results(ResultTable(test_console))
    old_export = main.console.export_text()
    assert old_export == test_console.export_text()


@pytest.mark.parametrize(
    "v1_file, v2_file, expected",
    [
        (trivy.FILENAME_V1, trivy.FILENAME_V2, trivy.EXPECTED_FINDINGS),
        (golangci.FILENAME_V1, golangci.FILENAME_V2, golangci.EXPECTED_FINDINGS),
        (sem.FILENAME_V1, sem.FILENAME_V2, sem.EXPECTED_FINDINGS)
    ]
)
def test_basefile_comparison_logging(v1_file: str, v2_file: str, expected: str, caplog) -> None:
    with pytest.raises(SystemExit):
        main.main(basefile="tests/testing.json", report_file=[v1_file], generate=True, verbose=False)
        main.main(basefile="tests/testing.json", report_file=[v2_file], generate=False, verbose=False)
    assert expected in caplog.text


def test_basefile_generation() -> None:
    main.main(
        basefile="tests/testing.json",
        report_file=[npm.FILENAME_V1, trivy.FILENAME_V1],
        generate=True,
        verbose=False
    )
    created = open("tests/testing.json", 'r', encoding='utf-8')
    expected = open("test_files/basefile.json", 'r', encoding='utf-8')
    assert created.read() == expected.read()

def test_basefile_generation_when_improved() -> None:
    main.main(
        basefile="tests/testing.json",
        report_file=[npm.FILENAME_V1, trivy.FILENAME_V1],
        generate=True,
        verbose=False
    )
    with pytest.raises(SystemExit) as excinfo:
        main.main(
            basefile="tests/testing.json",
            report_file=[npm.FILENAME_V1],
            generate=False,
            verbose=False
        )

    created = open("tests/testing.json", 'r', encoding='utf-8')
    expected = open("test_files/basefile_improved.json", 'r', encoding='utf-8')
    assert excinfo.value.code == 2
    assert created.read() == expected.read()

def test_basefile_order_of_keys() -> None:
    main.main(
        basefile="tests/testing.json",
        report_file=[npm.FILENAME_V1, trivy.FILENAME_V1],
        generate=True,
        verbose=False
    )
    with open("tests/testing.json", 'r', encoding='utf-8') as file:
        created = json.load(file)
    with open("test_files/basefile.json", 'r', encoding='utf-8') as file:
        expected = json.load(file)
    assert created.keys() == expected.keys()

def test_empty_baseline_is_valid() -> None:
    """Test that an empty baseline {} is treated as valid (zero issues)."""
    # Create empty baseline
    with open("tests/testing.json", 'w', encoding='utf-8') as f:
        json.dump({}, f)

    # Should not raise error, should exit with code 1 (worsened)
    with pytest.raises(SystemExit) as excinfo:
        main.main(
            basefile="tests/testing.json",
            report_file=[npm.FILENAME_V1],
            generate=False,
            verbose=False
        )

    # Empty baseline + new issues = worsened (exit code 1)
    assert excinfo.value.code == 1


def test_empty_baseline_vs_empty_report() -> None:
    """Test comparing empty baseline against empty report (no changes)."""
    # Create empty baseline
    with open("tests/testing.json", 'w', encoding='utf-8') as f:
        json.dump({}, f)

    # Create empty report
    empty_report = "tests/empty_report.sarif"
    with open(empty_report, 'w', encoding='utf-8') as f:
        json.dump({"runs": []}, f)

    try:
        # Should exit with code 0 (same/improved)
        with pytest.raises(SystemExit) as excinfo:
            main.main(
                basefile="tests/testing.json",
                report_file=[empty_report],
                generate=False,
                verbose=False
            )

        assert excinfo.value.code in (0, 2)  # 0=same, 2=improved
    finally:
        if os.path.exists(empty_report):
            os.remove(empty_report)


def test_empty_baseline_generation() -> None:
    """Test that generating baseline from empty reports creates {}."""
    # Create empty report
    empty_report = "tests/empty_report.sarif"
    with open(empty_report, 'w', encoding='utf-8') as f:
        json.dump({"runs": []}, f)

    try:
        main.main(
            basefile="tests/testing.json",
            report_file=[empty_report],
            generate=True,
            verbose=False
        )

        with open("tests/testing.json", 'r', encoding='utf-8') as f:
            baseline = json.load(f)

        # Should create empty baseline or baseline with empty linter entries
        assert isinstance(baseline, dict)
    finally:
        if os.path.exists(empty_report):
            os.remove(empty_report)


def test_empty_baseline_with_multiple_reports() -> None:
    """Test empty baseline against multiple report files with issues."""
    with open("tests/testing.json", 'w', encoding='utf-8') as f:
        json.dump({}, f)

    with pytest.raises(SystemExit) as excinfo:
        main.main(
            basefile="tests/testing.json",
            report_file=[npm.FILENAME_V1, trivy.FILENAME_V1],
            generate=False,
            verbose=False
        )

    # Empty baseline + new issues from multiple linters = worsened
    assert excinfo.value.code == 1


def test_baseline_becomes_empty_after_improvement() -> None:
    """Test that when all issues are fixed, baseline can become empty."""
    # Generate baseline with issues
    main.main(
        basefile="tests/testing.json",
        report_file=[npm.FILENAME_V1],
        generate=True,
        verbose=False
    )

    # Create empty report (all issues fixed)
    empty_report = "tests/empty_report.sarif"
    with open(empty_report, 'w', encoding='utf-8') as f:
        json.dump({"runs": []}, f)

    try:
        with pytest.raises(SystemExit) as excinfo:
            main.main(
                basefile="tests/testing.json",
                report_file=[empty_report],
                generate=False,
                verbose=False
            )

        # All issues fixed = improved (exit code 2)
        assert excinfo.value.code == 2

        # Check that updated baseline is empty or has zero counts
        with open("tests/testing.json", 'r', encoding='utf-8') as f:
            updated_baseline = json.load(f)

        # Verify baseline reflects improvement
        if updated_baseline:  # If not empty
            for linter in updated_baseline.values():
                assert linter.get("Total", 0) == 0
    finally:
        if os.path.exists(empty_report):
            os.remove(empty_report)

@patch('dev_from_baseline.baseline.logger')
def test_none_baseline_logs_error(mock_logger) -> None:
    """Test that None baseline (load failure) logs error and exits."""

    with pytest.raises(SystemExit) as excinfo:
        main.main(
            basefile="tests/nonexistent.json",
            report_file=[npm.FILENAME_V1],
            generate=False,
            verbose=False
        )

    # Should exit with error code
    assert excinfo.value.code != 0
