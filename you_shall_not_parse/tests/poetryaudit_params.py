from you_shall_not_parse.base_classes import Severity
from typing import List, Tuple

POETRY_AUDIT_AMOUNT = 2
ALL_AMOUNT: int = POETRY_AUDIT_AMOUNT
ALL_EXAMPLES = ["examples/poetry-audit.json"]

POETRYAUDIT_EXPECTED: Tuple[List[Tuple[str, Severity, str, str, str, None]], str] = ([
    ('poetry-audit', Severity.UNDEFINED, 'certifi', 'CVE-2022-23491', 'Certifi 2022.12.07 includes a fix for CVE-2022-23491: Certifi 2022.12.07 removes root certificates from "TrustCor" from the root store. These are in the process of being removed from Mozilla\'s trust store. TrustCor\'s root certificates are being removed pursuant to an investigation prompted by media reporting that TrustCor\'s ownership also operated a business that produced spyware. Conclusions of Mozilla\'s investigation can be found in the linked google group discussion.\r\nhttps://github.com/certifi/python-certifi/security/advisories/GHSA-43fp-rhv2-5gv8\r\nhttps://groups.google.com/a/mozilla.org/g/dev-security-policy/c/oxX69KFvsm4/m/yLohoVqtCgAJ', None),
    ('poetry-audit', Severity.UNDEFINED, 'py', 'CVE-2022-42969', 'Py throughout 1.11.0 allows remote attackers to conduct a ReDoS (Regular expression Denial of Service) attack via a Subversion repository with crafted info data, because the InfoSvnCommand argument is mishandled.\r\nhttps://github.com/pytest-dev/py/issues/287', None),
], "examples/poetry-audit.json")