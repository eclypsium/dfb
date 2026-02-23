from you_shall_not_parse.handler_classes import JmespathParserHandler
from you_shall_not_parse.base_classes import Severity


class GolangCiHandler(JmespathParserHandler):
    def parse_level(self, level: str) -> Severity:
        match level:
            case "warning":
                return Severity.WARNING
            case "medium":
                return Severity.MEDIUM
            case "error":
                return Severity.HIGH
            case "high":
                return Severity.HIGH
            case "low":
                return Severity.LOW
            case _:
                return Severity.UNDEFINED

    JMESPATHQUERY = "Issues[].[Severity, Pos.Filename, FromLinter, Text, Pos.Line]"
    LINTER_NAME = "golangci"

    SCHEMA_FILENAME = "golangci_schema.json"


HANDLER = GolangCiHandler
