
@echo off

echo python version
python --version

echo pip'd modules
pip list

echo -- clean-up -------------------------------------------
python .\scripts\clean.py

@REM - run linter and format checker - both with auto fix
echo -- ruff -----------------------------------------------
python -m ruff check . --fix
python -m ruff format .

@REM - run python type checker
echo -- pyright --------------------------------------------
python -m pyright .

@REM - run tests and print coverage
echo -- coverage -------------------------------------------
python -m pytest --cov=official_cheater --cov-report=term-missing .