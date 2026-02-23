"""
Module: dev_from_baseline.linter_comparison

This module defines the LinterComparison and LinterComparisonData classes for comparing
issues within a linter.
"""

from dataclasses import dataclass
from dev_from_baseline.counter import Counter, CounterComparison
from dev_from_baseline.comparison_result import ComparisonResult
from dev_from_baseline.common import BaselineType, FilenameType

from dev_from_baseline.database_manager import DatabaseManager

@dataclass
class LinterComparisonData:
    basefile: BaselineType
    linter_name: str
    old_files: list['FilenameType']


class LinterComparison():
    """
    Class representing a comparison of issues within a linter.

    Attributes:
        db_manager (DatabaseManager): The DatabaseManager instance containing issue data.
        result (ComparisonResult): An instance of ComparisonResult for storing comparison results.
        comparison_params (LinterComparisonData): Comparison parameters for the linter.
    """
    def __init__(self,
                 db_manager: DatabaseManager,
                 comparison_result: ComparisonResult,
                 comparison_params: LinterComparisonData) -> None:
        self.comparison_params = comparison_params
        self.comparison_result = comparison_result
        self.db_manager = db_manager

    def compare_files_inside_linter(self) -> None:
        """
        Compare issues within a linter and update the comparison result.
        """
        for file_name in self.db_manager.iter_files_names(self.comparison_params.linter_name):
            file_counter = self.db_manager.get_issues_counter_per_file(self.comparison_params.linter_name, file_name)
            if file_name in self.comparison_params.old_files:
                self.comparison_params.old_files.remove(file_name)
                self.compare_tracked_files(file_counter, file_name)

            else:
                self.compare_untracked_files(file_counter, file_name)

    def compare_tracked_files(self,
                            file_counter: Counter,
                            file_name: FilenameType) -> None:
        """
        Compare issues in tracked files and update the comparison result.

        Args:
            file_counter (Counter): The counter for issues in the file.
            file_name (FilenameType): The name of the file.
        """
        old_file_counter = Counter()
        old_file_counter.from_dict(
            self.comparison_params.basefile[self.comparison_params.linter_name]["files"][file_name]
        )
        if old_file_counter.compare_against_counter(file_counter):
            comparison = CounterComparison(old_file_counter, file_counter)
            self.comparison_result.add_issue(self.comparison_params.linter_name, comparison, file_name)
        elif old_file_counter.compare_against_counter(file_counter, warn_less_issues=True):
            self.comparison_result.update_result_improved()

    def compare_untracked_files(self,
                                file_counter: Counter,
                                file_name: FilenameType) -> None:
        """
        Compare issues in untracked files and update the comparison result.

        Args:
            file_counter (Counter): The counter for issues in the file.
            file_name (FilenameType): The name of the file.
        """
        comparison = CounterComparison(Counter(), file_counter)
        self.comparison_result.add_issue(self.comparison_params.linter_name, comparison, file_name)
