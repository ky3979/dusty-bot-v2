#!/bin/bash

set -eo pipefail

# Gunicorn settings
# http://gunicorn-docs.readthedocs.org/en/latest/settings.html

ARGS="services:create_app()"

# Heroku default is 5000, which doesnt work on macs
ARGS+=" --bind 0.0.0.0:${PORT:-8000}"

## Concurrency Settings
# The number of worker processes for handling requests.
WORKERS=${WEB_CONCURRENCY:-$((2 * $(getconf _NPROCESSORS_ONLN) + 1))}
ARGS+=" --workers ${WORKERS}"

# Logging
ARGS+=" --log-level ${GUNICORN_LOG_LEVEL:-info}"

if [ "$DEBUG" ]; then
    # autorestart when code changes
    ARGS+=" --reload"
fi

echo "ENV = ${ENV:-dev}"
echo "gunicorn $ARGS"
gunicorn $ARGS
