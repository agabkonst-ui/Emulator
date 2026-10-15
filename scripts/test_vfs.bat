@echo off
rem Check --vfs: the path is shown in the debug output.
call "%~dp0..\run.bat" --vfs examples\vfs.json < NUL
