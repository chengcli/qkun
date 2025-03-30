# If you have never updated your
# MUST use virtualenv
python3 -m venv .venv

# lat range + lon range
# long range + lat range

# brew
brew install hdf5

# how to test
python -m pip install -e .

# How to deploy
python -m build
python -m twine upload dist/*

# install with test
pip install -e .
