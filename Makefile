PORT?=8008
LASTTAG = $(shell git describe --tags --abbrev=0)

# if the command is only `make`, the default tasks will be the printing of the help.
.DEFAULT_GOAL := help

.PHONY: help
help: ## List all make commands available
	@grep -E '^[\.a-zA-Z_%-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk -F ":" '{print $1}' | grep -v % | sed 's/\\//g' | sort | awk 'BEGIN {FS = ":[^:]*?##"}; {printf "\033[1;34mmake %-50s\033[0m %s\n", $$1, $$2}'

# ===================================================================
# Virtualenv
# ===================================================================

venv-python: venv-min-python venv-dev-python ## Install all Python 3 venv

venv: venv-min venv-dev ## Install all Python 3 dependencies

venv-upgrade: venv-min-upgrade venv-dev-upgrade ## Upgrade all Python 3 dependencies

# For minimal installation (without optional dependencies)

venv-min-python: ## Install Python 3 venv minimal
	virtualenv -p /usr/bin/python3 venv-min

venv-min: venv-min-python ## Install Python 3 minimal run-time dependencies
	./venv-min/bin/pip install -r requirements.txt

venv-min-upgrade: ## Upgrade Python 3 minimal run-time dependencies
	./venv-min/bin/pip install --upgrade pip
	./venv-min/bin/pip install --upgrade -r requirements.txt

# For development

venv-dev-python: ## Install Python 3 venv
	virtualenv -p /usr/bin/python3 venv-dev

venv-dev: venv-python ## Install Python 3 dev dependencies
	./venv-dev/bin/pip install -r dev-requirements.txt
	./venv-dev/bin/pip install -r doc-requirements.txt

venv-dev-upgrade: ## Upgrade Python 3 dev dependencies
	./venv-dev/bin/pip install --upgrade pip
	./venv-dev/bin/pip install --upgrade -r dev-requirements.txt
	./venv-dev/bin/pip install --upgrade -r doc-requirements.txt

# ===================================================================
# Tests
# ===================================================================

test: ## Run unit tests
	./venv/bin/python ./unitest.py
	./venv/bin/python -m black ./klances --check

test-with-upgrade: venv-upgrade venv-dev-upgrade ## Upgrade deps and run unit tests
	./venv/bin/python ./unitest.py
	./venv/bin/python -m black ./klances --check

test-min: ## Run unit tests in minimal environment
	./venv-min/bin/python ./unitest.py

test-min-with-upgrade: venv-min-upgrade ## Upgrade deps and run unit tests in minimal environment
	./venv-min/bin/python ./unitest.py

# ===================================================================
# Linters and profilers
# ===================================================================

format: ## Format the code
	@git ls-files 'klances/*.py' | xargs ./venv-dev/bin/python -m autopep8 --in-place --jobs 0 --global-config=.flake8
	@git ls-files 'klances/*.py' | xargs ./venv-dev/bin/python -m autoflake --in-place --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --exclude="compat.py,globals.py"
	./venv-dev/bin/python -m black ./klances --exclude outputs/static

flake8: ## Run flake8 linter.
	@git ls-files 'klances/ *.py' | xargs ./venv-dev/bin/python -m flake8 --config=.flake8

ruff: ## Run Ruff (fastest) linter.
	./venv-dev/bin/python -m ruff check . --config=./pyproject.toml

codespell: ## Run codespell to fix common misspellings in text files
	./venv-dev/bin/codespell -S .git,./docs/_build,./klances.egg-info,./venv*,./klances/outputs,*.svg -L hart,bu,te,statics

semgrep: ## Run semgrep to find bugs and enforce code standards
	./venv-dev/bin/semgrep --config=auto --lang python --use-git-ignore ./klances

profiling: ## How to start the profiling of the klances software
	@echo "Please complete and run: sudo ./venv-dev/bin/py-spy record -o ./docs/_static/klances-flame.svg -d 60 -s --pid <klances PID>"

trace-malloc: ## Trace the malloc() calls
	@echo "Malloc test is running, please wait ~30 secondes..."
	./venv/bin/python -m klances -C ./conf/klances.conf --trace-malloc --stop-after 15 --quiet

memory-leak: ## Profile memory leaks
	./venv/bin/python -m klances -C ./conf/klances.conf --memory-leak

