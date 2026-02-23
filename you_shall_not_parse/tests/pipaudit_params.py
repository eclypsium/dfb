from you_shall_not_parse.base_classes import Severity
from typing import List, Tuple

PIP_AUDIT_AMOUNT = 5
ALL_AMOUNT: int = PIP_AUDIT_AMOUNT
ALL_EXAMPLES = ["examples/pip-audit.json", "examples/pip-audit-abram.json"]

PIPAUDIT_EXPECTED: Tuple[List[Tuple[str, Severity, str, str, str, None]], str] = ([
    ('pip-audit', Severity.UNDEFINED, 'certifi', 'GHSA-43fp-rhv2-5gv8', 'Certifi 2022.12.07 removes root certificates from "TrustCor" from the root store. These are in the process of being removed from Mozilla\'s trust store.  TrustCor\'s root certificates are being removed pursuant to an investigation prompted by media reporting that TrustCor\'s ownership also operated a business that produced spyware. Conclusions of Mozilla\'s investigation can be found [here](https://groups.google.com/a/mozilla.org/g/dev-security-policy/c/oxX69KFvsm4/m/yLohoVqtCgAJ).', None),
    ('pip-audit', Severity.UNDEFINED, 'gitpython', 'GHSA-hcpj-qp55-gfph', 'All versions of package gitpython are vulnerable to Remote Code Execution (RCE) due to improper user input validation, which makes it possible to inject a maliciously crafted remote URL into the clone command. Exploiting this vulnerability is possible because the library makes external calls to git without sufficient sanitization of input arguments.', None),
    ('pip-audit', Severity.UNDEFINED, 'py', 'PYSEC-2022-42969', 'The py library through 1.11.0 for Python allows remote attackers to conduct a ReDoS (Regular expression Denial of Service) attack via a Subversion repository with crafted info data, because the InfoSvnCommand argument is mishandled.', None)
], "examples/pip-audit.json")


PIPAUDIT_ABRAM_EXPECTED: Tuple[List[Tuple[str, Severity, str, str, str, None]], str] = ([
    ('pip-audit', Severity.UNDEFINED, 'gitpython', 'PYSEC-2024-4', 'GitPython is a python library used to interact with Git repositories. There is an incomplete fix for CVE-2023-40590. On Windows, GitPython uses an untrusted search path if it uses a shell to run `git`, as well as when it runs `bash.exe` to interpret hooks. If either of those features are used on Windows, a malicious `git.exe` or `bash.exe` may be run from an untrusted repository. This issue has been patched in version 3.1.41.', None),
    ('pip-audit', Severity.UNDEFINED, 'pip', 'PYSEC-2023-228', "When installing a package from a Mercurial VCS URL  (ie \"pip install  hg+...\") with pip prior to v23.3, the specified Mercurial revision could  be used to inject arbitrary configuration options to the \"hg clone\"  call (ie \"--config\"). Controlling the Mercurial configuration can modify  how and which repository is installed. This vulnerability does not  affect users who aren't installing from Mercurial. ", None),

], "examples/pip-audit-abram.json")
