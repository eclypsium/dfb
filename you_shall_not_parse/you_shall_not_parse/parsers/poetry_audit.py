from you_shall_not_parse.handler_classes import JmespathParserHandler
from you_shall_not_parse.base_classes import Severity
import jmespath


# mypy: disable_error_code=misc
# Requiring _func_merge in superclass (missing in stubs of jmespath)
class PoetryAuditHandler(JmespathParserHandler):
    class CustomFunctions(jmespath.functions.Functions):
        @jmespath.functions.signature({'types': ['object']}, {'types': ['array']})
        def _func_map_merge(self, obj: str, arg: list[dict[str, str]]) -> list[dict[str, str]]:
            result = []
            for element in arg:
                merged_object = super()._func_merge(obj, element)
                result.append(merged_object)
            return result

    def parse_level(self, level: str) -> Severity:
        # pylint:disable=unused-argument
        # Pip-audit not specifying the severity level, and this function is required
        return Severity.UNDEFINED

    JMESPATHQUERY = """vulnerabilities[]
    | [?vulns]
    | [].map_merge({"name": name}, vulns[])
    | [].[None, name, cve, advisory, None]
    """
    SCHEMA_FILENAME = "poetryaudit_schema.json"
    LINTER_NAME = "poetry-audit"
    OPTIONS = jmespath.Options(custom_functions=CustomFunctions())


HANDLER = PoetryAuditHandler
