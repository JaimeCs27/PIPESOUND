@echo off
setlocal

echo === Verificando si Python ya está instalado...

:: Verificar si python está en PATH
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python ya está instalado.
    goto verificar_pip
)

echo ⚠️ Python no está instalado. Descargando instalador de Python 3.10.11...

:: Configurar variables
set "PYTHON_INSTALLER=%TEMP%\python-3.10.11-amd64.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
set "PYTHON_PATH=%ProgramFiles%\Python310\python.exe"
set "PIP_PATH=%ProgramFiles%\Python310\Scripts\pip.exe"

:: Descargar el instalador
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"

:: Verificar que se haya descargado
if not exist "%PYTHON_INSTALLER%" (
    echo No se pudo descargar el instalador.
    goto end
)

echo Instalador descargado. Ejecutando instalación...

:: Ejecutar instalación en modo silencioso (sintaxis compatible con Windows 10)
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Esperar unos segundos para que se complete
timeout /t 5 >nul

:: Verificar Python por ruta directa
if exist "%PYTHON_PATH%" (
    echo Python se instaló correctamente en: %PYTHON_PATH%
) else (
    echo No se encontró Python en la ruta esperada.
    goto end
)

:: Mostrar versión
"%PYTHON_PATH%" --version

:verificar_pip
echo === Verificando pip...

:: Primero intentamos desde el PATH actual
pip --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo pip ya está disponible globalmente.
    py -3.10 -m pip install customtkinter pillow scipy numpy pyyaml soundfile matplotlib seaborn librosa psutil requests_toolbelt httplib2 birdnetlib
    goto end
)

:: Si no está, intentamos desde ruta directa
if exist "%PIP_PATH%" (
    echo pip está disponible en: %PIP_PATH%
    "%PIP_PATH%" --version
    py -3.10 -m pip install customtkinter pillow scipy numpy pyyaml soundfile matplotlib seaborn librosa psutil requests_toolbelt httplib2 birdnetlib
    goto end
)

:: Si aún no está, intentar instalarlo manualmente con ensurepip
echo ⚠️ pip no está instalado. Intentando instalar...
"%PYTHON_PATH%" -m ensurepip --upgrade >nul 2>&1
"%PYTHON_PATH%" -m pip install --upgrade pip >nul 2>&1

:: Verificar de nuevo
if exist "%PIP_PATH%" (
    echo pip fue instalado exitosamente.
    "%PIP_PATH%" --version
    py -3.10 -m pip install customtkinter pillow scipy numpy pyyaml soundfile matplotlib seaborn librosa psutil requests_toolbelt httplib2 birdnetlib birdnet
) else (
    echo pip no se pudo instalar.
)

:end
echo.
pause
endlocal