import csv
import io
from you_shall_not_parse.handler_classes import (
    ParserHandlerImplementation,
    ReturnHandleType
)
from you_shall_not_parse.base_classes import Severity, IssueTupleType
from you_shall_not_parse.observer import Observer


class LizardHandler(ParserHandlerImplementation):
    linter_name: str = "lizard"

    def handle(self, request: str, observer: Observer) -> ReturnHandleType:
        # Check if it looks like lizard CSV format
        if not self._is_lizard_csv(request):
            return super().handle(request, observer)
            
        # Try to parse as lizard CSV
        try:
            self.observer = observer
            self._parse_lizard_csv(request)
            return None
                
        except (csv.Error, ValueError, IndexError):
            return super().handle(request, observer)

    def _is_lizard_csv(self, request: str) -> bool:
    #Check if the content is a valid lizard CSV format.
        if ',' not in request or not request.strip():
            return False
        
        try:
            lines = request.strip().split('\n')[:5]
            csv_reader = csv.reader(lines)

            valid_rows = sum(1 for row in csv_reader if self._is_valid_row(row))
            return valid_rows > 0
        except (csv.Error, UnicodeDecodeError):
            return False

    def _is_valid_row(self, row: list[str]) -> bool:
        #check if row follow the lizard CSV formart
        if len(row) != 11:
            return False
        # Validate first 5 numeric columns
        if not all(self._is_int(row[i]) for i in range(5)): return False
            
       # Validate start and end lines
        if not self._is_valid_lines(row[9], row[10]):  return False
            
        # Validate file path
        if not self._is_valid_path(row[6]):  return False
            
        # Validate function name
        if not row[7].strip():  return False
            
        return True
    # Validate if value are int
    def _is_int(self, value: str) -> bool:
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False

    # Check ....
    def _is_valid_lines(self, start: str, end: str) -> bool:
        try:
            start_int = int(start)
            end_int = int(end)
            return start_int > 0 and end_int > 0 and start_int <= end_int
        except ValueError:
            return False


    def _is_valid_path(self, path: str) -> bool: return bool(path and ('/' in path or '\\' in path))
    
    def _parse_lizard_csv(self, csv_content: str) -> None:
         # Parse the CSV content
        csv_reader = csv.reader(io.StringIO(csv_content))
        for row in csv_reader:
                if len(row) < 11:  # Ensure we have enough columns
                    continue            
                try:
                    # nloc, ccn, token, param, length, name, file_path, function_name, signature, start_line, end_line
                    nloc = int(row[0])
                    ccn = int(row[1])
                    token = int(row[2])
                    param = int(row[3])
                    length = int(row[4])
                    name = row[5]
                    file_path = row[6]
                    function_name = row[7]
                    signature = row[8]
                    start_line = row[9]
                
                    if ccn >= 5 and int(start_line) > 0:
                        issue = (
                            Severity.HIGH,
                            file_path,
                            "high-complexity", 
                            f"Function '{function_name}' has high cyclomatic complexity: {ccn}",
                            start_line
                        )
                        self.observer.add_issue(self.linter_name, issue)
                        
                except (ValueError, IndexError):
                    continue


HANDLER = LizardHandler