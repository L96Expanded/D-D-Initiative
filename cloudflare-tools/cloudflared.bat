@echo off
REM Cloudflared wrapper script for easy access

REM Add the cloudflare-tools directory to PATH for this session
set PATH=%~dp0cloudflare-tools;%PATH%

REM Run cloudflared with all passed arguments
%~dp0cloudflare-tools\cloudflared.exe %*