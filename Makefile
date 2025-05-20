test:
	pytest --tb=short

watch-tests:
	ls *.py | entr pytest --tb=short

black:
	black $$(find * -name '*.py')

isort:
	isort .