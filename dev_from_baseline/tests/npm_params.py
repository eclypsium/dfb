# Same linters with same total count but files doesn't have same amount

from dev_from_baseline.counter import Counter

FILENAME_V1 = "test_files/npm_audit_V1.json"
FILENAME_V2 = "test_files/npm_audit_V2.json"

EXPECTED_FINDINGS = {
    'npm': {
        'files': {
            'async': (
                Counter(
                    [0, 0, 0, 0, 1, 0]
                ),
                Counter(
                    [0, 0, 0, 0, 2, 0]
                )
            )
        },
        'total': (
            Counter(
                [0, 0, 3, 2, 5, 0]
            ),
            Counter(
                [0, 0, 3, 2, 5, 0]
            )
        )
    }
}
