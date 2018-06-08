init:
	pip install pipenv
	pipenv install --dev
test:
	python setup.py test
