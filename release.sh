#!/bin/bash

# Tasks for heroku release phase: https://devcenter.heroku.com/articles/release-phase
#
# Run migrations before slug is executed so that migration failures cause deploy/promote to fail and rollback

set -eo pipefail

FLASK_APP="services:create_app()" flask db upgrade
