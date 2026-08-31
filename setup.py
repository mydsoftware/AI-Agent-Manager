#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-Agent-Manager: اسکریپت نصب خودکار
این فایل تمام وابستگی‌ها را نصب و سیستم را راه‌اندازی می‌کند
"""

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# رنگ‌ها برای خروجی ترمینال
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """نمایش بنر خوش‌آمدگویی"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🤖 AI-Agent-Manager - نصب خودکار                  ║
║                                                              ║
║          سیستم مدیریت و ساخت ایجنت‌های هوش مصنوعی         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)

def print_step(step_num, message):
    """نمایش مرحله"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}═══ مرحله {step_num}: {message} ═══{Colors.END}")

def print_success(message):
    """نمایش موفقیت"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_warning(message):
    """نمایش هشدار"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_error(message):
    """نمایش خطا"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    """نمایش اطلاعات"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")

def check_python_version():
    """بررسی نسخه پایتون"""
    print_step(1, "بررسی نسخه پایتون")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"پایتون 3.10+ مورد نیاز است. نسخه فعلی: {version.major}.{version.minor}")
        print_info("لطفاً پایتون 3.12 یا بالاتر نصب کنید")
        return False
    
    print_success(f"پایتون {version.major}.{version.minor}.{version.micro} نصب است")
    return True

def check_os():
    """بررسی سیستم‌عامل"""
    print_step(2, "بررسی سیستم‌عامل")
    
    os_name = platform.system()
    print_info(f"سیستم‌عامل: {os_name} {platform.release()}")
    
    if os_name == "Windows":
        print_info("ویندوز شناسایی شد")
    elif os_name == "Linux":
        print_info("لینوکس شناسایی شد")
    elif os_name == "Darwin":
        print_info("macOS شناسایی شد")
    
    return True

def install_pip_packages():
    """نصب وابستگی‌های پایتون"""
    print_step(3, "نصب وابستگی‌های پایتون")
    
    packages = [
        'requests',  # برای HTTP requests
        'pyyaml',    # برای فایل‌های YAML
    ]
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print_info(f"{package} قبلاً نصب شده")
        except ImportError:
            print_info(f"در حال نصب {package}...")
            try:
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', package, '-q'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print_success(f"{package} نصب شد")
            except subprocess.CalledProcessError:
                print_warning(f"خطا در نصب {package} (اختیاری)")
    
    return True

def create_directories():
    """ایجاد دایرکتوری‌های مورد نیاز"""
    print_step(4, "ایجاد دایرکتوری‌های مورد نیاز")
    
    base_dir = Path(__file__).parent
    
    directories = [
        'agents',
        'agents/active',
        'agents/archive',
        'logs',
        'config',
        'templates',
        'cache'
    ]
    
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print_info(f"دایرکتوری: {directory}")
    
    print_success("دایرکتوری‌ها ایجاد شدند")
    return True

def create_default_config():
    """ایجاد تنظیمات پیش‌فرض"""
    print_step(5, "ایجاد تنظیمات پیش‌فرض")
    
    base_dir = Path(__file__).parent
    config_file = base_dir / 'config.json'
    
    default_config = {
        "system": {
            "name": "AI-Agent-Manager",
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "auto_update": True
        },
        "agents": {
            "prefix": "agent",
            "default_language": "python",
            "auto_pr": True,
            "max_concurrent": 3
        },
        "tools": {
            "priority": ["freebuff", "opencode"],
            "timeout": 300,
            "retry_count": 3
        },
        "github": {
            "repository": "",
            "default_branch": "main",
            "auto_label": True
        },
        "supported_types": [
            "research",
            "developer",
            "qa",
            "github",
            "monitoring",
            "analysis",
            "automation"
        ]
    }
    
    if not config_file.exists():
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        print_success("فایل config.json ایجاد شد")
    else:
        print_info("فایل config.json موجود است")
    
    return True

def check_tools():
    """بررسی ابزارهای موجود"""
    print_step(6, "بررسی ابزارهای موجود")
    
    tools_found = []
    
    # بررسی Freebuff
    freebuff_key = os.getenv('FREEBUFF_API_KEY')
    if freebuff_key:
        print_success("Freebuff API Key یافت شد")
        tools_found.append('freebuff')
    else:
        print_warning("Freebuff API Key یافت نشد")
    
    # بررسی OpenCode
    opencode_key = os.getenv('OPENCODE_API_KEY')
    if opencode_key:
        print_success("OpenCode API Key یافت شد")
        tools_found.append('opencode')
    else:
        print_warning("OpenCode API Key یافت نشد")
    
    if not tools_found:
        print_error("هیچ ابزاری پیدا نشد!")
        print_info("لطفاً یکی از متغیرهای زیر را تنظیم کنید:")
        print_info("  export FREEBUFF_API_KEY='your_key'")
        print_info("  export OPENCODE_API_KEY='your_key'")
        return False
    
    print_success(f"ابزارهای موجود: {', '.join(tools_found)}")
    return True

