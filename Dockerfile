FROM python:3.13-slim

# For debugging
ENV PYTHONUNBUFFERED=True

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory at the root of the project
WORKDIR /

# Install dependencies with uv (creates .venv)
COPY . ./
RUN uv sync

# Add uv virtualenv to PATH so streamlit is found
#ENV PATH="/.venv/bin:$PATH"

# Copy the rest of the project

# Expose Streamlit port
EXPOSE 8501

# Run the app inside the container
CMD ["uvx", "streamlit", "run", "src/app.py"]
