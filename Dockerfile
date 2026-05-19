FROM python:3.9-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy the project files
COPY . /app

# Sync dependencies using uv (includes the current project as editable if defined)
RUN uv sync --frozen --no-cache

EXPOSE 5000

ENV FLASK_APP=application.py

CMD ["uv", "run", "python", "application.py"]