@echo off
setlocal

echo === Verificando instalacion de Python...

:: Verificar si Python ya está instalado
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Python ya esta instalado.
    goto verificar_pip
)

echo ⚠️ Python no esta instalado. Descargando Python 3.10.11...

:: Ruta del instalador
set "PYTHON_INSTALLER=%TEMP%\python-3.10.11-amd64.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"

:: Descargar el instalador
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"

:: Verificar descarga
if not exist "%PYTHON_INSTALLER%" (
    echo ❌ No se pudo descargar el instalador de Python.
    goto end
)

echo ✅ Instalador descargado. Ejecutando instalacion...

:: Ejecutar el instalador en modo silencioso (modo compatible con Windows 10)
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Verificar instalación
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ La instalacion de Python fallo.
    goto end
)

echo ✅ Python 3.10 instalado correctamente.

:verificar_pip
echo === Verificando pip...
pip --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ pip ya esta instalado.
    goto end
)

echo ⚠️ pip no esta instalado. Ejecutando ensurepip...
python -m ensurepip --upgrade >nul 2>&1
python -m pip install --upgrade pip >nul 2>&1

:: Verificar pip de nuevo
pip --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ pip se instalo correctamente.
    pip install customtkinter pillow scipy numpy pyyaml soundfile rfcx-0.3.1-py3-none-any.whl
) else (
    echo ❌ pip no se pudo instalar.
)

:end
echo.
pause
endlocal