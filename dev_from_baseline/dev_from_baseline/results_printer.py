from abc import ABC, abstractmethod
from dev_from_baseline.common import FileComparison, LinterName

# pylint: disable=too-few-public-methods
class ResultsPrinter(ABC):

    @abstractmethod
    def print_linter_results(
        self,
        linter_name: LinterName,
        comparison_list: list[FileComparison]
    ) -> None:
        pass
