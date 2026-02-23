"""
Module: dev_from_baseline.baseline

This module defines the Baseline class, which handles the baseline operations
like reading, saving, generating, and comparing baselines.
"""
import sys
from logging import getLogger
import json
from typing import Optional

from dev_from_baseline.counter import Counter
from dev_from_baseline.comparison_result import ComparisonResult
from dev_from_baseline.comparison import Comparison
from dev_from_baseline.database_manager import DatabaseManager
from dev_from_baseline.common import BaselineType, ERROR_CODE

logger = getLogger("dev-from-baseline")

class Baseline():
    """
    Class representing a baseline for code analysis.

    Attributes:
        filename (str): The file name of the baseline.
        json (Optional[BaselineType]): The baseline data in JSON format.
    """
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.json: Optional[BaselineType]

    def read_baseline(self) -> None:
        try:
            with open(self.filename, encoding="utf-8") as file:
                self.json = json.load(file)
        except FileNotFoundError:
            logger.error("File %s not found", self.filename)
            sys.exit(ERROR_CODE)

    def save_baseline(self) -> None:
        """Makes consistent the changes"""
        with open(self.filename, 'w', encoding="utf-8") as file:
            json.dump(self.json, file, default=lambda obj: obj.counter.asdict(),
                       indent="  ", sort_keys=True)
            file.write('\n')
        logger.info("Successfly stored basefile in %s", self.filename)

    def generate_baseline_from_db(self, db_manager: DatabaseManager) -> None:
        """Giving a database of issues, it will generate the basefile"""
        result: BaselineType = {}

        for linter_name in db_manager.iter_linters_names():
            linter_counter = Counter()
            result_files = {}
            for file_name in db_manager.iter_files_names(linter_name):
                file_counter = db_manager.get_issues_counter_per_file(linter_name, file_name)
                result_files[file_name] = file_counter.asdict()
                linter_counter.add_counters([file_counter])
            result[linter_name] = {
                "total": linter_counter.asdict(),
                "files": result_files
            }
        self.json = result

    def compare_against_db(self, db_manager: DatabaseManager) -> ComparisonResult:
        """Compare if there are more findings or not"""
        if self.json is None:
            self.read_baseline()
        if self.json is not None:
            old_linters = list(self.json.keys())
            comparison = Comparison()
            comparison_result: ComparisonResult = comparison.compare_all_linters(self.json, old_linters, db_manager)
        else:
            logger.error("Failed loading baseline file")
            sys.exit(ERROR_CODE)
        return comparison_result
