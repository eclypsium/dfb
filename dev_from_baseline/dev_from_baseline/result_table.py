"""
Module: dev_from_baseline.result_table

This module defines the classes DiffPrinter and ResultTable
that format the display of differences in counts.
"""

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED
from dev_from_baseline.counter import Counter, Severity
from dev_from_baseline.common import FileComparison
from dev_from_baseline.results_printer import ResultsPrinter

SEVERITY_COLORS = {
    "HIGH": 'bold red',
    "MEDIUM": 'yellow',
    "LOW": 'green',
    "NOTE": 'dim white',
    "UNDEFINED": 'dim white'
}
class ResultTable(ResultsPrinter):
    def __init__(self, console: Console = Console()) -> None:
        self.table: Table
        self.console = console

    def print_linter_results(self, linter_name: str, comparison_list: list[FileComparison]) -> None:
        self.init_table(linter_name)
        self.fill_linter_table(comparison_list)
        self.console.print(self.table)

    def init_table(self, linter_name: str) -> None:
        title_style: Text = Text(f"\n{linter_name}\n", style="bold blink")
        self.table = Table(title=title_style, highlight=True, show_lines=True)
        self.table.add_column("STATUS", vertical="middle", justify="center", style="red bold")
        self.table.add_column("FILE", justify="left", style="cyan", overflow="fold")
        self.table.add_column("Previous Findings", justify="left", style="cyan", overflow="fold")
        self.table.add_column("Current Findings", justify="left", style="cyan", overflow="fold")
        self.table.add_column("Difference", justify="full", overflow="fold")

    def fill_linter_table(self, file_comparisons: list[FileComparison]) -> None:
        for file_comparison in file_comparisons:
            self.table.add_row(
                Text("❌\nFAIL", style="bright_red"),
                file_comparison.file_name,
                file_comparison.comparison[0].to_text(),
                file_comparison.comparison[1].to_text(),
                self._difference(file_comparison.comparison[0], file_comparison.comparison[1])
            )

    def _difference(self, previous: Counter, current: Counter) -> Text:
        diff = DiffPrinter()
        for severity in Severity:
            diff.add(previous.counter[severity], current.counter[severity], f"      {severity.name}")
        return diff.get_text()

class DiffPrinter():
    """
    Class for formatting differences in counts.

    Attributes:
        text (Text): A rich Text object for displaying differences.
        total (int): The total difference.
    """
    def __init__(self) -> None:
        self.text: Text = Text()
        self.total: int = 0

    def append_text(self, delta: int, label: str) -> None:
        style: str = self.get_style(delta)
        self.text.append(f"{label}:  {abs(delta)}\n", style=style)

    def get_style(self, delta: int) -> str:
        return "green1" if delta >= 0 else "bright_red"

    def add(self, previous: int, current: int, label: str) -> None:
        delta: int = previous - current
        self.append_text(delta, label)
        self.total += delta

    def get_text(self) -> Text:
        self.append_text(self.total, "    Delta")
        return self.text

class ResultTableIssues:
    def __init__(self, console: Console = Console()) -> None:
        self.console = console

    def generate_table(self, issues_data: list[dict]) -> None:
        table = self.init_table()
        for detail in issues_data:
            self.add_to_table(table, detail)
        self.console.print(table)

    def init_table(self) -> Table:
        table = Table(show_header=True, header_style="bold magenta", box=ROUNDED, show_lines=True)
        table.add_column("Linter", style="orange1")
        table.add_column("File", style="cyan")
        table.add_column("Severity", style="bold")
        table.add_column("Message", style="white")
        table.add_column("Line", style="white")
        return table

    def add_to_table(self, table: Table, detail: dict) -> None:
        severity_color = SEVERITY_COLORS.get(detail['severity'], 'dim white')
        table.add_row(
            detail['linter'],
            detail['file'],
            f"[{severity_color}] {detail['severity']} [/{severity_color}]",
            detail['message'],
            detail['location']
        )
