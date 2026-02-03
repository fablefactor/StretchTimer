@echo off
setlocal EnableDelayedExpansion

:: ============================================
:: Stretch Timer - Windows Deployment Script
:: Creates StretchTimer-Windows.zip for distribution
:: ============================================

title Stretch Timer - Deploy

echo.
echo ========================================
echo   Stretch Timer Deployment Script
echo ========================================
echo.

:: Get script directory and change to it
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%" || (
    echo ERROR: Cannot access script directory: %SCRIPT_DIR%
    goto :error
)

:: Configuration
set "DIST_FOLDER=dist"
set "ZIP_FILE=StretchTimer-Windows.zip"
set "SOURCE_FILE=stretch_timer.py"

:: ==========================================
:: Step 1: Check prerequisites
:: ==========================================
echo [1/5] Checking prerequisites...

:: Check source file exists
if not exist "%SOURCE_FILE%" (
    echo ERROR: %SOURCE_FILE% not found in %SCRIPT_DIR%
    echo        Cannot create distribution without source file.
    goto :error
)
echo       OK - %SOURCE_FILE% found

:: Check PowerShell is available (needed for zip)
where powershell >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo.
    echo ========================================
    echo   PowerShell Required
    echo ========================================
    echo.
    echo   Deploy.bat requires PowerShell to create the ZIP archive.
    echo   PowerShell is included in Windows 7 SP1 and later.
    echo.
    echo   If you're on an older system, you can manually:
    echo   1. Copy stretch_timer.py to a dist folder
    echo   2. Copy StretchTimer.bat to the same folder
    echo   3. Create a README.txt with instructions
    echo   4. ZIP the folder using your preferred tool
    echo.
    goto :error
)
echo       OK - PowerShell available

:: ==========================================
:: Step 2: Clean and create distribution folder
:: ==========================================
echo.
echo [2/5] Preparing distribution folder...

:: Remove old distribution folder if exists
if exist "%DIST_FOLDER%" (
    echo       Removing old %DIST_FOLDER%\...
    rmdir /s /q "%DIST_FOLDER%" 2>nul
    if exist "%DIST_FOLDER%" (
        echo ERROR: Could not remove old %DIST_FOLDER% folder.
        echo        Please close any programs using files in that folder.
        goto :error
    )
)

:: Create fresh distribution folder
mkdir "%DIST_FOLDER%" 2>nul
if !ERRORLEVEL! neq 0 (
    echo ERROR: Could not create %DIST_FOLDER% folder.
    goto :error
)
echo       OK - Created %DIST_FOLDER%\

:: ==========================================
:: Step 3: Copy source file
:: ==========================================
echo.
echo [3/5] Copying application files...

copy /Y "%SOURCE_FILE%" "%DIST_FOLDER%\" >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo ERROR: Failed to copy %SOURCE_FILE%
    goto :error
)
echo       OK - %SOURCE_FILE% copied

:: ==========================================
:: Step 4: Create launcher and readme
:: ==========================================
echo.
echo [4/5] Creating launcher and documentation...

