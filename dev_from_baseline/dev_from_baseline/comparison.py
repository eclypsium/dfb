"""
Module: dev_from_baseline.comparison

This module defines the Comparison class, which handles the comparison
operations between the baseline and a new report.
"""

from logging import getLogger
from dev_from_baseline.common import BaselineType
from dev_from_baseline.counter import Counter, CounterComparison
from dev_from_baseline.comparison_result import ComparisonResult
from dev_from_baseline.linter_comparison import LinterComparison, LinterComparisonData
from dev_from_baseline.database_manager import DatabaseManager

logger = getLogger("dev-from-baseline")

# pylint: disable=too-few-public-methods
class Comparison():
    """
    Class representing a comparison between the baseline and a new report.

    Attributes:
        comparison_result (ComparisonResult): An instance of ComparisonResult for storing comparison results.
        db_manager (DatabaseManager): The DatabaseManager instance containing issue data.
    """

    def compare_all_linters(self,
                            basefile: BaselineType,
                            old_linters: list[str],
                            db_manager: DatabaseManager
                            ) -> ComparisonResult:
        """
        Compare the baseline against a new report for all linters and update result.

        Args:
            basefile (BaselineType): The baseline data in dictionary format.
            old_linters (list[str]): List of linter names in original basefile.
        """
        comparison_result = ComparisonResult()
        for linter_name in db_manager.iter_linters_names():
            if linter_name in old_linters:
                old_linters.remove(linter_name)
                old_files = list(basefile[linter_name]["files"].keys())
            else:
                old_files = []
            comparison_params = LinterComparisonData(basefile, linter_name, old_files)
            linter_comparison = LinterComparison(db_manager, comparison_result, comparison_params)
            linter_comparison.compare_files_inside_linter()
            self._check_linter(comparison_params, comparison_result, db_manager)

        if old_linters != []:
            comparison_result.update_result_improved()

        return comparison_result

    def _check_linter(self,
                     compare_params: LinterComparisonData,
                     comparison_result: ComparisonResult,
                     db_manager: DatabaseManager
                     ) -> None:
        """
        Check the linter for any remaining files and compare total findings.
        Args:
            compare_params (LinterComparisonData): Comparison parameters for the linter.
        """
        old_counter = Counter()
        if compare_params.linter_name in compare_params.basefile.keys():
            old_counter.from_dict(compare_params.basefile[compare_params.linter_name]["total"])
        linter_counter = db_manager.get_issues_counter_per_linter(compare_params.linter_name)
        if comparison_result.is_worse_than_basefile(compare_params.linter_name):
            details = db_manager.get_issues_details(compare_params.linter_name)
            counter_comparison = CounterComparison(old_counter, linter_counter, details=details)
            comparison_result.add_issue(compare_params.linter_name, counter_comparison, "Total")
        elif compare_params.old_files != []:
            comparison_result.update_result_improved()
