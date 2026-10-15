@echo off
cd /d "%~dp0"
set PYTHONPATH=src
set PYTHONUTF8=1
set "PY="
for %%P in (python3 python py) do if not defined PY (
    cmd /c "%%P -c "import sys"" >nul 2>nul && set "PY=%%P"
)
if not defined PY if exist "C:\msys64\ucrt64\bin\python.exe" (
    set "PY=C:\msys64\ucrt64\bin\python.exe"
)
if not defined PY (
    echo Python not found. Install Python 3.8+ and retry.
    exit /b 1
)
"%PY%" -m shell_emulator %*
exit /b %errorlevel%
