@echo off
REM 1) 가상환경 활성화
call "%~dp0\bin\eclass-venv\Scripts\activate.bat"

REM 2) 스크립트 실행
python "%~dp0\bin\eclass_downloader.py"

REM 3) 종료 전 대기
pause
