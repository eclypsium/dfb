#!/usr/bin/env python
"""Script to check if there was more findings in last sast analysis"""
import argparse
import sys
import logging
from rich.console import Console

from you_shall_not_parse.parser import Parser
from you_shall_not_parse.observers.database_observer import DBObserver
from dev_from_baseline.database_manager import DatabaseManager
from dev_from_baseline.baseline import Baseline
from dev_from_baseline.comparison_result import ComparisonResult, ResultCode
from dev_from_baseline.common import ERROR_CODE
from dev_from_baseline.result_table import ResultTable, ResultTableIssues

args_parser = argparse.ArgumentParser()
console = Console()
logging.basicConfig()
logger = logging.getLogger("dev-from-baseline")

def generate_baseline(basefile: str, reports: list[str]) -> None:
    """it creates a basefile file with the results in --report_file."""
    observer = DBObserver()
    Parser().parse_from_filenames(reports, observer)
    db_manager = DatabaseManager(observer.get_database())
    baseline = Baseline(basefile)
    baseline.generate_baseline_from_db(db_manager)
    baseline.save_baseline()


def compare(basefile: str,
            report_files: list[str]) -> tuple[ComparisonResult, dict]:
    """
    It will compare the results already stored in --basefile with the new
    report --report_file
    """
    observer = DBObserver()
    Parser().parse_from_filenames(report_files, observer)
    old_baseline = Baseline(basefile)
    old_baseline.read_baseline()
    db_manager = DatabaseManager(observer.get_database())

    if old_baseline.json is None:
        logger.error("Baseline json failed to load")
        sys.exit(ERROR_CODE)

    comparison_result: ComparisonResult = old_baseline.compare_against_db(db_manager)
    printer = ResultTable(console)
    comparison_result.show_results(printer)
    worsened_severities: dict[str, dict] = extract_worsened_severities(comparison_result)

    return comparison_result, worsened_severities

def extract_worsened_severities(result: ComparisonResult) -> dict:
    worsened_severities: dict[str, dict[str, set[str]]] = {}
    for linter_name, file_comparisons in result.linters.items():
        for file_comparison in file_comparisons:
            if file_comparison.file_name != "Total":
                extract_severity_changes(file_comparison, linter_name, worsened_severities)
    return worsened_severities

def extract_severity_changes(file_comparison, linter_name, worsened_severities):
    old_counts = file_comparison.comparison.old.asdict()
    new_counts = file_comparison.comparison.new.asdict()

    for severity, old_value in old_counts.items():
        new_value = new_counts.get(severity)
        if old_value != new_value:
            worsened_severities.setdefault(severity, {}).setdefault(file_comparison.file_name, set()).add(linter_name)

def display_worsened_issues(result: ComparisonResult, worsened_severities: dict) -> None:
    worsened_issues = result.get_worsened_issues()
    issues_data: list[dict[str, str]] = []

    for file_name, linters in worsened_issues.items():
        process_linters(file_name, linters, worsened_severities, issues_data)

    result_table_issues = ResultTableIssues(console)
    result_table_issues.generate_table(issues_data)

def process_linters(_file_name, linters, worsened_severities, issues_data):
    for _linter_name, issues in linters.items():
        for issue in issues:
            process_issue_details(issue, worsened_severities, issues_data)

def process_issue_details(issue, worsened_severities, issues_data):
    if 'details' not in issue:
        return

    for detail in issue['details']:
        file_name = detail['file']
        severity = detail['severity'].lower()

        if file_name in worsened_severities.get(severity, {}):
            issues_data.append({
                'linter': detail['linter'],
                'file': file_name,
                'severity': detail['severity'],
                'message': detail['message'],
                'location': detail.get('location', 'N/A')
            })

def handle_comparison_result(
        result: ComparisonResult, basefile: str, report_file: list[str],
        worsened_severities: dict, details: bool = False) -> None:
    status_code = result.status_code

    if status_code == ResultCode.SAME:
        logger.info("No change detected: The code quality is consistent with the baseline. No updates needed")

    elif status_code == ResultCode.WORSE:
        logger.info(
            "Code quality has declined: More issues were found than in the baseline."
            "Please address the issues. If that's not possible, "
            "you can update the baseline with the newly generated one.")
        if details:
            display_worsened_issues(result, worsened_severities)
        else:
            logger.info("Use the --details flag to see the details of the issues")
        generate_baseline(basefile, report_file)

    else:
        logger.info("Code quality has improved: Fewer issues detected compared to the baseline."
                    "A new baseline has been generated. Consider updating the baseline to reflect the improvements.")
        generate_baseline(basefile, report_file)

    sys.exit(status_code.value)

def main(basefile: str,
         report_file: list[str],
         generate: bool = False,
         verbose: bool = False,
         details: bool = False) -> None:

    if verbose:
        logger.setLevel(logging.DEBUG)
    if generate:
        generate_baseline(basefile, report_file)
    else:
        result, worsened_severities = compare(basefile, report_file)
        handle_comparison_result(result, basefile, report_file, worsened_severities, details)

def main_cli() -> None:
    args_parser.add_argument("-b",
                             "--basefile",
                             required=True,
                             help="Location of basefile")
    args_parser.add_argument("-r",
                             "--report-file",
                             nargs='+',
                             required=True,
                             help="Linters report file to parse")
    args_parser.add_argument("-g",
                             "--generate",
                             action='store_true',
                             default=False,
                             help="Generate basefile")
    args_parser.add_argument("-v",
                             "--verbose",
                             action='store_true',
                             default=False,
                             help="Verbose")
    args_parser.add_argument("-d",
                             "--details",
                             action='store_true',
                             default=False,
                             help="Details")

    args = args_parser.parse_args()
    main(args.basefile, args.report_file, args.generate, args.verbose, args.details)
