@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

rem =============================================================================
rem build.bat - Biesse2Csv
rem Buildt PyInstaller onedir, signeert EXE, maakt Inno Setup installer
rem en signeert daarna ook de installer.
rem =============================================================================

set "PROJECT_NAME=Biesse2Csv"
set "SPEC_FILE=Biesse2Csv.spec"
set "DST_FOLDER=dist"
set "LOGFILE=build_log.txt"
set "VERSION_FILE=app\version.py"
set "ISS_FILE=installer\Biesse2Csv_setup.iss"
set "TIMESTAMP_URL=http://timestamp.digicert.com"
set "SIGN_SUBJECT="

rem ---- Python detecteren ----
set "PYEXE=python"
if exist "venv\Scripts\python.exe"  set "PYEXE=%~dp0venv\Scripts\python.exe"
if exist ".venv\Scripts\python.exe" set "PYEXE=%~dp0.venv\Scripts\python.exe"
if exist "Scripts\python.exe"       set "PYEXE=%~dp0Scripts\python.exe"

echo [info] Python: %PYEXE%
"%PYEXE%" -V >nul 2>&1
if not errorlevel 1 goto PYTHON_OK
echo [FOUT] Geen werkende Python gevonden.
goto FAIL

:PYTHON_OK

rem =============================================================================
rem [S0] Signing
rem =============================================================================
set "DO_SIGN=N"
if defined B2C_DO_SIGN set "DO_SIGN=%B2C_DO_SIGN%"
if defined B2C_DO_SIGN echo [sign] Modus via parameter: %B2C_DO_SIGN%
if defined B2C_DO_SIGN goto SIGN_PARAM_SET

set /p DO_SIGN=[S0] Binaries signen? [J/N] - standaard N:
if not defined DO_SIGN set "DO_SIGN=N"

:SIGN_PARAM_SET

set "SIGNTOOL_EXE="
if /I "%DO_SIGN%"=="J" call :FIND_SIGNTOOL

if /I "%DO_SIGN%"=="J" if not defined SIGNTOOL_EXE (
    echo [WAARSCHUWING] signtool.exe niet gevonden. Signing overgeslagen.
    set "DO_SIGN=N"
)

if /I "%DO_SIGN%"=="J" if defined SIGNTOOL_EXE (
    echo [sign] signtool: !SIGNTOOL_EXE!
    if defined SIGN_SUBJECT (
        echo [sign] Certificaatselectie: subject "%SIGN_SUBJECT%"
    ) else (
        echo [sign] Certificaatselectie: automatisch /a
    )
)

rem =============================================================================
rem [0] Versie verhogen
rem =============================================================================
if defined B2C_BUMP_PART (
    set "PART_TO_BUMP=%B2C_BUMP_PART%"
    echo [0] Versie-bump via parameter: %B2C_BUMP_PART%
) else (
    set "PART_TO_BUMP=patch"
    set /p PART_TO_BUMP=[0] Versie verhogen? [patch/minor/major] - Enter=patch:
    if not defined PART_TO_BUMP set "PART_TO_BUMP=patch"
)

echo [0] bump_version.py uitvoeren (%PART_TO_BUMP%)...
"%PYEXE%" bump_version.py %PART_TO_BUMP%
if errorlevel 1 (
    echo [FOUT] Versieverhoging mislukt.
    goto FAIL
)

rem =============================================================================
rem [1] Versie uitlezen
rem =============================================================================
set "VER_TXT=%TEMP%\__b2c_version.txt"
del /q "%VER_TXT%" >nul 2>&1

"%PYEXE%" read_version.py "%VER_TXT%"
if errorlevel 1 (
    echo [FOUT] Versie uitlezen mislukt.
    goto FAIL
)

set "NEW_VERSION="
set /p NEW_VERSION=<"%VER_TXT%"
del /q "%VER_TXT%" >nul 2>&1

if not defined NEW_VERSION (
    echo [FOUT] Kon versie niet lezen.
    goto FAIL
)

echo [1] Versie: %NEW_VERSION%

