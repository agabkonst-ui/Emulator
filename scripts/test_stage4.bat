@echo off
rem Stage 4: startup script for ls, cd, pwd, history, tail (with and without VFS).
echo === stage4.json ===
call "%~dp0..\run.bat" --vfs examples\vfs\stage4.json --script examples\stage4.txt
echo exit code: %errorlevel%
echo === deep.json ===
call "%~dp0..\run.bat" --vfs examples\vfs\deep.json --script examples\stage4.txt
echo exit code: %errorlevel%
echo === no VFS ===
call "%~dp0..\run.bat" --script examples\stage4.txt
echo exit code: %errorlevel%
