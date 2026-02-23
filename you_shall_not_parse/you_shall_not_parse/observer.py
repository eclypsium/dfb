from __future__ import annotations
from abc import ABC, abstractmethod
from you_shall_not_parse.base_classes import IssueTupleType


class Observer(ABC):
    # pylint:disable=too-few-public-methods
    @abstractmethod
    def add_issue(self, linter_name: str, issue: IssueTupleType) -> None:
        pass
