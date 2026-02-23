# In V1 and V2 are issues in multiple linters
import pipaudit_params as pip_audit

FILENAME_LIST_V1 = ["test_files/pip_audit_V1.json", "test_files/npm_audit_V1.json"]
FILENAME_LIST_V2 = ["test_files/pip_audit_V2.json", "test_files/npm_audit_V1.json"]

EXPECTED_FINDINGS = pip_audit.EXPECTED_FINDINGS
