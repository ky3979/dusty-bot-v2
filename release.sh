#!/bin/bash

# Run migrations before slug is executed so that migration failures cause deploy/promote to fail and rollback

set -eo pipefail

ALEMBIC_PATH="./migrations/alembic.ini"

python -m alembic -c $ALEMBIC_PATH upgrade head
