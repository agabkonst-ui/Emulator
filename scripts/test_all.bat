@echo off
rem Check both --vfs and --script together.
call "%~dp0..\run.bat" --vfs examples\vfs.json --script examples\startup.txt
