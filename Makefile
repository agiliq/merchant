.PHONY: check-ver

all: init test

init:
	pip install -e .
	pip install -r example/requirements.txt

test: init
	python example/manage.py test billing

release: check-ver
	@echo ${VER}
	sed -i "s/^VERSION = .*/VERSION = '${VER}'/g" setup.py
	git add setup.py
	git commit -m "version bump"
	git tag v${VER}
	git push --tags
	python setup.py sdist upload

check-ver:
ifndef VER
	$(error VER is undefined)
endif
