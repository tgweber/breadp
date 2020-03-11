init:
	pip install -r requirements.txt
test: clean
	python setup.py develop
	pytest --cov=breadp --cov-report html
clean:
	find breadp -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: init test
