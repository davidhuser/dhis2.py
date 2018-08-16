init:
	pip install pipenv
	pipenv install --dev --skip-lock
test:
	python setup.py test
