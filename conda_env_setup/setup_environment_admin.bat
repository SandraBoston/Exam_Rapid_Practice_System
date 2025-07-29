@echo off
REM PCEP Environment Setup - Run as Administrator
REM This batch file sets up the conda environment for the PCEP project

echo =====================================================
echo PCEP Certification Exam Accelerator - Environment Setup
echo =====================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ❌ NOT running as Administrator!
    echo Please right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo 📁 Current Directory: %~dp0
echo.

REM Change to the project directory
cd /d "%~dp0"

REM Run the optimized Python setup script
echo 🐍 Running optimized Python setup script...
python setup_environment_optimized.py

echo.
echo =====================================================
echo Setup completed! Press any key to close...
pause >nul
