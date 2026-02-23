import json
from typing import Optional
from you_shall_not_parse.handler_classes import (
    ParserHandlerImplementation,
    validate_schema,
    load_schema,
    ReturnHandleType
)
from you_shall_not_parse.base_classes import IssueTupleType, Severity
from you_shall_not_parse.observer import Observer

RequestType = list[dict[str, str]]
IssueType = dict[str, str]

class PylintHandler(ParserHandlerImplementation):
    def handle(self, request: str, observer: Observer) -> ReturnHandleType:
        schema = load_schema("pylint_schema.json")
        self.observer = observer
        if not validate_schema(request, schema):
            return super().handle(request, observer)
        pylint = json.loads(request)
        self._parse_pylint(pylint)
        return None

    def _parse_pylint(self, res: RequestType) -> None:
        for issue in res:
            pylint_issue = self._get_issue(issue)
            if pylint_issue is not None:
                self.observer.add_issue("pylint", pylint_issue)

    def _get_issue(self, issue: IssueType) -> Optional[IssueTupleType]:
        msg = issue['message']
        issue_id = issue['symbol']
        level = self._parse_level(issue['type'])
        if level is None:
            return None
        location = str(issue['line'])
        return (level, issue['path'], issue_id, msg, location)

    def _parse_level(self, level: str) -> Optional[Severity]:
        level_map = {
            "error": Severity.HIGH,
            "warning": Severity.MEDIUM,
            "refactor": Severity.LOW,
            "convention": Severity.LOW
        }
        return level_map.get(level, Severity.UNDEFINED)

HANDLER = PylintHandler
