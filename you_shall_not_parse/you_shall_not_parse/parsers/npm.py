from you_shall_not_parse.handler_classes import JmespathParserHandler
from you_shall_not_parse.base_classes import Severity


class NpmHandler(JmespathParserHandler):
    def parse_level(self, level: str) -> Severity:
        match level:
            case "critical":
                return Severity.HIGH
            case "high":
                return Severity.HIGH
            case "moderate":
                return Severity.MEDIUM
            case "low":
                return Severity.LOW
            case _:
                return Severity.UNDEFINED

    JMESPATHQUERY = "vulnerabilities.*.via[].[severity, name, source, title, range]"
    LINTER_NAME = "npm"
    SCHEMA_FILENAME = "npm_schema.json"


HANDLER = NpmHandler
