@echo off
call ".venv\Scripts\activate.bat"
python kaspi_parser.py "%~1"
pause
