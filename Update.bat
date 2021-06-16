@echo off
set /p var=Commit: 
echo %var%
git add .
git commit -m "%var%"
git push -u origin main
pause