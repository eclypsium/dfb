"""Module to extract report data from linters output files"""
from __future__ import annotations
from enum import IntEnum
from logging import getLogger
from typing import Callable, Optional
from rich.text import Text
from typing_extensions import NamedTuple

logger = getLogger("dev-from-baseline")

COLORS = ["green_yellow"]*3 + ["gold1"] + ["red1"] + ["grey50"]

class CounterComparison(NamedTuple):
    old: Counter
    new: Counter
    details: Optional[list[dict]] = None

    def to_dict(self) -> dict:
        result = {}
        if self.details:
            result["details"] = self.details
        return result

class Severity(IntEnum):
    NOTE = 0
    WARNING = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    UNDEFINED = 5


_SEVERITIES_COUNT = len(Severity)


class Counter:
    counter: list[int]

    def asdict(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for severity in Severity:
            result[severity.name.lower()] = self.counter[severity]
        return result

    def __init__(self, args: Optional[list[int]] = None) -> None:
        if args:
            self.counter = args
        else:
            self.counter = [0]*_SEVERITIES_COUNT

    def compare_against_counter(self, other: Counter, warn_less_issues: bool=False) -> bool:
        """
        Args:
            warn_less_issues (bool): warn when the new amount of issues
            are less than the amount saved on basefile.
            other: is the counter to be compared (self against other)

        Returns:
            bool: is the result of the comparison between self and other.
        """
        if warn_less_issues:
            return self.compare(lambda x, y: x != y, other)
        return self.compare(lambda x, y: x < y, other)

    def compare(self, func: Callable[[int, int], bool], other: Counter) -> bool:
        result = False
        for i in Severity:
            result = result or func(self.counter[i], other.counter[i])
        return result

    def total(self) -> int:
        return sum(self.counter)

    def from_dict(self, counter_dict: dict[str, int]) -> None:
        for severity in Severity:
            self.counter[severity] = counter_dict[severity.name.lower()]

    def to_text(self) -> Text:
        text = Text()
        for i in Severity:
            text.append(f"     {i.name}: {self.counter[i.value]}\n", style=COLORS[i.value])
        text.append(f"    TOTAL: {self.total()}", style="thistle1")
        return text

    def add_counters(self, counters: list[Counter]) -> None:
        for count in counters:
            self.counter = [sum(i) for i in zip(self.counter, count.counter)]
