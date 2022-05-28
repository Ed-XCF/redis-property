init:
	python3 -m venv venv
	. venv/bin/activate \
	&& pip3 install wheel \
	&& pip3 install -r requirements-dev.txt

test:
	coverage run -m pytest

release:
	pip3 install -r requirements.txt

build:
	python3 setup.py sdist bdist_wheel

pypi:
	twine upload dist/*