set "BUILD_FOLDER=%PROJECT_NAME%_%NEW_VERSION%"
set "INITIAL_EXE=%DST_FOLDER%\%PROJECT_NAME%\%PROJECT_NAME%.exe"
set "FINAL_APP_EXE=%DST_FOLDER%\%BUILD_FOLDER%\%PROJECT_NAME%.exe"
set "SETUP_EXE=%DST_FOLDER%\%PROJECT_NAME%_setup_%NEW_VERSION%.exe"

rem =============================================================================
rem [2] Opschonen
rem =============================================================================
echo [2] Opruimen...
rmdir /s /q build >nul 2>&1
rmdir /s /q "%DST_FOLDER%" >nul 2>&1
del /q "%LOGFILE%" >nul 2>&1
echo --- Build gestart op %DATE% %TIME% --- >> "%LOGFILE%"

rem =============================================================================
rem [3] pip + requirements
rem =============================================================================
echo [3] pip en requirements...

if exist requirements.txt (
    "%PYEXE%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [FOUT] pip install -r requirements.txt faalde.
        goto FAIL
    )
)

if exist requirements-build.txt (
    "%PYEXE%" -m pip install -r requirements-build.txt
    if errorlevel 1 (
        echo [FOUT] pip install -r requirements-build.txt faalde.
        goto FAIL
    )
) else (
    "%PYEXE%" -c "import PyInstaller" >nul 2>&1
    if errorlevel 1 (
        echo [3b] PyInstaller installeren...
        "%PYEXE%" -m pip install "pyinstaller>=6.0" "pyinstaller-hooks-contrib>=2025.0"
        if errorlevel 1 (
            echo [FOUT] PyInstaller installatie mislukt.
            goto FAIL
        )
    )
)

"%PYEXE%" -m pip check
if errorlevel 1 echo [WAARSCHUWING] pip check rapporteert problemen.

rem =============================================================================
rem [4] PyInstaller build
rem =============================================================================
echo [4] PyInstaller bouwen...
"%PYEXE%" -m PyInstaller --clean --noconfirm "%SPEC_FILE%" >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo [FOUT] PyInstaller build mislukt. Zie %LOGFILE%.
    goto FAIL
)

if not exist "%INITIAL_EXE%" (
    echo [FOUT] EXE niet gevonden: %INITIAL_EXE%
    goto FAIL
)

echo [OK] Build geslaagd.

rem =============================================================================
rem [4b] EXE signen + verifieren
rem =============================================================================
if /I "%DO_SIGN%"=="J" (
    echo [4b] EXE signen...
    call :SIGN_FILE "%INITIAL_EXE%"
    if errorlevel 1 (
        echo [FOUT] EXE signen mislukt.
        goto FAIL
    )

    call :VERIFY_FILE "%INITIAL_EXE%"
    if errorlevel 1 (
        echo [FOUT] EXE signature-verificatie mislukt.
        goto FAIL
    )
)

rem =============================================================================
rem [5] Map hernoemen
rem =============================================================================
echo [5] Hernoemen naar %BUILD_FOLDER%...

if exist "%DST_FOLDER%\%BUILD_FOLDER%" (
    rmdir /S /Q "%DST_FOLDER%\%BUILD_FOLDER%"
)

rename "%DST_FOLDER%\%PROJECT_NAME%" "%BUILD_FOLDER%" >nul 2>&1

if errorlevel 1 (
    echo [5] Fallback via robocopy...
    robocopy "%DST_FOLDER%\%PROJECT_NAME%" "%DST_FOLDER%\%BUILD_FOLDER%" /E /MOVE >nul

    if errorlevel 8 (
        echo [FOUT] Hernoemen mislukt.
        goto FAIL
    )
)

if not exist "%FINAL_APP_EXE%" (
    echo [FOUT] EXE ontbreekt na hernoemen.
    goto FAIL
)

echo %NEW_VERSION% > "%DST_FOLDER%\%BUILD_FOLDER%\version.txt"

