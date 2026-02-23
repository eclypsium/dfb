# In V2 are new files (i.e. V2 has all the files of V1 and more)
from dev_from_baseline.counter import Counter

FILENAME_V1 = "test_files/pip_audit_V1.json"
FILENAME_V2 = "test_files/pip_audit_V2.json"

EXPECTED_FINDINGS = {
    'pip-audit': {
        'files': {
            'autocommand': (
                Counter(
                    [0, 0, 0, 0, 0, 0]
                ),
                Counter(
                    [0, 0, 0, 0, 0, 1]
                )
            )
        },
        'total': (
            Counter(
                [0, 0, 0, 0, 0, 3]
            ),
            Counter(
                [0, 0, 0, 0, 0, 4]
            )
        )
    }
}
