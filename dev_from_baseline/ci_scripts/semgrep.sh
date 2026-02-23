#!/bin/sh
set -eu

cd "$(dirname "${0}")/.."

semgrep \
    --config "p/ci" \
    --config "p/command-injection" \
    --config "p/flask" \
    --config "p/gitlab-bandit" \
    --config "p/insecure-transport" \
    --config "p/jwt" \
    --config "p/owasp-top-ten" \
    --config "p/python" \
    --config "p/r2c" \
    --config "p/r2c-bug-scan" \
    --config "p/r2c-ci" \
    --config "p/sql-injection" \
    --config "p/trailofbits" \
    --config "p/xss" \
    --include='*.py' \
    --error \
    --exclude="test*" \
    --sarif \
    --metrics=off \
    --output semgrep.sarif
