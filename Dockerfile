#
# Base image with defaults for all stages
FROM registry.access.redhat.com/ubi9-minimal@sha256:383329bf9c4f968e87e85d30ba3a5cb988a3bbde28b8e4932dcd3a025fd9c98c AS base

COPY LICENSE /licenses/

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
FROM registry.access.redhat.com/ubi9/python-312@sha256:2049a086cccdabf5608cbdc9cd022f3e54d2344f7e11dc156f6f3fa0f5a3c9b6 AS builder
COPY --from=ghcr.io/astral-sh/uv:0.7.17@sha256:68a26194ea8da0dbb014e8ae1d8ab08a469ee3ba0f4e2ac07b8bb66c0f8185c1 /uv /bin/uv
ENV \
    # use venv from ubi image
    UV_PROJECT_ENVIRONMENT=${APP_ROOT} \
    # compile bytecode for faster startup
    UV_COMPILE_BYTECODE="true" \
    # disable uv cache. it doesn't make sense in a container
    UV_NO_CACHE=true

COPY --chown=1001:root packages/automated_actions_utils packages/automated_actions_utils
COPY --chown=1001:root packages/automated_actions packages/automated_actions
COPY --chown=1001:root README.md pyproject.toml uv.lock ./
RUN cd packages/automated_actions && uv sync --frozen --no-group dev --verbose

#
# Test image
#
FROM base AS test
COPY --from=ghcr.io/astral-sh/uv:0.7.17@sha256:68a26194ea8da0dbb014e8ae1d8ab08a469ee3ba0f4e2ac07b8bb66c0f8185c1 /uv /bin/uv

COPY Makefile ./
COPY --from=builder /opt/app-root /opt/app-root
RUN uv sync --frozen --verbose
RUN make test


#
# Production image
#
FROM base AS prod
COPY --from=builder /opt/app-root /opt/app-root
COPY app.sh ./
ENTRYPOINT [ "./app.sh" ]
