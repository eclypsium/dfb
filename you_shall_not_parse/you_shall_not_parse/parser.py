from __future__ import annotations
from typing import Optional
import importlib.util
import importlib.machinery
import os
from pathlib import Path
import types

from you_shall_not_parse.observer import Observer
from you_shall_not_parse.handler_classes import ParserHandler, ReturnHandleType

InitialAndPreviousModuleType = tuple[Optional[ParserHandler], Optional[ParserHandler]]
Filename = str

class Parser():
    # pylint:disable=too-few-public-methods
    def __init__(self) -> None:
        self.chain = _get_chain()
        self.observer: Observer

    def parse_from_filenames(self, file_names_lists: list[Filename], observer: Observer) -> None:
        self.observer = observer
        for filename in file_names_lists:
            with open(filename, 'r', encoding="utf-8") as file:
                res = file.read()
                self._parse_str(res)

    def parse_from_str(self, content_to_parse: str, observer: Observer) -> None:
        self.observer = observer
        self._parse_str(content_to_parse)

    def _parse_str(self, content: str) -> Optional[ReturnHandleType]:
        result = None
        if self.chain:
            result = self.chain.handle(content, self.observer)
        return result


def _get_chain() -> Optional[ParserHandler]:
    current_path = Path(__file__).parent
    parsers_path = os.path.join(current_path, "parsers/")
    prev: Optional[ParserHandler] = None
    initial: Optional[ParserHandler] = None
    for module in os.listdir(parsers_path):
        module_path = parsers_path + module
        if os.path.isfile(module_path):
            initial, prev = _load_module(module, module_path, initial, prev)
    return initial


def _load_module(module: str, module_path: str, initial: Optional[ParserHandler],
                 prev: Optional[ParserHandler]) -> InitialAndPreviousModuleType:
    rule_module = _helper_loader(module, module_path)
    rule = rule_module.HANDLER
    instance = rule()
    if prev is None:
        initial = instance
        prev = instance
    else:
        prev = prev.set_next(instance)
    return (initial, prev)


def _helper_loader(module: str, path: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(module, path)
    if spec and spec.loader:
        rule_module = importlib.util.module_from_spec(spec)
        if rule_module:
            spec.loader.exec_module(rule_module)
            return rule_module
        raise ValueError
    raise ValueError
