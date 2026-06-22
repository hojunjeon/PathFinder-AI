@echo off
setlocal
cd /d "%~dp0"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run-dev-servers.ps1" %*
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" if not defined RUN_DEV_NO_PAUSE (
    echo.
    echo Launcher exited with code %EXITCODE%.
    echo Press any key to close this window.
    pause >nul
)
exit /b %EXITCODE%
