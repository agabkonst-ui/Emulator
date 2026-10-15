@echo off
rem VFS load errors: missing file, bad format, not a file.
echo === VFS: missing.json ===
call "%~dp0..\run.bat" --vfs examples\vfs\missing.json < NUL
echo exit code: %errorlevel%
echo === VFS: bad_json.json ===
call "%~dp0..\run.bat" --vfs examples\vfs\bad_json.json < NUL
echo exit code: %errorlevel%
echo === VFS: bad_type.json ===
call "%~dp0..\run.bat" --vfs examples\vfs\bad_type.json < NUL
echo exit code: %errorlevel%
echo === VFS: bad_base64.json ===
call "%~dp0..\run.bat" --vfs examples\vfs\bad_base64.json < NUL
echo exit code: %errorlevel%
echo === VFS: bad_root.json ===
call "%~dp0..\run.bat" --vfs examples\vfs\bad_root.json < NUL
echo exit code: %errorlevel%
echo === VFS: directory instead of file ===
call "%~dp0..\run.bat" --vfs examples < NUL
echo exit code: %errorlevel%
