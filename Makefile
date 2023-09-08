# First run make python
# Then run make test

test: dagger/bin/python
	dagger/bin/python main.py

python:
	nix-shell -p 'python310.withPackages(ps: with ps; [ virtualenv ])'

dagger/bin/python:
	virtualenv dagger
	dagger/bin/pip install dagger-io

