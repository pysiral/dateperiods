init:
	pip install -e .[dev]

test:
	python -m unittest discover -s tests -t tests