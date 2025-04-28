#!/bin/bash

source /opt/venv/bin/activate

cd /code
RUN_PORT=${PORT:-8000}
RUN_HOST=${HOST:-0.0.0.0}
APP_ENV=${APP_ENV:-development}

# if env is for local or development run this command
# "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"
# if env is for production run this command
# "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "$RUN_HOST:$RUN_PORT", "main:app"



if [ "$APP_ENV" = "production" ]; then
    echo "Starting in production mode..."
    exec gunicorn -k uvicorn.workers.UvicornWorker -b "$RUN_HOST:$RUN_PORT" main:app
else
    echo "Starting in development mode..."
    exec uvicorn src.main:app --host "0.0.0.0" --port "8000" --reload
fi
