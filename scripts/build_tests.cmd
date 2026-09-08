
@echo off

echo python version
python --version

echo pip'd modules
pip list

echo -- clean-up -------------------------------------------
python .\scripts\clean.py

echo -- check building of package --------------------------
python -m build

echo -- check package meta data ----------------------------
python -m twine check dist/*
