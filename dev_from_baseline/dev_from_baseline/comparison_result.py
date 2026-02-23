"""
Module: dev_from_baseline.comparison_result

This module defines the class ComparisonResult
that stores the results of differences in counts.
"""

from dataclasses import dataclass, field
from enum import Enum
from logging import getLogger
from typing import Dict, List, Optional
from dev_from_baseline.counter import CounterComparison
from dev_from_baseline.common import ResultType, FileComparison, LinterName
from dev_from_baseline.results_printer import ResultsPrinter

logger = getLogger("dev-from-baseline")

Issue = Dict
DetailedInfo = list[Issue]

class ResultCode(Enum):
    """Code to return when exit"""
    SAME = 0
    WORSE = 1
    IMPROVED = 2

@dataclass
class IssueDetail:
    severity: str
    file_name: str
    location: Optional[str] = None

@dataclass
class LinterResults:
    linter_name: str
    file_name: str
    issues: List[IssueDetail] = field(default_factory=list)

class ComparisonResult():
    """
    Class for storing comparison results.

    Attributes:
        linters (ResultType): A dictionary to store comparison results for each linter.
        status_code (ResultCode): The result of the baseline comparison.
    """
    def __init__(self) -> None:
        self.linters: ResultType = {}
        self.status_code = ResultCode.SAME

    def is_worse_than_basefile(self, linter_name: LinterName) -> bool:
        """
        Determines whether the code is worse than the basefile regarding a specific linter.

        A code is considered worse than the basefile with respect to a linter if,
        for the given 'linter_name', there is at least one file that has added an issue.
        """
        return linter_name in self.linters

    def is_better_than_basefile(self) -> bool:
        return self.status_code == ResultCode.IMPROVED

    def update_result_improved(self) -> None:
        if self.status_code != ResultCode.WORSE:
            self.status_code = ResultCode.IMPROVED

    def add_issue(self, linter_name: str, comparison: CounterComparison, file_name: str, detailed_info: Optional[DetailedInfo] = None) -> None:
        if linter_name not in self.linters:
            self.linters[linter_name] = []
        if detailed_info:
            comparison.details = detailed_info
        self.linters[linter_name].append(FileComparison(file_name, comparison))
        self.status_code = ResultCode.WORSE

    def show_results(self, printer: ResultsPrinter) -> None:
        for linter_name, file_comparison_list in self.linters.items():
            printer.print_linter_results(linter_name, file_comparison_list)

        if self.status_code == ResultCode.IMPROVED:
            logger.error("The baseline has been improved. Please update the basefile.")

    def get_worsened_issues(self) -> Dict[str, List[IssueDetail]]:
        def initialize_worsened_issues():
            return {'Total': {linter_name: [] for linter_name in self.linters}}

        def process_comparison(file_comparison, linter_name: str, worsened_issues: Dict):
            detailed_comparison = file_comparison.comparison.to_dict()
            if 'details' not in detailed_comparison:
                return
            file_name = file_comparison.file_name
            if file_name not in worsened_issues:
                worsened_issues[file_name] = {}
            if linter_name not in worsened_issues[file_name]:
                worsened_issues[file_name][linter_name] = []
            if detailed_comparison not in worsened_issues[file_name][linter_name]:
                worsened_issues[file_name][linter_name].append(detailed_comparison)
            if detailed_comparison not in worsened_issues['Total'][linter_name]:
                worsened_issues['Total'][linter_name].append(detailed_comparison)
        worsened_issues = initialize_worsened_issues()

        for linter_name, file_comparisons in self.linters.items():
            for file_comparison in file_comparisons:
                process_comparison(file_comparison, linter_name, worsened_issues)
        return worsened_issues
    