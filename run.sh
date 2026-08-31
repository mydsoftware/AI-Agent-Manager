#!/bin/bash
# AI-Agent-Manager: اسکریپت اجرایی
# این فایل را اجرا کنید تا سیستم راه‌اندازی شود

cd "$(dirname "$0")"

echo "🤖 AI-Agent-Manager"
echo "=================="
echo ""

# بررسی نصب بودن سیستم
if [ ! -f "config.json" ]; then
    echo "⚠️  سیستم نصب نشده است!"
    echo "در حال اجرای نصب خودکار..."
    echo ""
    python3 setup.py
    echo ""
fi

# اجرای CLI
python3 cli.py "$@"
