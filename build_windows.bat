@echo off
setlocal

cd /d %~dp0

echo [1/4] Checking Python...
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY_CMD=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PY_CMD=python"
  ) else (
    echo Python 3 not found. Please install Python 3.10+ from https://www.python.org/downloads/windows/
    pause
    exit /b 1
  )
)

echo [2/4] Creating build virtualenv...
%PY_CMD% -m venv .venv-build
if errorlevel 1 (
  echo Failed to create virtual environment.
  pause
  exit /b 1
)

call .venv-build\Scripts\activate.bat

echo [3/4] Installing PyInstaller...
python -m pip install --upgrade pip
if errorlevel 1 (
  echo Failed to upgrade pip.
  pause
  exit /b 1
)

python -m pip install pyinstaller
if errorlevel 1 (
  echo Failed to install PyInstaller.
  pause
  exit /b 1
)

echo [4/4] Building EXE...
pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --name FactoryDistanceTool_v1.0.0 ^
  --version-file version_info.txt ^
  app.py

if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)

echo.
echo Build completed.
echo EXE path: %~dp0dist\FactoryDistanceTool_v1.0.0.exe
echo.
pause
