cd src
rm -rf dist
python setup.py sdist
python setup.py bdist_wheel --universal
twine --version
ls -la
twine upload dist/*