:: Create the launcher batch file
(
echo @echo off
echo setlocal EnableDelayedExpansion
echo.
echo :: ============================================
echo :: Stretch Timer Launcher
echo :: ============================================
echo.
echo title Stretch Timer
echo.
echo :: Get script directory
echo set "SCRIPT_DIR=%%~dp0"
echo cd /d "%%SCRIPT_DIR%%" ^|^| ^(
echo     echo ERROR: Cannot access script directory.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo :: Verify stretch_timer.py exists
echo if not exist "stretch_timer.py" ^(
echo     echo ERROR: stretch_timer.py not found.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo :check_python
echo set "PYTHON_CMD="
echo.
echo python --version ^>nul 2^>^&1
echo if ^^!ERRORLEVEL^^! equ 0 ^(
echo     set "PYTHON_CMD=python"
echo     goto :python_found
echo ^)
echo.
echo py --version ^>nul 2^>^&1
echo if ^^!ERRORLEVEL^^! equ 0 ^(
echo     set "PYTHON_CMD=py"
echo     goto :python_found
echo ^)
echo.
echo :: Python not found
echo echo Python not found. Opening installation instructions...
echo.
echo where powershell ^>nul 2^>^&1
echo if ^^!ERRORLEVEL^^! neq 0 ^(
echo     echo.
echo     echo Python Required - Install from Microsoft Store or python.org
echo     pause
echo     exit /b 1
echo ^)
echo.
echo powershell -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Stretch Timer requires Python.`n`nClick OK to open Microsoft Store.`n`nAfter installing, click Recheck.', 'Python Required', 'OK', 'Information')" ^>nul 2^>^&1
echo.
echo start "" "ms-windows-store://pdp/?productid=9NCVDN91XZQP"
echo.
echo :recheck_dialog
echo powershell -Command "Add-Type -AssemblyName PresentationFramework; $result = [System.Windows.MessageBox]::Show('Click OK to recheck for Python.`nClick Cancel to quit.', 'Recheck', 'OKCancel', 'Question'); if ($result -eq 'OK') { exit 0 } else { exit 1 }" ^>nul 2^>^&1
echo if ^^!ERRORLEVEL^^! equ 0 ^(
echo     goto :check_python
echo ^) else ^(
echo     exit /b 0
echo ^)
echo.
echo :python_found
echo echo Found Python: ^^!PYTHON_CMD^^!
echo echo Checking dependencies...
echo ^^!PYTHON_CMD^^! -m pip install plyer --quiet --disable-pip-version-check ^>nul 2^>^&1
echo echo Starting Stretch Timer...
echo start "" ^^!PYTHON_CMD^^!w "%%SCRIPT_DIR%%stretch_timer.py"
) > "%DIST_FOLDER%\StretchTimer.bat"

if !ERRORLEVEL! neq 0 (
    echo ERROR: Failed to create StretchTimer.bat
    goto :error
)
echo       OK - StretchTimer.bat created

:: Create README
(
echo STRETCH TIMER
echo =============
echo.
echo A desktop app that reminds you to stretch at regular intervals.
echo.
echo REQUIREMENTS
echo ------------
echo Python 3.10+ ^(free from Microsoft Store or python.org^)
echo.
echo HOW TO RUN
echo ----------
echo Double-click StretchTimer.bat
echo.
echo If Python is not installed, you'll be guided to install it.
echo After installing Python, click "Recheck" to continue.
echo.
echo FEATURES
echo --------
echo - Configurable reminder intervals
echo - Standing stretches with step-by-step instructions
echo - Eye exercises and breathing exercises
echo - Light/dark themes
echo - Quiet hours
echo - Desktop notifications
echo - Auto-saved settings
echo.
echo AUTO-START WITH WINDOWS
echo -----------------------
echo To have Stretch Timer start automatically when you log in:
echo.
echo 1. Press Win+R to open the Run dialog
echo 2. Type: shell:startup
echo 3. Press Enter ^(opens your Startup folder^)
echo 4. Right-click in the folder and select "New ^> Shortcut"
echo 5. Browse to StretchTimer.bat and select it
echo 6. Name the shortcut "Stretch Timer"
echo.
echo The app will now start automatically when you log in.
) > "%DIST_FOLDER%\README.txt"

if !ERRORLEVEL! neq 0 (
    echo ERROR: Failed to create README.txt
    goto :error
)
echo       OK - README.txt created

:: ==========================================
:: Step 5: Create ZIP archive
:: ==========================================
echo.
echo [5/5] Creating ZIP archive...

:: Remove old zip if exists
if exist "%ZIP_FILE%" (
    del /f /q "%ZIP_FILE%" 2>nul
    if exist "%ZIP_FILE%" (
        echo ERROR: Could not remove old %ZIP_FILE%
        echo        Please close any programs using that file.
        goto :error
    )
)

:: Create zip using PowerShell (archive contents, not the folder itself)
powershell -Command "try { Compress-Archive -Path '%DIST_FOLDER%\*' -DestinationPath '%ZIP_FILE%' -Force -ErrorAction Stop } catch { Write-Host $_.Exception.Message; exit 1 }" 2>nul
if !ERRORLEVEL! neq 0 (
    echo ERROR: Failed to create ZIP archive.
    goto :error
)

:: Verify zip was created
if not exist "%ZIP_FILE%" (
    echo ERROR: ZIP file was not created.
    goto :error
)

:: Get and display file size
for %%A in ("%ZIP_FILE%") do set "ZIP_SIZE=%%~zA"
if "!ZIP_SIZE!"=="" set "ZIP_SIZE=0"
set /a ZIP_SIZE_KB=!ZIP_SIZE! / 1024
echo       OK - %ZIP_FILE% created (!ZIP_SIZE_KB! KB)

:: ==========================================
:: Success
:: ==========================================
echo.
echo ========================================
echo   SUCCESS! Deployment complete.
echo ========================================
echo.
echo   Output: %SCRIPT_DIR%%ZIP_FILE%
echo   Size:   !ZIP_SIZE_KB! KB
echo.
echo   Distribution contents:
echo   - StretchTimer.bat  (launcher)
echo   - stretch_timer.py  (application)
echo   - README.txt        (instructions)
echo.
echo   Share %ZIP_FILE% with your team.
echo   Users extract and run StretchTimer.bat
echo.
goto :end

:: ==========================================
:: Error handler
:: ==========================================
:error
echo.
echo ========================================
echo   DEPLOYMENT FAILED
echo ========================================
echo.
echo   Please fix the error above and try again.
echo.

:end
echo.
echo Press any key to exit...
pause >nul
exit /b !ERRORLEVEL!
