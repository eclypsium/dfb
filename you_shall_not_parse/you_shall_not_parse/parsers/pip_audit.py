from you_shall_not_parse.handler_classes import JmespathParserHandler
from you_shall_not_parse.base_classes import Severity
import jmespath


# mypy: disable_error_code=misc
class PipAuditHandler(JmespathParserHandler):
    class CustomFunctions(jmespath.functions.Functions):
        @jmespath.functions.signature({'types': ['object']}, {'types': ['array']})
        def _func_map_merge(self, obj: str, arg: list[dict[str, str]]) -> list[dict[str, str]]:
            result = []
            for element in arg:
                merged_object = super()._func_merge(obj, element)
                result.append(merged_object)
            return result

    def parse_level(self, level: str) -> Severity:
        # pylint:disable= unused-argument
        # Pip-audit not specifying the severity level, and this function is required
        return Severity.UNDEFINED

    JMESPATHQUERY = """dependencies[]
    | [?vulns]
    | [].map_merge({"name": name}, vulns[])
    | [].[None, name, id, description, None]
    """
    SCHEMA_FILENAME = "pipaudit_schema.json"
    LINTER_NAME = "pip-audit"
    OPTIONS = jmespath.Options(custom_functions=CustomFunctions())


HANDLER = PipAuditHandler
