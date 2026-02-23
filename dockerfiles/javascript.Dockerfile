FROM ghcr.io/eclypsium/dfb/base:latest

RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install njsscan && \
    npm install -g eslint@8.39.0
