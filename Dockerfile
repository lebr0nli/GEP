ARG image
FROM $image

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    tmux \
    git \
    gdb \
    curl \
    wget \
    vim && \
    git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && \
    ~/.fzf/install --all

ENV PATH="/root/.fzf/bin:/root/.local/bin:${PATH}"

COPY --from=ghcr.io/astral-sh/uv:0.5.14 /uv /bin/

COPY . /root/.local/share/GEP

WORKDIR /root/.local/share/GEP

RUN ./install.sh --dev
