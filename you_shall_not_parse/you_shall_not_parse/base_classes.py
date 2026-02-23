from enum import Enum, auto

IssueTupleType = tuple['Severity', str, str, str, str]


class Severity(Enum):
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    WARNING = auto()
    NOTE = auto()
    UNDEFINED = auto()
