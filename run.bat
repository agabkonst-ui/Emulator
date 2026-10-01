@echo off
cd /d "%~dp0"
set PYTHONPATH=src
for %%P in (python3 python py) do (
    cmd /c "%%P -c "import sys"" >nul 2>nul && (
        %%P -m shell_emulator %*
        exit /b %errorlevel%
    )
)
if exist "C:\msys64\ucrt64\bin\python.exe" (
    "C:\msys64\ucrt64\bin\python.exe" -m shell_emulator %*
    exit /b %errorlevel%
)
echo Python not found. Install Python 3.8+ and retry.
exit /b 1