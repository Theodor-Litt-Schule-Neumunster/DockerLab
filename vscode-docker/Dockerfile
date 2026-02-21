FROM codercom/code-server:latest

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    default-jdk \
    maven \
    gradle \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g npm@latest && \
    rm -rf /var/lib/apt/lists/*

USER coder

RUN code-server --install-extension ms-python.python || true && \
    code-server --install-extension ms-python.vscode-pylance || true && \
    code-server --install-extension redhat.java || true && \
    code-server --install-extension vscjava.vscode-java-pack || true && \
    code-server --install-extension vscjava.vscode-maven || true && \
    code-server --install-extension dbaeumer.vscode-eslint || true && \
    code-server --install-extension esbenp.prettier-vscode || true && \
    code-server --install-extension formulahendry.auto-close-tag || true && \
    code-server --install-extension ritwickdey.liveserver || true && \
    code-server --install-extension eamodio.gitlens || true

EXPOSE 8080
