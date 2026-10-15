@echo off
rem Errors: missing script, unknown and incomplete parameter.
call "%~dp0..\run.bat" --script examples\missing.txt
echo exit code: %errorlevel%
call "%~dp0..\run.bat" --unknown
echo exit code: %errorlevel%
call "%~dp0..\run.bat" --vfs
echo exit code: %errorlevel%
