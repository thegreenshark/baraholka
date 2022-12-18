::password test1234
@echo off
chcp 1251
PATH C:\Program Files\PostgreSQL\15\bin;%PATH%
if not exist "%APPDATA%\postgresql" md "%APPDATA%\postgresql"
psql.exe -h localhost -U "baraholkaapp" -d baraholka -p 5432
pause