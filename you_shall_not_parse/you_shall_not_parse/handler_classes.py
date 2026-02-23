from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Collection, List
import json
import os
from pathlib import Path
from xml.etree.ElementTree import Element  # nosec
from jsonschema import validate, ValidationError

# pylint:disable=import-error
import jmespath
from defusedxml import ElementTree as ET  # type: ignore
from lxml.etree import XMLSchema, parse as lxml_parse, fromstring # nosec


from you_shall_not_parse.base_classes import Severity, IssueTupleType
from you_shall_not_parse.observer import Observer

SearchedType = list["IssueType"]
IssueType = list[str]
SchemaType = dict[str, Collection[str]]
ReturnHandleType = Optional["ParserHandler"]


class SchemaInvalidError(BaseException):
    pass


class ParserHandler(ABC):
    """
    The Handler interface declares a method for building the chain of handlers.
    It also declares a method for executing a request.
    """

    @abstractmethod
    def set_next(self, handler: ParserHandler) -> ParserHandler:
        pass

    @abstractmethod
    def handle(self, request: str, observer: Observer) -> ReturnHandleType:
        pass


class ParserHandlerImplementation(ParserHandler):
    """
    The default chaining behavior can be implemented inside a base handler
    class.
    """

    _next_handler: Optional[ParserHandler] = None
    observer: Observer

    def set_next(self, handler: ParserHandler) -> ParserHandler:
        self._next_handler = handler
        return handler

    def handle(self, request: str, observer: Observer) -> ReturnHandleType:
        if self._next_handler:
            return self._next_handler.handle(request, observer)
        return None


class JmespathParserHandler(ParserHandlerImplementation):
    SCHEMA_FILENAME: str = ""
    JMESPATHQUERY: str = ""
    LINTER_NAME: str = ""
    OPTIONS: Optional[jmespath.Options] = None

    def handle(self, request: str, observer: Observer) -> ReturnHandleType:
        schema = load_schema(self.SCHEMA_FILENAME)
        self.observer = observer
        if not validate_schema(request, schema):
            return super().handle(request, observer)
        self._parse(request)
        return None

    @abstractmethod
    def parse_level(self, level: str) -> Severity:
        raise NotImplementedError

    def _parse(self, request: str) -> None:
        json_loaded = json.loads(request)
        compiled = jmespath.compile(self.JMESPATHQUERY)
        result = compiled.search(json_loaded, options=self.OPTIONS)
        return self._check_vuln(result)

    def _check_vuln(self, vuln: SearchedType) -> None:
        for issue in vuln:
            res = self._get_issue(issue)
            if res:
                self.observer.add_issue(self.LINTER_NAME, res)

    def _get_issue(self, issue: list[str]) -> Optional[IssueTupleType]:
        if issue:
            if any(issue):
                return (
                    self.parse_level(issue[0]),
                    issue[1],
                    issue[2],
                    issue[3],
                    issue[4],
                )
        return None


class JunitHandler(ParserHandlerImplementation):
    linter_name: str = ""

    def __init__(self) -> None:
        schema_doc = lxml_parse( # nosec
            os.path.join(Path(__file__).parent, "schemas/junit_schema.xsd")
        )
        self._schema = XMLSchema(schema_doc.getroot())

    def handle(self, request: str, observer: Observer) -> ReturnHandleType:
        self.observer = observer
        if self._is_junit_xml(request):
            self.parse(request)
            return None
        return super().handle(request, observer)

    def _is_junit_xml(self, request: str) -> bool:
        # pylint:disable=broad-exception-caught
        try:
            root = fromstring(request.encode("utf-8")) # nosec
            return self._schema.validate(root)
        except Exception as _:
            return False

    def parse(self, request: str) -> None:
        root = ET.fromstring(request)
        for elem in root.iter("testcase"):
            self._process_testcases(elem)

    def _process_testcases(self, root: Element) -> None:
        for testcase in root.iter("testcase"):
            self._process_failures(testcase)

    def _process_failures(self, testcase: Element) -> None:
        for failure in testcase.iter("failure"):
            self._process_messages(failure)

    def _process_messages(self, failure: Element) -> None:
        messages: List[str] = failure.text.split("\n") if failure.text else []
        for message in messages:
            self._process_message(message)

    @abstractmethod
    def _process_message(self, message: str) -> None:
        pass


def validate_schema(request: str, schema: Optional[SchemaType]) -> bool:
    result: bool = False
    if isinstance(schema, dict):
        try:
            req = json.loads(request)
            validate(req, schema=schema)
            result = True
        except (json.JSONDecodeError, ValidationError):
            result = False
    return result


def load_schema(schema_path: str) -> Optional[SchemaType]:
    """Load the JSON schema at the given path as a Python object.

    Args:
        schema_path: A filename for a JSON schema.

    Returns:
        A Python object representation of the schema.

    """
    schema: Optional[SchemaType] = None
    current_path = Path(__file__).parent
    schemas_path = os.path.join(current_path, "schemas/")
    try:
        with open(
            os.path.join(schemas_path, schema_path), "r", encoding="utf-8"
        ) as schema_file:
            schema = json.load(schema_file)
    except ValueError as error:
        print(f"Error in schema {error}")
        schema = None
    return schema
