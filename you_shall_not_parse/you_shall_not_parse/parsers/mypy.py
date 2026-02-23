import re

from you_shall_not_parse.handler_classes import JunitHandler
from you_shall_not_parse.base_classes import Severity


class MypyHandler(JunitHandler):
    linter_name: str = "mypy"

    def _process_message(self, message: str) -> None:
        match = re.match(r"(.*):(\d+): (error|note): (.*)", message)
        if match:
            file, location, issue_type, issue_message = match.groups()
            severity: Severity = (
                Severity.HIGH if issue_type == "error" else Severity.NOTE
            )
            issue = (severity, file, issue_type, issue_message, location)
            self.observer.add_issue(self.linter_name, issue)


HANDLER = MypyHandler
