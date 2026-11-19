FROM python:3.14-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

FROM python:3.14-slim
WORKDIR /app
COPY --from=build /app/.venv .venv
COPY app app
COPY data data
RUN useradd --no-create-home api
USER api
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "--factory", "app.main:from_env", "--host", "0.0.0.0", "--port", "8000"]
