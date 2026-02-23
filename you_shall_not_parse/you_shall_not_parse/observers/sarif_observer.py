from __future__ import annotations
from typing import Optional
from typing_extensions import TypedDict
# pylint:disable=import-error
from overrides import overrides
from you_shall_not_parse.observer import Observer
from you_shall_not_parse.base_classes import IssueTupleType

FileLineType = dict[str, str]
FilenameLocationType = dict[str, str]


class PhysicalLocation(TypedDict):
    artifactLocation: FilenameLocationType
    region: FileLineType


class Results(TypedDict):
    ruleId: str
    level: str
    message: dict[str, str]
    locations: list[dict[str, PhysicalLocation]]


class Driver(TypedDict):
    name: Optional[str]
    rules: list[str]


class Tools(TypedDict):
    driver: Driver


class Runs(TypedDict):
    tool: Tools
    results: list[Results]


SarifType = TypedDict('SarifType', {
    '$schema': str,
    'runs': list['Runs']
}, total=True)


class SarifObserver(Observer):
    tools: Runs = {
        "tool": {
            "driver": {
                "name": None,
                "rules": []
            }
        },
        "results": [],
        }
    sarif: SarifType = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0-rtm.5.json",
        "runs": []
    }
    index = 0
    seen_linters: list[str] = []

    def get_sarif_json(self) -> SarifType:
        return self.sarif

    @overrides(check_signature=False)
    def add_issue(self, linter_name: str, issue: IssueTupleType) -> None:
        result: Results = {
            'ruleId': issue[2],
            'level': issue[0].name.lower(),
            'message': {
                'text': issue[3]
            },
            'locations': [{
                'physicalLocation': {
                    'artifactLocation': {
                        'uri': issue[1]
                    },
                    'region': {
                        'startLine': issue[4]
                    }
                }
            }
            ]
        }
        if linter_name in self.seen_linters:
            self.index = self.seen_linters.index(linter_name)
            self.sarif['runs'][self.index]['results'].append(result)
        else:
            self.index = len(self.seen_linters)
            self.seen_linters.append(linter_name)
            run: Runs = self.tools
            run['tool']['driver']['name'] = linter_name
            run['results'] = [result]
            self.sarif['runs'].append(run)
