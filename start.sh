#!/bin/bash
# AI-Agent-Manager: شروع سریع
# این فایل تمام مراحل را به‌صورت خودکار انجام می‌دهد

set -e

cd "$(dirname "$0")"

echo "🚀 AI-Agent-Manager: شروع سریع"
echo "=============================="
echo ""

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# مرحله ۱: بررسی پایتون
echo -e "${BLUE}مرحله ۱: بررسی پایتون${NC}"
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo -e "${RED}❌ پایتون یافت نشد!${NC}"
    echo -e "${YELLOW}لطفاً پایتون 3.10+ نصب کنید${NC}"
    exit 1
fi
echo -e "${GREEN}✅ پایتون یافت شد${NC}"
echo ""

# مرحله ۲: نصب خودکار
echo -e "${BLUE}مرحله ۲: نصب خودکار${NC}"
if [ ! -f "config.json" ]; then
    echo -e "${YELLOW}در حال نصب...${NC}"
    $PYTHON setup.py
else
    echo -e "${GREEN}✅ سیستم قبلاً نصب شده${NC}"
fi
echo ""

# مرحله ۳: اجرای CLI
echo -e "${BLUE}مرحله ۳: اجرای CLI${NC}"
echo -e "${GREEN}✅ در حال اجرای سیستم...${NC}"
echo ""
echo "=============================="
echo ""

$PYTHON cli.py "$@"
