@echo off
setlocal
REM Descobre o diretório do .bat
set "scriptDir=%~dp0"
REM Caminho para o main.py
set "mainPy=%scriptDir%TratarDadosPlotSurface\main.py"
if exist "%mainPy%" (
    start "" /b python "%mainPy%"
) else (
    msg * "main.py não encontrado em %mainPy%"
)
endlocal
