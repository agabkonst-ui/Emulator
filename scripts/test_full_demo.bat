@echo off
rem Full startup script: with VFS, with another VFS, without VFS.
echo === deep.json ===
call "%~dp0..\run.bat" --vfs examples\vfs\deep.json --script examples\full_demo.txt
echo === several.json ===
call "%~dp0..\run.bat" --vfs examples\vfs\several.json --script examples\full_demo.txt
echo === no VFS ===
call "%~dp0..\run.bat" --script examples\full_demo.txt
