@echo off
setlocal
call "%~dp0..\run.bat" --vfs examples/vfs/stage5.json --script examples/stage5.txt
exit /b %errorlevel%