memory-profiling: ## Profile memory usage
	@echo "It's a very long test (~4 hours)..."
	rm -f mprofile_*.dat
	@echo "1/2 - Start memory profiling with the history option enable"
	./venv-dev/bin/mprof run -T 1 -C run.py -C ./conf/klances.conf --stop-after 2400 --quiet
	./venv-dev/bin/mprof plot --output ./docs/_static/klances-memory-profiling-with-history.png
	rm -f mprofile_*.dat
	@echo "2/2 - Start memory profiling with the history option disable"
	./venv-dev/bin/mprof run -T 1 -C run.py -C ./conf/klances.conf --disable-history --stop-after 2400 --quiet
	./venv-dev/bin/mprof plot --output ./docs/_static/klances-memory-profiling-without-history.png
	rm -f mprofile_*.dat

# ===================================================================
# Docs
# ===================================================================

docs: ## Create the documentation
	./venv/bin/python -m klances -C ./conf/klances.conf --api-doc > ./docs/api.rst
	cd docs && ./build.sh && cd ..

docs-server: docs ## Start a Web server to serve the documentation
	(sleep 2 && sensible-browser "http://localhost:$(PORT)") &
	cd docs/_build/html/ && ../../../venv/bin/python -m http.server $(PORT)

release-note: ## Generate release note
	git --no-pager log $(LASTTAG)..HEAD --first-parent --pretty=format:"* %s"
	@echo "\n"
	git --no-pager shortlog -s -n $(LASTTAG)..HEAD

install: ## Open a Web Browser to the installation procedure
	sensible-browser "https://github.com/nicolargo/klances#installation"

# ===================================================================
# Packaging
# ===================================================================

flatpak: venv-dev-upgrade ## Generate FlatPack JSON file
	git clone https://github.com/flatpak/flatpak-builder-tools.git
	./venv/bin/python ./flatpak-builder-tools/pip/flatpak-pip-generator klances
	rm -rf ./flatpak-builder-tools
	@echo "Now follow: https://github.com/flathub/flathub/wiki/App-Submission"

# ===================================================================
# Docker
# ===================================================================

docker: docker-alpine

docker-alpine: ## Generate local docker images (Alpine)
	docker build --target full -f ./docker-files/alpine.Dockerfile -t klances:local-alpine-full .
	docker build --target minimal -f ./docker-files/alpine.Dockerfile -t klances:local-alpine-minimal .
	docker build --target dev -f ./docker-files/alpine.Dockerfile -t klances:local-alpine-dev .

# ===================================================================
# Run
# ===================================================================

run: ## Start klances in console mode (also called standalone)
	./venv/bin/python -m klances -C ./conf/klances.conf

run-debug: ## Start klances in debug console mode (also called standalone)
	./venv/bin/python -m klances -C ./conf/klances.conf -d

run-local-conf: ## Start klances in console mode with the system conf file
	./venv/bin/python -m klances

run-min: ## Start minimal klances in console mode (also called standalone)
	./venv-min/bin/python -m klances -C ./conf/klances.conf

run-min-debug: ## Start minimal klances in debug console mode (also called standalone)
	./venv-min/bin/python -m klances -C ./conf/klances.conf -d

run-min-local-conf: ## Start minimal klances in console mode with the system conf file
	./venv-min/bin/python -m klances

run-docker-alpine-minimal: ## Start klances Alpine Docker minimal in console mode
	docker run --rm -e TZ="${TZ}" -e klances_OPT="" -v /run/user/1000/podman/podman.sock:/run/user/1000/podman/podman.sock:ro -v /var/run/docker.sock:/var/run/docker.sock:ro --pid host --network host -it klances:local-alpine-minimal

run-docker-alpine-full: ## Start klances Alpine Docker full in console mode
	docker run --rm -e TZ="${TZ}" -e klances_OPT="" -v /run/user/1000/podman/podman.sock:/run/user/1000/podman/podman.sock:ro -v /var/run/docker.sock:/var/run/docker.sock:ro --pid host --network host -it klances:local-alpine-full

run-docker-alpine-dev: ## Start klances Alpine Docker dev in console mode
	docker run --rm -e TZ="${TZ}" -e klances_OPT="" -v /run/user/1000/podman/podman.sock:/run/user/1000/podman/podman.sock:ro -v /var/run/docker.sock:/var/run/docker.sock:ro --pid host --network host -it klances:local-alpine-dev

show-version: ## Show klances version number
	./venv/bin/python -m klances -C ./conf/klances.conf -V

.PHONY: test docs docs-server venv venv-min venv-dev
