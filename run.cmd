@echo off
cd /d "%~dp0"
call venv\Scripts\activate
py gui_app.py
