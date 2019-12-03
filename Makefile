init:
	pip install -r requirements.txt
test:
	python setup.py develop
	pytest --cov=breadp --cov-report html

.PHONY: init test
