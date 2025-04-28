
FROM python:3.12-slim-bullseye AS builder
WORKDIR /core
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install os dependencies for our mini vm
RUN apt-get update && apt-get install -y \
    # for postgres
    libpq-dev \
    # for Pillow
    libjpeg-dev \
    # for CairoSVG
    libcairo2 \
    # other
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /core/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /core/wheels -r /core/requirements.txt



FROM python:3.12-slim-bullseye
WORKDIR /core
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY /src /core/src

RUN apt update && apt install vim -y && pip install --upgrade pip setuptools wheel

COPY --from=builder /core/wheels /wheels
RUN pip install --no-cache /wheels/* && rm -r /wheels
# Run the FastAPI project via the runtime script
# when the container starts
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]