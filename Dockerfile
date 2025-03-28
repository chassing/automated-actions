#
# Base image with defaults for all stages
FROM registry.access.redhat.com/ubi9/ubi-minimal@sha256:bafd57451de2daa71ed301b277d49bd120b474ed438367f087eac0b885a668dc AS base
ENV APP_ROOT=/opt/app-root
ENV \
    # use venv from ubi image
    UV_PROJECT_ENVIRONMENT=${APP_ROOT} \
    # compile bytecode for faster startup
    UV_COMPILE_BYTECODE="true" \
    # disable uv cache. it doesn't make sense in a container
    UV_NO_CACHE=true \
    BASH_ENV="${APP_ROOT}/bin/activate" \
    ENV="${APP_ROOT}/bin/activate" \
    PROMPT_COMMAND=". ${APP_ROOT}/bin/activate"

# Install base dependencies
RUN microdnf install -y python3.12 make && microdnf clean all
USER 1001
WORKDIR ${APP_ROOT}/src


#
# Builder image
#
FROM registry.access.redhat.com/ubi9/python-312@sha256:b3316249c58e1800118ec1f311514f6ec355a60d8c78383bfa868887952b2ee1 AS builder
COPY --from=ghcr.io/astral-sh/uv:0.6.9@sha256:cbc016e49b55190e17bfd0b89a1fdc1a54e0a54a8f737dfacc72eca9ad078338 /uv /bin/uv
ENV \
    # use venv from ubi image
    UV_PROJECT_ENVIRONMENT=${APP_ROOT} \
    # compile bytecode for faster startup
    UV_COMPILE_BYTECODE="true" \
    # disable uv cache. it doesn't make sense in a container
    UV_NO_CACHE=true

COPY packages/automated_actions/pyproject.toml uv.lock ./
# Install the project dependencies
RUN uv sync --frozen --no-install-project --no-group dev

COPY README.md ./
COPY --chown=1001:root packages/automated_actions packages/automated_actions
RUN uv sync --frozen --no-group dev


#
# Test image
#
FROM base AS test
COPY --from=ghcr.io/astral-sh/uv:0.6.9@sha256:cbc016e49b55190e17bfd0b89a1fdc1a54e0a54a8f737dfacc72eca9ad078338 /uv /bin/uv

COPY Makefile ./
COPY --from=builder /opt/app-root /opt/app-root
RUN uv sync --frozen
RUN make test


#
# Production image
#
FROM base AS prod
COPY --from=builder /opt/app-root /opt/app-root
COPY app.sh ./
ENTRYPOINT [ "./app.sh" ]
