FROM ghcr.io/eclypsium/dfb/base:latest

RUN pip install \
    "bandit[sarif]==1.7.8" \
    "pylint==3.3.6" \
    "mypy==1.15.0" \
    "lizard==1.17.31"
