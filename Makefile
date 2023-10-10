###############################################################################
# Common make values.
lib    := textual_astview
run    := pipenv run
python := $(run) python
build  := $(python) -m build
lint   := $(run) pylint
mypy   := $(run) mypy
twine  := $(run) twine
vermin := $(run) vermin -v --no-parse-comments --backport dataclasses --backport typing --backport argparse --eval-annotations
black  := $(run) black

##############################################################################
# Run the app.
.PHONY: run
run:				# Run the app.
	$(python) -m $(lib) $(lib)/widgets/astview.py

.PHONY: debug
debug:				# Run the app in debug mode (for the console)
	TEXTUAL=devtools make

.PHONY: console
console:			# Run up the Textual development console.
	$(run) textual console

##############################################################################
# Setup/update packages the system requires.
.PHONY: setup
setup:				# Install all dependencies
	pipenv sync --dev
	$(run) pre-commit install

.PHONY: resetup
resetup:			# Recreate the virtual environment from scratch
	rm -rf $(shell pipenv --venv)
	pipenv sync --dev

.PHONY: depsoutdated
depsoutdated:			# Show a list of outdated dependencies
	pipenv update --outdated

.PHONY: depsupdate
depsupdate:			# Update all dependencies
	pipenv update --dev

.PHONY: depsshow
depsshow:			# Show the dependency graph
	pipenv graph

##############################################################################
# Checking/testing/linting/etc.
.PHONY: lint
lint:				# Run Pylint over the library
	$(lint) $(lib)

.PHONY: typecheck
typecheck:			# Perform static type checks with mypy
	$(mypy) --scripts-are-modules $(lib)

.PHONY: stricttypecheck
stricttypecheck:	        # Perform a strict static type checks with mypy
	$(mypy) --scripts-are-modules --strict $(lib)

.PHONY: minpy
minpy:				# Check the minimum supported Python version
	$(vermin) $(lib)

.PHONY: checkall
checkall: lint stricttypecheck # Check all the things

##############################################################################
# Package/publish.
.PHONY: package
package:			# Package the library
	$(build)

.PHONY: spackage
spackage:			# Create a source package for the library
	$(build) --sdist

.PHONY: packagecheck
packagecheck: package		# Check the packaging.
	$(twine) check dist/*

.PHONY: testdist
testdist: packagecheck		# Perform a test distribution
	$(twine) upload --skip-existing --repository testpypi dist/*

.PHONY: dist
dist: packagecheck		# Upload to pypi
	$(twine) upload --skip-existing dist/*

##############################################################################
# Utility.
.PHONY: ugly
ugly:				# Reformat the code with black.
	$(black) $(lib)

.PHONY: repl
repl:				# Start a Python REPL
	$(python)

.PHONY: clean
clean:				# Clean the build directories
	rm -rf build dist $(lib).egg-info

.PHONY: help
help:				# Display this help
	@grep -Eh "^[a-z]+:.+# " $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.+# "}; {printf "%-20s %s\n", $$1, $$2}'

##############################################################################
# Housekeeping tasks.
.PHONY: housekeeping
housekeeping:			# Perform some git housekeeping
	git fsck
	git gc --aggressive
	git remote update --prune

### Makefile ends here
