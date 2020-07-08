export PROJECTNAME=$(shell basename "$(PWD)")

.SILENT: ;               # no need for @

setup: ## Setup Virtual Env
	python3 -m venv venv
	./venv/bin/pip install -r requirements/dev.txt

deps: ## Install dependencies
	./venv/bin/pip install -r requirements/dev.txt

lint: ## Runs black for code formatting
	./venv/bin/black . --exclude venv

clean: ## Clean package
	find . -type d -name '__pycache__' | xargs rm -rf
	rm -rf build dist

deploy: clean ## Copies any changed file to the server
	ssh ${PROJECTNAME} -C 'bash -l -c "mkdir -vp ./yt-telegram-rider"'
	rsync -avzr \
		env.cfg \
		yt-telegram-rider.py \
		bot \
		common \
		config \
		requirements \
		scripts \
		${PROJECTNAME}:./yt-telegram-rider

start: deploy ## Sets up a screen session on the server and start the app
	ssh ${PROJECTNAME} -C 'bash -l -c "./yt-telegram-rider/scripts/setup_bot.sh"'

ssh: ## SSH into the target VM
	ssh ${PROJECTNAME}

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