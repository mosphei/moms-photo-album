cd %~0dp%
call npm run build
robocopy /s /purge build\* ..\app\static