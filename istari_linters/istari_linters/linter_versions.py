from typing import Final

LINTER_VERSIONS: Final = {
    "bandit": "1.7.8",
    "pip-audit": "2.5.2",
    "pylint": "3.3.6",
    "mypy": "1.15.0",
    "radon": "5.1.0",
    "eslint": "8.39.0",
    "hadolint": "2.12.0",
    "golangci-lint": "1.51.2",
    "lizardlint": "1.17.31",
    "shellcheck": "0.8.0",
    "rustup": "1.28.2",
}

# SHA-256 of the release assets installed by `istari.py --install`.
# Update them together with the matching version above.
# shellcheck: the project publishes no checksum, this is the hash of the downloaded asset.
LINTER_CHECKSUMS: Final = {
    "shellcheck": "ab6ee1b178f014d1b86d1e24da20d1139656c8b0ed34d2867fbb834dad02bf0a",
    "hadolint": "56de6d5e5ec427e17b74fa48d51271c7fc0d61244bf5c90e828aab8362d55010",
    "golangci-lint": "4de479eb9d9bc29da51aec1834e7c255b333723d38dbd56781c68e5dddc6a90b",
    "rustup-init": "20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c",
}
