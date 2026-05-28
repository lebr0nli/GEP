ARG image=ubuntu:24.04
FROM $image

ARG ZIG_VERSION=0.16.0

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    ca-certificates \
    python3 \
    python3-pip \
    python3-venv \
    tmux \
    git \
    gdb \
    make \
    curl \
    wget \
    xz-utils \
    vim && \
    git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && \
    ~/.fzf/install --all

RUN set -eux; \
    case "$(uname -m)" in \
        x86_64) zig_arch=x86_64-linux ;; \
        aarch64) zig_arch=aarch64-linux ;; \
        *) echo "Unsupported Zig host architecture: $(uname -m)" >&2; exit 1 ;; \
    esac; \
    curl -fsSL "https://ziglang.org/download/${ZIG_VERSION}/zig-${zig_arch}-${ZIG_VERSION}.tar.xz" -o /tmp/zig.tar.xz; \
    mkdir -p /opt/zig; \
    tar -xJf /tmp/zig.tar.xz -C /opt/zig --strip-components=1; \
    rm /tmp/zig.tar.xz; \
    /opt/zig/zig version

ENV PATH="/opt/zig:/root/.fzf/bin:/root/.local/bin:${PATH}"

COPY --from=ghcr.io/astral-sh/uv:0.11.13 /uv /bin/

COPY . /root/.local/share/GEP

WORKDIR /root/.local/share/GEP

RUN ./install.sh --dev
