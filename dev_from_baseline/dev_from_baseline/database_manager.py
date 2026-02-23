"""
Module: dev_from_baseline.database_manager

This module defines the DatabaseManager class, which handles querying issues
from a database and generating counters.
"""

from logging import getLogger
from typing import Generator
from typing_extensions import NamedTuple

from you_shall_not_parse.observers.database_observer import Database
from dev_from_baseline.counter import Counter, Severity

class IssuesType(NamedTuple):
    severity: str
    amount: int

ListOfIssues = list['IssuesType']

logger = getLogger("dev-from-baseline")

class DatabaseManager():
    """
    A class to manage querying issues from a database and generating counters.

    Attributes:
        database (Database): The database instance to query.
    """

    def __init__(self, database: Database) -> None:
        self.database = database

    def get_issues_counter_per_file(self, linter_name: str, file_name: str) -> Counter:
        """
        Get the counter for issues per file (for a specific linter).

        Args:
            linter_name (str): The name of the linter.
            file_name (str): The name of the file.

        Returns:
            Counter: The counter for issues per file.
        """
        issues: ListOfIssues = self.database.query(
            'SELECT\n    severity,\n    COUNT(*) AS amount\n' +
            'FROM issues\n' +
            'WHERE linter_name = :linter_name AND file_path = :file_name GROUP BY severity',
            {'linter_name': linter_name, 'file_name': file_name}
        )
        file_counter: Counter = Counter()
        self._add_findings_to_counter(file_counter, issues)
        return file_counter

    def get_issues_details(self, linter_name: str) -> list[dict]:
        """
        Obtains detailed information about issues from the database for a specific linter.

        Args:
            linter_name (str): The name of the linter to fetch details for.

        Returns:
            list[dict]: A list of dictionaries containing details about the issues (file, severity, message).
        """
        issues_details = self.database.query(
            'SELECT file_path, severity, message, location FROM issues WHERE linter_name = :linter_name',
            {'linter_name': linter_name}
        )
        details = [
            {
                "linter": linter_name,
                "file": issue.file_path,
                "severity": issue.severity,
                "message": issue.message,
                "location": issue.location
            }
            for issue in issues_details
        ]
        return details

    def get_issues_counter_per_linter(self, linter_name: str) -> Counter:
        """
        Get the counter for issues per linter.

        Args:
            linter_name (str): The name of the linter.

        Returns:
            Counter: The counter for issues per linter.
        """
        issues: ListOfIssues = self.database.query(
            'SELECT\n    severity,\n    COUNT(*) AS amount\n' +
            'FROM issues\n' +
            'WHERE linter_name = :linter_name GROUP BY severity',
            {'linter_name': linter_name}
        )
        linter_counter: Counter = Counter()
        self._add_findings_to_counter(linter_counter, issues)
        return linter_counter

    def _add_findings_to_counter(self, count: Counter, findings: ListOfIssues) -> None:
        for issue in findings:
            try:
                index = Severity[issue.severity]
                count.counter[index] += issue.amount
            except KeyError:
                logger.debug("Something went wrong while counting the level")

    def iter_linters_names(self) -> Generator[str, None, None]:
        """
        Iterate over linter names in the database.

        Yields:
            str: A linter name.
        """
        linters: list[str] = self.database.query("SELECT DISTINCT linter_name FROM issues")
        for linter in linters:
            yield linter[0]

    def iter_files_names(self, linter_name: str) -> Generator[str, None, None]:
        """
        Iterate over unique file names for a given linter in the database.

        Args:
            linter_name (str): The name of the linter.

        Yields:
            str: A file name.
        """
        files: list[str] = self.database.query(
            "SELECT DISTINCT file_path FROM issues WHERE linter_name = :linter_name",
            {'linter_name': linter_name}
        )
        for file in files:
            yield file[0]
