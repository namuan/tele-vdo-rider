export PROJECTNAME=$(shell basename "$(PWD)")

.SILENT: ;               # no need for @

setup: ## Setup Virtual Env
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

deps: ## Install dependencies
	./venv/bin/pip install -r requirements.txt

lint: ## Runs black for code formatting
	./venv/bin/black genie --exclude generated

clean: ## Clean package
	rm -rf build dist

run: ## Run all unit tests
	./venv/bin/python yt2audiobot.py

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