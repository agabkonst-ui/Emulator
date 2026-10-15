@echo off
rem VFS variants (minimal, several files, 3+ levels) via --script.
echo === VFS: minimal ===
call "%~dp0..\run.bat" --vfs examples\vfs\minimal.json --script examples\vfs_check.txt
echo === VFS: several ===
call "%~dp0..\run.bat" --vfs examples\vfs\several.json --script examples\vfs_check.txt
echo === VFS: deep ===
call "%~dp0..\run.bat" --vfs examples\vfs\deep.json --script examples\vfs_check.txt
