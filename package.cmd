setlocal
cd %~dp0%
set appname=photodb
rd /s/q publish
rem mkdir /s/q publish
rem git version
for /f %%i in ('dotnet-gitversion /output json /showvariable SemVer') do set semver=%%i
rem check out the files into publish directory
git archive HEAD --format=tar --prefix=publish/%appname%/ | tar -xvf - 
rem build and copy 
pushd frontend
call npm run publish
popd
pushd publish
ren %appname% %appname%-%semver%
tar -czf %appname%-%semver%.tgz %appname%-%semver%
endlocal