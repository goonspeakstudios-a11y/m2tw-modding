@echo off
rem Start EUR quick-pass. Set the shared secret once below, then double-click this file.
if "%EURMP_SECRET%"=="" set EURMP_SECRET=change-this-to-your-group-phrase
cd /d "%~dp0"
py -3 eurmp_pass.py run --config config.json
pause
