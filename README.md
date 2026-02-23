# dfb — Deviation from Baseline

A toolkit for running static analysis linters and tracking code quality over time. It compares linter results against a stored baseline to detect regressions in CI/CD pipelines.

## Project structure

```
dfb/
├── dev_from_baseline/       # CLI tool — compares linter results against a JSON baseline
├── you_shall_not_parse/     # Library — parses linter outputs into a unified format
├── istari_linters/          # Runner — orchestrates linters per language
└── dockerfiles/             # Per-language Docker images
```

### dev_from_baseline

CLI tool that reads linter report files, compares them against a stored `basefile.json`, and exits with a status code indicating whether code quality has improved, stayed the same, or declined.

```
dev-from-baseline -b basefile.json -r linters_results/* -v -d
```

Exit codes: `0` = same, `1` = worse (regression), `2` = improved.

Use `--generate` to create or update the baseline from current results.

### you_shall_not_parse

Parser library that normalizes outputs from different linters (JSON, CSV, XML, SARIF) into a unified format via an observer pattern. Supports: bandit, pylint, mypy, lizard, npm-audit, pip-audit, poetry-audit, golangci-lint, eslint, semgrep, trivy, gitleaks, and any SARIF-compatible tool.

### istari_linters

Script that runs the appropriate set of linters for a given language. Each language has a strategy with its own linter set:

| Language   | Linters                                  |
|------------|------------------------------------------|
| python     | bandit, pylint, mypy, lizard             |
| javascript | njsscan, eslint, npm audit               |
| go         | golangci-lint                            |
| shell      | shellcheck                               |
| dockerfile | hadolint                                 |

```
python istari.py -l python -e tests -r -f src/myproject
```

## Docker images

Pre-built images are available on GitHub Container Registry. A **base image** provides the core tooling, and **per-language images** extend it with the relevant linters installed natively.

| Image | Contents |
|-------|----------|
| `ghcr.io/eclypsium/dfb/base` | Python 3.12, dev-from-baseline CLI, you_shall_not_parse, istari.py |
| `ghcr.io/eclypsium/dfb/python` | base + bandit, pylint, mypy, lizard |
| `ghcr.io/eclypsium/dfb/javascript` | base + Node.js 20, njsscan, eslint |
| `ghcr.io/eclypsium/dfb/go` | base + golangci-lint |
| `ghcr.io/eclypsium/dfb/shell` | base + shellcheck, shellcheck-sarif |
| `ghcr.io/eclypsium/dfb/dockerfile` | base + hadolint |

### Using a per-language image

Pick the image that matches your project language and run linters + baseline comparison:

```bash
docker run --rm -v "$PWD:/project" ghcr.io/eclypsium/dfb/python:latest \
  /bin/bash -c "cd /project && \
    python3 /opt/dfb/istari_linters/istari_linters/istari.py -l python -e tests -r -f /project/src && \
    dev-from-baseline -b /project/basefile.json -r /project/linters_results/* -v"
```

For a Go project, swap the image and language flag:

```bash
docker run --rm -v "$PWD:/project" ghcr.io/eclypsium/dfb/go:latest \
  /bin/bash -c "cd /project && \
    python3 /opt/dfb/istari_linters/istari_linters/istari.py -l go -r -f /project && \
    dev-from-baseline -b /project/basefile.json -r /project/linters_results/* -v"
```

### Building a custom image

Derive from the base image to create a tailored image with your own linter selection:

```dockerfile
FROM ghcr.io/eclypsium/dfb/base:latest

# Install only the linters you need
RUN pip install "bandit[sarif]==1.7.8" "mypy==1.15.0"

# Add project-specific tooling
RUN pip install custom-linter
```

This gives you the full `dev-from-baseline` + `you_shall_not_parse` + `istari.py` stack with only the linters your project actually uses.

### CI/CD example (GitLab CI)

```yaml
dev-from-baseline:
  image: ghcr.io/eclypsium/dfb/python:latest
  stage: lint
  script:
    - python3 /opt/dfb/istari_linters/istari_linters/istari.py -l python -e tests -r -f src/myproject
    - dev-from-baseline -b basefile.json -r linters_results/* -v
  artifacts:
    when: always
    paths:
      - linters_results/
      - basefile.json
```

### CI/CD example (GitHub Actions)

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/eclypsium/dfb/python:latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          python3 /opt/dfb/istari_linters/istari_linters/istari.py -l python -e tests -r -f src/myproject
          dev-from-baseline -b basefile.json -r linters_results/* -v
```

## Generating a baseline

To create the initial `basefile.json` for a project:

```bash
docker run --rm -v "$PWD:/project" ghcr.io/eclypsium/dfb/python:latest \
  /bin/bash -c "cd /project && \
    python3 /opt/dfb/istari_linters/istari_linters/istari.py -l python -e tests -r -f /project/src && \
    dev-from-baseline -b /project/basefile.json -r /project/linters_results/* -g"
```

The `-g` flag generates the baseline instead of comparing against one.
