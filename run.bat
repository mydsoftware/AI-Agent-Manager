@echo off
REM AI-Agent-Manager: اسکریپت اجرایی
REM این فایل را اجرا کنید تا سیستم راه‌اندازی شود

cd /d "%~dp0"

echo 🤖 AI-Agent-Manager
echo ==================
echo.

REM بررسی نصب بودن سیستم
if not exist "config.json" (
    echo ⚠️  سیستم نصب نشده است!
    echo در حال اجرای نصب خودکار...
    echo.
    python setup.py
    echo.
)

REM اجرای CLI
python cli.py %*
