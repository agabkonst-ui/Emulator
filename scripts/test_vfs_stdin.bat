@echo off
rem VFS variants (minimal, several files, 3+ levels) via stdin.
echo === VFS: minimal ===
call "%~dp0..\run.bat" --vfs examples\vfs\minimal.json < examples\vfs_check.txt
echo === VFS: several ===
call "%~dp0..\run.bat" --vfs examples\vfs\several.json < examples\vfs_check.txt
echo === VFS: deep ===
call "%~dp0..\run.bat" --vfs examples\vfs\deep.json < examples\vfs_check.txt
