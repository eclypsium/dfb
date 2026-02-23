from typing import Final
from typing_extensions import TypedDict, NamedTuple
from dev_from_baseline.counter import CounterComparison

ERROR_CODE: Final = 1

FilenameType = str
CounterType = dict[str, int]

FilesType = dict[FilenameType, CounterType]
LinterName = str
class LinterDict(TypedDict):
    total: CounterType
    files: FilesType

BaselineType = dict[LinterName, LinterDict]
# {
#   linter1:{
#       "total":[int, int, int, int],
#       "files": {
#           "file1": [int, int, int, int],
#           ...
#       }
#   },
#   linter2
#   ...
# }

class FileComparison(NamedTuple):
    file_name: str
    comparison: CounterComparison

ResultType = dict[LinterName, list[FileComparison]]
