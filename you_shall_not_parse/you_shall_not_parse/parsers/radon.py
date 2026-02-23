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

IssueType = dict[str, str]
ListIssueType = list['IssueType']
RequestType = dict[str, 'ListIssueType']
THRESHOLD = "A5"

class RadonHandler(ParserHandlerImplementation):
    def handle(self, request: str, observer: Observer) -> ReturnHandleType:
        schema = load_schema("radon_schema.json")
        self.observer = observer
        if not validate_schema(request, schema):
            return super().handle(request, observer)
        radon = json.loads(request)
        self.parse_radon(radon)
        return None

    def parse_radon(self, res: RequestType) -> None:
        for depn in res:
            for issue in res[depn]:
                radon_issue = self.get_issue(issue, depn)
                if radon_issue is not None:
                    self.observer.add_issue("radon", radon_issue)
                continue

    def get_issue(self, issue: IssueType, filename: str) -> Optional[IssueTupleType]:
        msg = issue['rank'] + str(issue['complexity'])
        if issue["type"] in ["class", "function"]:
            issue_id = issue['name']
            level = self._parse_level(issue['rank'] + str(issue["complexity"]))
            location = issue['lineno']
        elif issue["type"] == "method":
            issue_id = issue['classname'] + issue['name']
            level = self._parse_level(issue['rank'] + str(issue["complexity"]))
            location = issue['lineno']
        if level is None:
            return None
        return (level, filename, issue_id, msg, location)

    def _parse_level(self, level: str) -> Optional[Severity]:
        if level >= THRESHOLD:
            return Severity.MEDIUM
        return None


HANDLER = RadonHandler
