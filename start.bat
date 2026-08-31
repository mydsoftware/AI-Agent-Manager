@echo off
REM AI-Agent-Manager: شروع سریع
REM این فایل تمام مراحل را به‌صورت خودکار انجام می‌دهد

cd /d "%~dp0"

echo 🚀 AI-Agent-Manager: شروع سریع
echo ==============================
echo.

REM مرحله ۱: بررسی پایتون
echo مرحله ۱: بررسی پایتون
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ پایتون یافت نشد!
    echo لطفاً پایتون 3.10+ نصب کنید
    pause
    exit /b 1
)
echo ✅ پایتون یافت شد
echo.

REM مرحله ۲: نصب خودکار
echo مرحله ۲: نصب خودکار
if not exist "config.json" (
    echo در حال نصب...
    python setup.py
) else (
    echo ✅ سیستم قبلاً نصب شده
)
echo.

REM مرحله ۳: اجرای CLI
echo مرحله ۳: اجرای CLI
echo ✅ در حال اجرای سیستم...
echo.
echo ==============================
echo.

python cli.py %*
