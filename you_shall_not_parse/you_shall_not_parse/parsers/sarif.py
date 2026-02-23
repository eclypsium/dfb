from typing import Union
import json

from you_shall_not_parse.handler_classes import (
    ParserHandlerImplementation,
    validate_schema,
    load_schema,
    ReturnHandleType
)
from you_shall_not_parse.base_classes import Severity
from you_shall_not_parse.observer import Observer

MessageType = dict[str, str]
LocationType = list[dict[str, dict[str, dict[str, str]]]]
InsideResultsType = dict[str, Union[str, 'MessageType', 'LocationType']]
ResultsType = list['InsideResultsType']
IssuesType = dict[str, str | dict[str, str]]
RulesType = list['IssuesType']


class SarifHandler(ParserHandlerImplementation):
    linter_name: str = ""

    def handle(self, request: str, observer: Observer) -> ReturnHandleType:
        schema = load_schema("sarif_schema.json")
        self.observer = observer
        if validate_schema(request, schema):
            self.parse(request)
            return None
        return super().handle(request, observer)

    def parse(self, request: str) -> None:
        sarif = json.loads(request)['runs'][0]
        runned = False
        if sarif['tool']['driver']['name']:
            self.linter_name = sarif['tool']['driver']['name']
        if 'results' in sarif:
            if sarif['results']:
                runned = True
                self.parse_results(sarif['results'])
        if 'rules' in sarif['tool']['driver'] and not runned:
            if sarif['tool']['driver']['rules']:
                self.parse_rules(sarif['tool']['driver']['rules'])

    def parse_results(self, res: ResultsType) -> None:
        for issue in res:
            if isinstance(issue['ruleId'], str):
                issue_id = issue['ruleId']
            level = self.get_level_from_result(issue)
            fn_msg_loc = self.parse_issue_in_result(issue)
            self.observer.add_issue(
                self.linter_name,
                (self.parse_level(level), fn_msg_loc[0], issue_id, fn_msg_loc[1], fn_msg_loc[2])
            )

    def get_level_from_result(self, issue: InsideResultsType) -> str:
        level = ""
        try:
            if isinstance(issue['level'], str):
                level = issue['level']
        except KeyError:
            pass
        return level

    def parse_issue_in_result(self, issue: InsideResultsType) -> tuple[str, str, str]:
        if isinstance(issue['message'], dict):
            message = issue['message']['text']
        res = self.get_location_and_filename(issue)
        location = res[0]
        filename = res[1]
        return (filename, message, location)

    def get_location_and_filename(self, issue: InsideResultsType) -> tuple[str, str]:
        if isinstance(issue['locations'], list):
            location = issue['locations'][0]['physicalLocation']['region']['startLine']
            filename = issue['locations'][0]['physicalLocation']['artifactLocation']['uri']
        else:
            location = ""
            filename = ""
        return (location, filename)

    def parse_rules(self, res: RulesType) -> None:
        for issue in res:
            if isinstance(issue['fullDescription'], dict):
                message = issue['fullDescription']['text']
            issue_loc = self.get_issueid_and_location(issue)
            level = self.get_level(issue)
            self.observer.add_issue(
                self.linter_name,
                (self.parse_level(level), issue_loc[0], issue_loc[0], message, issue_loc[1])
            )

    def get_issueid_and_location(self, issue: IssuesType) -> tuple[str, str]:
        issue_id = ""
        location = ""
        if isinstance(issue['id'], str):
            issue_id = issue['id']
        if isinstance(issue['name'], str):
            location = issue['name']
        return (issue_id, location)

    def get_level(self, issue: IssuesType) -> str:
        level = ""
        try:
            if isinstance(issue['defaultConfiguration'], dict):
                level = issue['defaultConfiguration']['level']
        except KeyError:
            pass
        return level

    def parse_level(self, level: str) -> Severity:
        match level:
            case "note":
                return Severity.NOTE
            case "warning":
                return Severity.WARNING
            case "error":
                return Severity.HIGH
            case _:
                return Severity.UNDEFINED


HANDLER = SarifHandler
