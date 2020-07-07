export PROJECTNAME=$(shell basename "$(PWD)")

.SILENT: ;               # no need for @

setup: ## Setup Virtual Env
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

deps: ## Install dependencies
	./venv/bin/pip install -r requirements.txt

lint: ## Runs black for code formatting
	./venv/bin/black . --exclude venv

clean: ## Clean package
	rm -rf build dist

run: lint ## Run all unit tests
	./venv/bin/python yt-telegram-rider.py

package: clean
	./pypi.sh

.PHONY: help
.DEFAULT_GOAL := help

help: Makefile
	echo
	echo " Choose a command run in "$(PROJECTNAME)":"
	echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	echo