rem =============================================================================
rem [6] Inno Setup
rem =============================================================================
if defined B2C_MAKE_INSTALLER (
    set "MAKE_INSTALLER=%B2C_MAKE_INSTALLER%"
    echo [6] Installer via parameter: %B2C_MAKE_INSTALLER%
) else (
    set "MAKE_INSTALLER=J"
    set /p MAKE_INSTALLER=[6] Installer bouwen? [J/N] - Enter=J:
    if not defined MAKE_INSTALLER set "MAKE_INSTALLER=J"
)

if /I not "%MAKE_INSTALLER%"=="J" goto INSTALLER_SKIP

set "ISCC_EXE="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe"       set "ISCC_EXE=C:\Program Files\Inno Setup 6\ISCC.exe"

if not defined ISCC_EXE (
    echo [WAARSCHUWING] ISCC.exe niet gevonden. Installer overgeslagen.
    goto INSTALLER_SKIP
)

echo [6] Inno Setup compileren...
"%ISCC_EXE%" /DMyAppVersion=%NEW_VERSION% /DMySourceDir="..\dist\%BUILD_FOLDER%" "%ISS_FILE%"

if errorlevel 1 (
    echo [FOUT] Inno Setup mislukt.
    goto FAIL
)

if exist "%SETUP_EXE%" (
    echo [OK] Installer: %SETUP_EXE%
) else (
    echo [FOUT] Installer niet gevonden na compile: %SETUP_EXE%
    goto FAIL
)

rem =============================================================================
rem [7] Installer signen + verifieren
rem =============================================================================
if /I "%DO_SIGN%"=="J" (
    echo [7] Installer signen...
    call :SIGN_FILE "%SETUP_EXE%"
    if errorlevel 1 (
        echo [FOUT] Installer signen mislukt.
        goto FAIL
    )

    call :VERIFY_FILE "%SETUP_EXE%"
    if errorlevel 1 (
        echo [FOUT] Installer signature-verificatie mislukt.
        goto FAIL
    )
)

:INSTALLER_SKIP

echo.
echo =============================================================================
echo [OK] Build voltooid - Biesse2Csv %NEW_VERSION%
echo =============================================================================
echo   App:       %FINAL_APP_EXE%
echo   Installer: %SETUP_EXE%
echo   Signing:   %DO_SIGN%
echo =============================================================================
echo.
endlocal
exit /b 0

:FAIL
echo.
echo =============================================================================
echo [FOUT] Build afgebroken.
echo =============================================================================
endlocal
exit /b 1


rem =============================================================================
rem SignTool zoeken
rem =============================================================================
:FIND_SIGNTOOL
set "SIGNTOOL_EXE="
set "SIGNTOOL_TXT=%TEMP%\__b2c_signtool.txt"

del /q "%SIGNTOOL_TXT%" >nul 2>&1

"%PYEXE%" find_signtool.py "%SIGNTOOL_TXT%"
if errorlevel 1 (
    goto :eof
)

if not exist "%SIGNTOOL_TXT%" (
    goto :eof
)

set /p SIGNTOOL_EXE=<"%SIGNTOOL_TXT%"
del /q "%SIGNTOOL_TXT%" >nul 2>&1

goto :eof


rem =============================================================================
rem Bestand signen
rem =============================================================================
:SIGN_FILE
if not exist "%~1" (
    echo [FOUT] Bestand niet gevonden: %~1
    exit /b 1
)

if not defined SIGNTOOL_EXE (
    echo [FOUT] signtool niet geconfigureerd.
    exit /b 1
)

echo [sign] Bestand: %~1

if defined SIGN_SUBJECT (
    "!SIGNTOOL_EXE!" sign /fd SHA256 /td SHA256 /tr "%TIMESTAMP_URL%" /n "%SIGN_SUBJECT%" "%~1"
) else (
    "!SIGNTOOL_EXE!" sign /fd SHA256 /td SHA256 /tr "%TIMESTAMP_URL%" /a "%~1"
)

if errorlevel 1 exit /b 1

echo [OK] Gesigned: %~1
exit /b 0


rem =============================================================================
rem Signature verifieren
rem =============================================================================
:VERIFY_FILE
echo [sign] Verifieren: %~1
"!SIGNTOOL_EXE!" verify /pa /v "%~1"
if errorlevel 1 exit /b 1

echo [OK] Signature geldig: %~1
exit /b 0
