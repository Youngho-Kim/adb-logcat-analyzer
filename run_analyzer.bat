@echo off
chcp 65001 > nul
cd /d "%~dp0"

:menu
cls
echo ============================================================
echo [ADB Logcat Analyzer] Mobile QA Diagnostic Launcher
echo ============================================================
echo  1. Demo Analysis (Sample Log)
echo  2. Connected Device Log Dump Analysis (--adb)
echo  3. Real-time Crash Watch + Auto Screenshot (--watch)
echo  4. Analyze Specific Log File (--file)
echo  5. Monkey Stress Test + Crash Watch (--monkey)
echo  0. Exit
echo ============================================================
set /p choice="Select menu (0-5): "

if "%choice%"=="1" (
    python analyzer.py
    pause
    goto menu
)
if "%choice%"=="2" (
    set /p pkg="Package filter (leave blank for all): "
    if "%pkg%"=="" ( python analyzer.py --adb ) else ( python analyzer.py --adb --package "%pkg%" )
    pause
    goto menu
)
if "%choice%"=="3" (
    set /p pkg="Package filter (leave blank for all): "
    if "%pkg%"=="" ( python analyzer.py --watch ) else ( python analyzer.py --watch --package "%pkg%" )
    pause
    goto menu
)
if "%choice%"=="4" (
    set /p fpath="Enter log file path: "
    python analyzer.py --file "%fpath%"
    pause
    goto menu
)
if "%choice%"=="5" (
    set /p pkg="Target package name (e.g. com.example.app): "
    set /p evts="Event count (default 300): "
    if "%evts%"=="" set evts=300
    python analyzer.py --monkey "%pkg%" --events %evts%
    pause
    goto menu
)
if "%choice%"=="0" exit /b 0
goto menu