FROM python:3.13-slim

# For debugging
ENV PYTHONUNBUFFERED=True

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# set-up for PyQt5 map widget
from PyQt5.QtCore
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxtst6 \
    libssl3 \
    libnss3 \
    libnspr4 \
    libx11-xcb1 \
    libxcb1 \
    libxcb-glx0 \
    libxcb-keysyms1 \
    libxcb-image0 \
    libxcb-shm0 \
    libxcb-icccm4 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxkbcommon-x11-0 \
    libglu1-mesa \
    libx11-dev \
    libegl1 \
    libdbus-1-3 \
    libfreetype6 \
    xvfb \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app
ENV UV_VENV_PATH=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY . ./
RUN uv sync

EXPOSE 8501

CMD ["streamlit", "run", "src/app.py", "--server.port", "8051", "--server.address", "0.0.0.0"]
