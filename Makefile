.PHONY: mypy ruff style style-check test lint pytest sync

package?=ktx tests

all: sync style test

style:
	ruff format $(package)
	ruff check --select I --fix $(package)

mypy:
	mypy --enable-error-code ignore-without-code $(package)

ruff:
	ruff check $(package)

style-check:
	ruff format --check --diff $(package)

deptry:
	deptry . -e 'env|\.env|venv|\.venv|\..+'

lint: style-check ruff mypy deptry

pytest:
	pytest .

test: lint pytest

sync:
	uv sync --all-extras
