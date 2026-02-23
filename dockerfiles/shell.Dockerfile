FROM ghcr.io/eclypsium/dfb/base:latest

RUN apt-get update && \
    apt-get install -y curl xz-utils build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/koalaman/shellcheck/releases/download/v0.8.0/shellcheck-v0.8.0.linux.x86_64.tar.xz | \
    tar xJf - && \
    mv shellcheck-v0.8.0/shellcheck /usr/local/bin/ && \
    rm -rf shellcheck-v0.8.0

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    . "$HOME/.cargo/env" && \
    cargo install shellcheck-sarif

ENV PATH="/root/.cargo/bin:${PATH}"
