# pylint:disable=import-error
from overrides import overrides
from you_shall_not_parse.observer import Observer
from you_shall_not_parse.base_classes import IssueTupleType


class ConsoleObserver(Observer):
    # pylint:disable=too-few-public-methods
    @overrides(check_signature=False)
    def add_issue(self, linter_name: str, issue: IssueTupleType) -> None:
        print((linter_name, issue[0].name, *issue[1:]))
