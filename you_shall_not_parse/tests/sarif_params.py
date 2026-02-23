from you_shall_not_parse.base_classes import Severity
from typing import List, Tuple

BANDIT_AMOUNT = 14
ESLINT_AMOUNT = 2
SEMGREP_AMOUNT = 1019
TRIVY_AMOUNT = 22
GITLEAKS_AMOUNT = 2
ALL_AMOUNT: int = BANDIT_AMOUNT + ESLINT_AMOUNT + SEMGREP_AMOUNT + TRIVY_AMOUNT + GITLEAKS_AMOUNT
ALL_EXAMPLES = [
     "examples/gitleaks.sarif",
     "examples/bandit.sarif",
     "examples/eslint.sarif",
     "examples/semgrep.sarif",
     "examples/trivy.sarif"
]
LINTERS_AMOUNT: int = 5

TRIVY_EXPECTED: Tuple[List[Tuple[str, Severity, str, str, str, int]], str] = ([
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2022-3715', 'Package: bash\nInstalled Version: 5.1-6ubuntu1\nVulnerability CVE-2022-3715\nSeverity: LOW\nFixed Version: \nLink: [CVE-2022-3715](https://avd.aquasec.com/nvd/cve-2022-3715)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2016-2781', 'Package: coreutils\nInstalled Version: 8.32-4.1ubuntu1\nVulnerability CVE-2016-2781\nSeverity: LOW\nFixed Version: \nLink: [CVE-2016-2781](https://avd.aquasec.com/nvd/cve-2016-2781)', 1),
     ('Trivy', Severity.WARNING, 'library/7a1af8b86aa5', 'CVE-2022-43551', 'Package: curl\nInstalled Version: 7.81.0-1ubuntu1.6\nVulnerability CVE-2022-43551\nSeverity: MEDIUM\nFixed Version: \nLink: [CVE-2022-43551](https://avd.aquasec.com/nvd/cve-2022-43551)', 1),
     ('Trivy', Severity.WARNING, 'library/7a1af8b86aa5', 'CVE-2022-43552', 'Package: curl\nInstalled Version: 7.81.0-1ubuntu1.6\nVulnerability CVE-2022-43552\nSeverity: MEDIUM\nFixed Version: \nLink: [CVE-2022-43552](https://avd.aquasec.com/nvd/cve-2022-43552)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2022-3219', 'Package: gpgv\nInstalled Version: 2.2.27-3ubuntu2.1\nVulnerability CVE-2022-3219\nSeverity: LOW\nFixed Version: \nLink: [CVE-2022-3219](https://avd.aquasec.com/nvd/cve-2022-3219)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2016-20013', 'Package: libc-bin\nInstalled Version: 2.35-0ubuntu3.1\nVulnerability CVE-2016-20013\nSeverity: LOW\nFixed Version: \nLink: [CVE-2016-20013](https://avd.aquasec.com/nvd/cve-2016-20013)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2016-20013', 'Package: libc6\nInstalled Version: 2.35-0ubuntu3.1\nVulnerability CVE-2016-20013\nSeverity: LOW\nFixed Version: \nLink: [CVE-2016-20013](https://avd.aquasec.com/nvd/cve-2016-20013)', 1),
     ('Trivy', Severity.WARNING, 'library/7a1af8b86aa5', 'CVE-2022-43551', 'Package: libcurl4\nInstalled Version: 7.81.0-1ubuntu1.6\nVulnerability CVE-2022-43551\nSeverity: MEDIUM\nFixed Version: \nLink: [CVE-2022-43551](https://avd.aquasec.com/nvd/cve-2022-43551)', 1),
     ('Trivy', Severity.WARNING, 'library/7a1af8b86aa5', 'CVE-2022-43552', 'Package: libcurl4\nInstalled Version: 7.81.0-1ubuntu1.6\nVulnerability CVE-2022-43552\nSeverity: MEDIUM\nFixed Version: \nLink: [CVE-2022-43552](https://avd.aquasec.com/nvd/cve-2022-43552)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2022-29458', 'Package: libncurses6\nInstalled Version: 6.3-2\nVulnerability CVE-2022-29458\nSeverity: LOW\nFixed Version: \nLink: [CVE-2022-29458](https://avd.aquasec.com/nvd/cve-2022-29458)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2022-29458', 'Package: libncursesw6\nInstalled Version: 6.3-2\nVulnerability CVE-2022-29458\nSeverity: LOW\nFixed Version: \nLink: [CVE-2022-29458](https://avd.aquasec.com/nvd/cve-2022-29458)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2017-11164', 'Package: libpcre3\nInstalled Version: 2:8.39-13ubuntu0.22.04.1\nVulnerability CVE-2017-11164\nSeverity: LOW\nFixed Version: \nLink: [CVE-2017-11164](https://avd.aquasec.com/nvd/cve-2017-11164)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2022-3857', 'Package: libpng16-16\nInstalled Version: 1.6.37-3build5\nVulnerability CVE-2022-3857\nSeverity: LOW\nFixed Version: \nLink: [CVE-2022-3857](https://avd.aquasec.com/nvd/cve-2022-3857)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2022-3996', 'Package: libssl3\nInstalled Version: 3.0.2-0ubuntu1.7\nVulnerability CVE-2022-3996\nSeverity: LOW\nFixed Version: \nLink: [CVE-2022-3996](https://avd.aquasec.com/nvd/cve-2022-3996)', 1),
     ('Trivy', Severity.WARNING, 'library/7a1af8b86aa5', 'CVE-2022-3821', 'Package: libsystemd0\nInstalled Version: 249.11-0ubuntu3.6\nVulnerability CVE-2022-3821\nSeverity: MEDIUM\nFixed Version: \nLink: [CVE-2022-3821](https://avd.aquasec.com/nvd/cve-2022-3821)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2022-29458', 'Package: libtinfo6\nInstalled Version: 6.3-2\nVulnerability CVE-2022-29458\nSeverity: LOW\nFixed Version: \nLink: [CVE-2022-29458](https://avd.aquasec.com/nvd/cve-2022-29458)', 1),
     ('Trivy', Severity.WARNING, 'library/7a1af8b86aa5', 'CVE-2022-3821', 'Package: libudev1\nInstalled Version: 249.11-0ubuntu3.6\nVulnerability CVE-2022-3821\nSeverity: MEDIUM\nFixed Version: \nLink: [CVE-2022-3821](https://avd.aquasec.com/nvd/cve-2022-3821)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2016-20013', 'Package: locales\nInstalled Version: 2.35-0ubuntu3.1\nVulnerability CVE-2016-20013\nSeverity: LOW\nFixed Version: \nLink: [CVE-2016-20013](https://avd.aquasec.com/nvd/cve-2016-20013)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2022-29458', 'Package: ncurses-base\nInstalled Version: 6.3-2\nVulnerability CVE-2022-29458\nSeverity: LOW\nFixed Version: \nLink: [CVE-2022-29458](https://avd.aquasec.com/nvd/cve-2022-29458)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2022-29458', 'Package: ncurses-bin\nInstalled Version: 6.3-2\nVulnerability CVE-2022-29458\nSeverity: LOW\nFixed Version: \nLink: [CVE-2022-29458](https://avd.aquasec.com/nvd/cve-2022-29458)', 1),
     ('Trivy', Severity.NOTE, 'library/7a1af8b86aa5', 'CVE-2022-3996', 'Package: openssl\nInstalled Version: 3.0.2-0ubuntu1.7\nVulnerability CVE-2022-3996\nSeverity: LOW\nFixed Version: \nLink: [CVE-2022-3996](https://avd.aquasec.com/nvd/cve-2022-3996)', 1),
     ('Trivy', Severity.WARNING, 'library/7a1af8b86aa5', 'CVE-2021-31879', 'Package: wget\nInstalled Version: 1.21.2-2ubuntu1\nVulnerability CVE-2021-31879\nSeverity: MEDIUM\nFixed Version: \nLink: [CVE-2021-31879](https://avd.aquasec.com/nvd/cve-2021-31879)', 1)
], "examples/trivy.sarif")
