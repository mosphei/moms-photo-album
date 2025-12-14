cd %~0dp%
call npm run build
xcopy /s/d/y build\* ..\app\static