# In V2 are new linters (i.e. V2 has a linter not tracked in V1)
# pylint: disable=duplicate-code

from dev_from_baseline.counter import Counter

FILENAME_V1 = "test_files/pip_audit_V1.json"
FILENAME_V2 = "test_files/npm_audit_V2.json"

EXPECTED_FINDINGS = {
    'npm': {
        'files': {
            'async': (
                Counter(
                    [0, 0, 0, 0, 0, 0]
                ),
                Counter(
                    [0, 0, 0, 0, 2, 0]
                )
            ),
            'axios': (
                Counter(
                    [0, 0, 0, 0, 0, 0]
                ),
                Counter(
                    [0, 0, 0, 1, 1, 0]
                )
            ),
            'bl': (
                Counter(
                    [0, 0, 0, 0, 0, 0]
                ),
                Counter(
                    [0, 0, 0, 1, 0, 0]
                )
            ),
            'braces': (
                Counter(
                    [0, 0, 0, 0, 0, 0]
                ),
                Counter(
                    [0, 0, 2, 0, 0, 0]
                )
            ),
            'cryptiles': (
                Counter(
                    [0, 0, 0, 0, 0, 0]
                ),
                Counter(
                    [0, 0, 0, 0, 1, 0]
                )
            ),
            'decode-uri-component': (
                Counter(
                    [0, 0, 0, 0, 0, 0]
                ),
                Counter(
                    [0, 0, 1, 0, 0, 0]
                )
            ),
            'degenerator': (
                Counter(
                    [0, 0, 0, 0, 0, 0]
                ),
                Counter(
                    [0, 0, 0, 0, 1, 0]
                )
            )
        },
        'total': (
            Counter(
                [0, 0, 0, 0, 0, 0]
            ),
            Counter(
                [0, 0, 3, 2, 5, 0]
            )
        )
    }
}
