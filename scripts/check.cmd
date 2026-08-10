
@echo off

echo -- black -----------------------------------------
python -m black .

echo -- ruf -------------------------------------------
python -m ruff check .

echo -- pyright ---------------------------------------
python -m pyright .