def create_launcher():
    """ایجاد فایل‌های اجرایی"""
    print_step(7, "ایجاد فایل‌های اجرایی")
    
    base_dir = Path(__file__).parent
    os_name = platform.system()
    
    # ایجاد لانچر لینوکس/Mac
    if os_name in ['Linux', 'Darwin']:
        launcher_sh = base_dir / 'run.sh'
        with open(launcher_sh, 'w') as f:
            f.write("""#!/bin/bash
cd "$(dirname "$0")"
python3 cli.py "$@"
""")
        os.chmod(launcher_sh, 0o755)
        print_success("فایل run.sh ایجاد شد")
    
    # ایجاد لانچر ویندوز
    if os_name == 'Windows':
        launcher_bat = base_dir / 'run.bat'
        with open(launcher_bat, 'w') as f:
            f.write("""@echo off
cd /d "%~dp0"
python cli.py %*
""")
        print_success("فایل run.bat ایجاد شد")
    
    return True

def run_tests():
    """اجرای تست‌های اولیه"""
    print_step(8, "اجرای تست‌های اولیه")
    
    base_dir = Path(__file__).parent
    test_file = base_dir / 'test_agent_builder.py'
    
    if test_file.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(test_file), '-v'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print_success("تست‌ها با موفقیت اجرا شدند")
            else:
                print_warning("برخی تست‌ها ناموفق بودند (اختیاری)")
        except subprocess.TimeoutExpired:
            print_warning("تست‌ها بیش از حد طول کشیدند")
        except Exception as e:
            print_warning(f"خطا در اجرای تست‌ها: {e}")
    else:
        print_info("فایل تست یافت نشد")
    
    return True

def show_final_guide():
    """نمایش راهنمای نهایی"""
    print_step(9, "راهنمای استفاده")
    
    guide = f"""
{Colors.GREEN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║                    ✅ نصب با موفقیت انجام شد!                ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.CYAN}نحوه استفاده:{Colors.END}

  {Colors.BOLD}۱. اجرای CLI تعاملی:{Colors.END}
     python cli.py

  {Colors.BOLD}۲. ساخت ایجنت با یک دستور:{Colors.END}
     python cli.py create --type developer --description "توضیحات"

  {Colors.BOLD}۳. لیست ایجنت‌ها:{Colors.END}
     python cli.py list

  {Colors.BOLD}۴. دریافت کمک:{Colors.END}
     python cli.py help

{Colors.CYAN}نکته: اگر OpenCode یا Freebuff دارید:{Colors.END}
  - کافیست مسیر AI-Agent-Manager را به آن بدهید
  - اسکریپت cli.py را اجرا کنید
  - راهنما شما را قدم به قدم هدایت می‌کند

{Colors.GREEN}برای شروع:{Colors.END}
  python cli.py

"""
    print(guide)

def main():
    """تابع اصلی نصب"""
    print_banner()
    
    start_time = datetime.now()
    
    steps = [
        ("بررسی پایتون", check_python_version),
        ("بررسی سیستم‌عامل", check_os),
        ("نصب وابستگی‌ها", install_pip_packages),
        ("ایجاد دایرکتوری‌ها", create_directories),
        ("ایجاد تنظیمات", create_default_config),
        ("بررسی ابزارها", check_tools),
        ("ایجاد لانچر", create_launcher),
        ("اجرای تست‌ها", run_tests),
    ]
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                print_error(f"خطا در مرحله: {step_name}")
                print_info("آیا می‌خواهید ادامه دهید? (y/n)")
                response = input().lower()
                if response != 'y':
                    sys.exit(1)
        except Exception as e:
            print_error(f"خطا در {step_name}: {e}")
    
    show_final_guide()
    
    elapsed = datetime.now() - start_time
    print(f"{Colors.GREEN}زمان نصب: {elapsed.total_seconds():.1f} ثانیه{Colors.END}")

if __name__ == '__main__':
    main()
