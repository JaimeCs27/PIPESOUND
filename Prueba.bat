@echo off
setlocal

:: Verificar si Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Python ya esta instalado.
) else (
    echo ⚠️ Python no esta instalado. Descargando e instalando...

    set "PYTHON_INSTALLER=%TEMP%\python_installer.exe"

    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe -OutFile '%PYTHON_INSTALLER%'"

    %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    :: Verificar instalación de Python
    python --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ La instalacion de Python fallo.
        goto end
    ) else (
        echo ✅ Python fue instalado correctamente.
    )
)

:: Verificar si pip funciona
pip --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ pip ya esta instalado.
) else (
    echo ⚠️ pip no esta funcionando. Intentando reinstalar con ensurepip...
    python -m ensurepip --upgrade >nul 2>&1
    python -m pip install --upgrade pip >nul 2>&1
)

:: Verificar nuevamente
pip --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ pip esta funcionando correctamente.
    pip install customtkinter pillow scipy numpy pyyaml soundfile rfcx-0.3.1-py3-none-any.whl
    
) else (
    echo ❌ pip no se pudo instalar o no funciona.
)

:end
endlocal
pause