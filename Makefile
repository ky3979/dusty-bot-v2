PACKAGE := src

# MAIN TASKS ##################################################################

.PHONY: all
all: install

.PHONY: run ## Start the program
run: install
	poetry run python main.py

.PHONY: hooks
hooks: .git/hooks/pre-push
.git/hooks/pre-push: pre-push
	cp pre-push .git/hooks/pre-push
	chmod +x .git/hooks/pre-push

# PROJECT DEPENDENCIES ########################################################

VIRTUAL_ENV ?= .venv
DEPENDENCIES := $(VIRTUAL_ENV)/.poetry-$(shell bin/checksum pyproject.toml poetry.lock)

.PHONY: install
install: $(DEPENDENCIES)

$(DEPENDENCIES): poetry.lock
	@ rm -rf $(VIRTUAL_ENV)/.flag-*
	poetry install ${POETRY_INSTALL_FLAGS}
	@ touch $@

ifndef CI
poetry.lock: pyproject.toml
	poetry lock --no-update
	@ touch $@
endif

# CHECKS ######################################################################

.PHONY: isort
isort: install
	poetry run isort --settings-path .ml-python-configs/.isort.cfg --project $(PACKAGE) --virtual-env .venv/ ${ISORT_ARGS} $(PACKAGE)

.PHONY: isort-check-only
isort-check-only: install
	@ ISORT_ARGS=--check-only make isort

.PHONY: pylint-package
pylint-package: install
	poetry run pylint --rcfile=.ml-python-configs/.pylintrc -dC0111 $(PACKAGE)

# .PHONY: pylint-tests
# pylint-tests: install
# 	poetry run pylint --rcfile=.ml-python-configs/.tests-pylintrc -dC0111 tests

.PHONY: pylint
pylint: pylint-package

.PHONY: format
format: install
	poetry run isort --settings-path .ml-python-configs/.isort.cfg --project $(PACKAGE) --virtual-env .venv/ ${ISORT_ARGS} $(PACKAGE)
	@ echo

.PHONY: lint
lint: pylint

# DATABASE ####################################################################
ARGS = $(foreach a,$($(subst -,_,$1)_args),$(if $(value $a),-$a "$($a)"))

ALEMBIC_PATH := ./migrations/alembic.ini
migrate_args = m

.PHONY: migrate
migrate: .install
	poetry run alembic -c $(ALEMBIC_PATH) revision --autogenerate $(call ARGS,$@)

.PHONY: upgrade
upgrade: .install
	poetry run alembic -c $(ALEMBIC_PATH) upgrade head

.PHONY: downgrade
downgrade: .install
	poetry run alembic -c $(ALEMBIC_PATH) downgrade -1


.install: poetry.lock
	poetry install
	touch .install

# HELP ########################################################################

.PHONY: help
help: all
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := run
