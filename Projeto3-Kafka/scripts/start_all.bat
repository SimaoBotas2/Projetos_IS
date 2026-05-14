@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "APP_DIR=%ROOT_DIR%..\api\"
for %%I in ("%ROOT_DIR%..\.venv\Scripts\python.exe") do set "PYTHON_EXE=%%~fI"

if not exist "%APP_DIR%" (
    echo [ERROR] Pasta do projeto nao encontrada: "%APP_DIR%"
    pause
    exit /b 1
)

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python da virtual environment nao foi encontrado.
    echo Esperado em: "%PYTHON_EXE%"
    pause
    exit /b 1
)

echo A iniciar os 3 servicos do projeto...

start "Library REST API" cmd /k "cd /d "%APP_DIR%" && "%PYTHON_EXE%" main.py"
timeout /t 2 /nobreak >nul

start "Library MCP Server" cmd /k "cd /d "%APP_DIR%" && "%PYTHON_EXE%" mcp_server.py"
timeout /t 2 /nobreak >nul

start "Library Agent API" cmd /k "cd /d "%APP_DIR%" && "%PYTHON_EXE%" langchain_agent.py"
timeout /t 5 /nobreak >nul

start "Library Web App" "%APP_DIR%webapp.html"

echo.
echo ================= ESTADO CONSOLIDADO ================
call :check_http "REST API" "http://127.0.0.1:8001/" "Get"
call :check_http "MCP SSE" "http://127.0.0.1:8002/sse" "Head"
call :check_http "Agent API" "http://127.0.0.1:8000/health" "Get"
echo ====================================================
echo Enderecos:
echo - REST API:  http://127.0.0.1:8001
echo - MCP SSE:   http://127.0.0.1:8002/sse
echo - Agent API: http://127.0.0.1:8000
echo.
echo A webapp foi aberta no browser por defeito.
pause
goto :eof

:check_http
set "SERVICE_NAME=%~1"
set "SERVICE_URL=%~2"
set "METHOD=%~3"
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { $r = Invoke-WebRequest -Uri '%SERVICE_URL%' -Method %METHOD% -UseBasicParsing -TimeoutSec 5; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 400) { exit 0 } else { exit 1 } } catch { exit 1 }"
if errorlevel 1 (
    echo [FAIL] %SERVICE_NAME% nao respondeu em %SERVICE_URL%
) else (
    echo [OK]   %SERVICE_NAME% ativo em %SERVICE_URL%
)
exit /b 0
