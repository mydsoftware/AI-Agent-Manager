#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-Agent-Manager: CLI تعاملی
نقطه ورود واحد برای تمام عملیات
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# اضافه کردن مسیر فعلی به sys.path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from agent_builder import AgentBuilder

# رنگ‌ها
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def print_banner():
    """نمایش بنر"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🤖 AI-Agent-Manager                                 ║
║                                                              ║
║          سیستم مدیریت و ساخت ایجنت‌های هوش مصنوعی         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)

def print_menu():
    """نمایش منوی اصلی"""
    menu = f"""
{Colors.BOLD}منوی اصلی:{Colors.END}

  {Colors.GREEN}۱.{Colors.END} ساخت ایجنت جدید
  {Colors.GREEN}۲.{Colors.END} لیست ایجنت‌ها
  {Colors.GREEN}۳.{Colors.END} مشاهده ایجنت
  {Colors.GREEN}۴.{Colors.END} ایجاد PR
  {Colors.GREEN}۵.{Colors.END} تنظیمات
  {Colors.GREEN}۶.{Colors.END} تست سیستم
  {Colors.GREEN}۷.{Colors.END} راهنما
  {Colors.GREEN}۸.{Colors.END} خروج

"""
    print(menu)

def get_user_choice(max_choice):
    """دریافت انتخاب کاربر"""
    while True:
        try:
            choice = input(f"{Colors.CYAN}انتخاب شما (1-{max_choice}): {Colors.END}")
            choice = int(choice)
            if 1 <= choice <= max_choice:
                return choice
            print(f"{Colors.RED}لطفاً عددی بین 1 تا {max_choice} وارد کنید{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}لطفاً یک عدد وارد کنید{Colors.END}")

def get_agent_type():
    """دریافت نوع ایجنت"""
    types = [
        ('1', 'research', 'تحقیق و جستجو'),
        ('2', 'developer', 'توسعه و برنامه‌نویسی'),
        ('3', 'qa', 'تست و کنترل کیفیت'),
        ('4', 'github', 'مدیریت گیت‌هاب'),
        ('5', 'monitoring', 'پایش سیستم'),
        ('6', 'analysis', 'تحلیل داده'),
        ('7', 'automation', 'اتوماسیون وظایف'),
    ]
    
    print(f"\n{Colors.BOLD}نوع ایجنت:{Colors.END}")
    for num, type_name, desc in types:
        print(f"  {Colors.GREEN}{num}.{Colors.END} {type_name} - {desc}")
    
    while True:
        choice = input(f"\n{Colors.CYAN}انتخاب نوع (1-7): {Colors.END}")
        for num, type_name, desc in types:
            if choice == num:
                return type_name
        print(f"{Colors.RED}لطفاً عددی بین 1 تا 7 وارد کنید{Colors.END}")

def get_language():
    """دریافت زبان برنامه‌نویسی"""
    languages = [
        ('1', 'python', 'Python'),
        ('2', 'javascript', 'JavaScript'),
        ('3', 'typescript', 'TypeScript'),
        ('4', 'csharp', 'C#'),
        ('5', 'go', 'Go'),
        ('6', 'rust', 'Rust'),
    ]
    
    print(f"\n{Colors.BOLD}زبان برنامه‌نویسی:{Colors.END}")
    for num, lang, name in languages:
        print(f"  {Colors.GREEN}{num}.{Colors.END} {name}")
    
    while True:
        choice = input(f"\n{Colors.CYAN}انتخاب زبان (1-6): {Colors.END}")
        for num, lang, name in languages:
            if choice == num:
                return lang
        print(f"{Colors.RED}لطفاً عددی بین 1 تا 6 وارد کنید{Colors.END}")

def create_agent_interactive(builder):
    """ساخت تعاملی ایجنت"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══ ساخت ایجنت جدید ═══{Colors.END}\n")
    
    # دریافت نوع ایجنت
    agent_type = get_agent_type()
    
    # دریافت توضیحات
    print(f"\n{Colors.BOLD}توضیحات ایجنت:{Colors.END}")
    print(f"{Colors.DIM}توضیح دهید ایجنت چه کاری باید انجام دهد{Colors.END}")
    description = input(f"{Colors.CYAN}توضیحات: {Colors.END}")
    
    if not description.strip():
        print(f"{Colors.RED}توضیحات نمی‌تواند خالی باشد!{Colors.END}")
        return
    
    # دریافت زبان
    language = get_language()
    
    # تأیید
    print(f"\n{Colors.BOLD}اطلاعات ایجنت:{Colors.END}")
    print(f"  نوع: {Colors.GREEN}{agent_type}{Colors.END}")
    print(f"  توضیحات: {Colors.GREEN}{description}{Colors.END}")
    print(f"  زبان: {Colors.GREEN}{language}{Colors.END}")
    
    confirm = input(f"\n{Colors.CYAN}آیا ادامه دهیم? (y/n): {Colors.END}")
    if confirm.lower() != 'y':
        print(f"{Colors.YELLOW}لغو شد{Colors.END}")
        return
    
    # ساخت ایجنت
    print(f"\n{Colors.YELLOW}در حال ساخت ایجنت...{Colors.END}")
    print(f"{Colors.DIM}لطفاً صبر کنید{Colors.END}")
    
    try:
        agent = builder.create_agent(
            agent_type=agent_type,
            description=description,
            language=language
        )
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ایجنت با موفقیت ساخته شد!{Colors.END}")
        print(f"\n{Colors.BOLD}اطلاعات ایجنت:{Colors.END}")
        print(f"  شناسه: {Colors.GREEN}{agent['id']}{Colors.END}")
        print(f"  نوع: {Colors.GREEN}{agent['type']}{Colors.END}")
        print(f"  ابزار: {Colors.GREEN}{agent['tool_used']}{Colors.END}")
        print(f"  مسیر: {Colors.GREEN}agents/{agent['id']}/{Colors.END}")
        
        # پیشنهاد ایجاد PR
        create_pr = input(f"\n{Colors.CYAN}آیا PR ایجاد شود? (y/n): {Colors.END}")
        if create_pr.lower() == 'y':
            print(f"{Colors.YELLOW}در حال ایجاد PR...{Colors.END}")
            result = builder.create_pull_request(agent['id'])
            if result.get('pr_url'):
                print(f"{Colors.GREEN}PR ایجاد شد: {result['pr_url']}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}PR ایجاد نشد (ممکن است GitHub Token تنظیم نباشد){Colors.END}")
    
    except Exception as e:
        print(f"{Colors.RED}خطا در ساخت ایجنت: {e}{Colors.END}")

def list_agents(builder):
    """نمایش لیست ایجنت‌ها"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══ لیست ایجنت‌ها ═══{Colors.END}\n")
    
    agents = builder.list_agents()
    
    if not agents:
        print(f"{Colors.YELLOW}هیچ ایجنتی وجود ندارد{Colors.END}")
        print(f"{Colors.DIM}اولین ایجنت خود را بسازید!{Colors.END}")
        return
    
    print(f"{Colors.BOLD}{'شناسه':<30} {'نوع':<15} {'تاریخ':<20}{Colors.END}")
    print("-" * 70)
    
    for agent in agents:
        agent_id = agent.get('id', 'نامشخص')
        agent_type = agent.get('type', 'نامشخص')
        created = agent.get('created_at', '')[:10]
        
        print(f"{agent_id:<30} {agent_type:<15} {created:<20}")

def show_agent(builder):
    """نمایش جزئیات یک ایجنت"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══ مشاهده ایجنت ═══{Colors.END}\n")
    
    agent_id = input(f"{Colors.CYAN}شناسه ایجنت: {Colors.END}")
    
    agent = builder.get_agent(agent_id)
    
    if not agent:
        print(f"{Colors.RED}ایجنت {agent_id} یافت نشد{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}جزئیات ایجنت:{Colors.END}")
    for key, value in agent.items():
        print(f"  {Colors.BOLD}{key}:{Colors.END} {value}")

def test_system(builder):
    """تست سیستم"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══ تست سیستم ═══{Colors.END}\n")
    
    print(f"{Colors.YELLOW}در حال تست...{Colors.END}")
    
    # تست ۱: بررسی ابزار
    print(f"\n{Colors.BOLD}تست ۱: بررسی ابزار{Colors.END}")
    print(f"  ابزار انتخاب شده: {Colors.GREEN}{builder.selected_tool}{Colors.END}")
    
    # تست ۲: ساخت ایجنت تست
    print(f"\n{Colors.BOLD}تست ۲: ساخت ایجنت تست{Colors.END}")
    try:
        agent = builder.create_agent(
            agent_type='developer',
            description='ایجنت تست سیستم',
            language='python'
        )
        print(f"  ایجنت تست: {Colors.GREEN}{agent['id']}{Colors.END}")
        print(f"  {Colors.GREEN}✅ تست موفق{Colors.END}")
    except Exception as e:
        print(f"  {Colors.RED}❌ تست ناموفق: {e}{Colors.END}")
    
    # تست ۳: لیست ایجنت‌ها
    print(f"\n{Colors.BOLD}تست ۳: لیست ایجنت‌ها{Colors.END}")
    agents = builder.list_agents()
    print(f"  تعداد ایجنت‌ها: {Colors.GREEN}{len(agents)}{Colors.END}")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ تست سیستم تکمیل شد!{Colors.END}")

def show_help():
    """نمایش راهنما"""
    help_text = f"""
{Colors.BOLD}{Colors.CYAN}═══ راهنمای AI-Agent-Manager ═══{Colors.END}

{Colors.BOLD}نحوه استفاده:{Colors.END}

  {Colors.GREEN}۱. ساخت ایجنت:{Colors.END}
     از منوی اصلی گزینه ۱ را انتخاب کنید
     نوع ایجنت، توضیحات و زبان را مشخص کنید
     ایجنت به‌صورت خودکار ساخته می‌شود

  {Colors.GREEN}۲. لیست ایجنت‌ها:{Colors.END}
     از منوی اصلی گزینه ۲ را انتخاب کنید

  {Colors.GREEN}۳. مشاهده ایجنت:{Colors.END}
     از منوی اصلی گزینه ۳ را انتخاب کنید
     شناسه ایجنت را وارد کنید

  {Colors.GREEN}۴. ایجاد PR:{Colors.END}
     از منوی اصلی گزینه ۴ را انتخاب کنید
     شناسه ایجنت را وارد کنید

{Colors.BOLD}انواع ایجنت:{Colors.END}

  {Colors.GREEN}research{Colors.END}    - تحقیق و جستجوی اطلاعات
  {Colors.GREEN}developer{Colors.END}   - توسعه و برنامه‌نویسی
  {Colors.GREEN}qa{Colors.END}          - تست و کنترل کیفیت
  {Colors.GREEN}github{Colors.END}      - مدیریت گیت‌هاب
  {Colors.GREEN}monitoring{Colors.END}  - پایش سیستم
  {Colors.GREEN}analysis{Colors.END}    - تحلیل داده
  {Colors.GREEN}automation{Colors.END}  - اتوماسیون وظایف

{Colors.BOLD}نکات:{Colors.END}

  • ابزار خودکار انتخاب می‌شود (Freebuff یا OpenCode)
  • GitHub Token برای PR خودکار نیاز است
  • تمام فایل‌ها در پوشه agents/ ذخیره می‌شوند

"""
    print(help_text)

def main_loop():
    """حلقه اصلی CLI"""
    builder = AgentBuilder(config_path='config.json')
    
    while True:
        print_menu()
        choice = get_user_choice(8)
        
        if choice == 1:
            create_agent_interactive(builder)
        
        elif choice == 2:
            list_agents(builder)
        
        elif choice == 3:
            show_agent(builder)
        
        elif choice == 4:
            agent_id = input(f"\n{Colors.CYAN}شناسه ایجنت: {Colors.END}")
            print(f"{Colors.YELLOW}در حال ایجاد PR...{Colors.END}")
            result = builder.create_pull_request(agent_id)
            if result.get('pr_url'):
                print(f"{Colors.GREEN}PR ایجاد شد: {result['pr_url']}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}PR ایجاد نشد{Colors.END}")
        
        elif choice == 5:
            print(f"\n{Colors.DIM}تنظیمات در config.json{Colors.END}")
            print(f"{Colors.DIM}فایل را ویرایش کنید{Colors.END}")
        
        elif choice == 6:
            test_system(builder)
        
        elif choice == 7:
            show_help()
        
        elif choice == 8:
            print(f"\n{Colors.GREEN}خداحافظ! 👋{Colors.END}\n")
            break
        
        input(f"\n{Colors.DIM}برای ادامه Enter را بزنید...{Colors.END}")

def main():
    """نقطه ورود اصلی"""
    parser = argparse.ArgumentParser(
        description='AI-Agent-Manager: سیستم مدیریت و ساخت ایجنت‌ها'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='دستورات')
    
    # دستور create
    create_parser = subparsers.add_parser('create', help='ساخت ایجنت')
    create_parser.add_argument('--type', required=True, help='نوع ایجنت')
    create_parser.add_argument('--description', required=True, help='توضیحات')
    create_parser.add_argument('--language', default='python', help='زبان')
    
    # دستور list
    subparsers.add_parser('list', help='لیست ایجنت‌ها')
    
    # دستور get
    get_parser = subparsers.add_parser('get', help='دریافت ایجنت')
    get_parser.add_argument('--agent-id', required=True, help='شناسه ایجنت')
    
    # دستور pr
    pr_parser = subparsers.add_parser('pr', help='ایجاد PR')
    pr_parser.add_argument('--agent-id', required=True, help='شناسه ایجنت')
    
    # دستور interactive
    subparsers.add_parser('interactive', help='حالت تعاملی')
    
    args = parser.parse_args()
    
    # اگر دستوری داده نشده، حالت تعاملی اجرا شود
    if not args.command:
        print_banner()
        main_loop()
        return
    
    builder = AgentBuilder(config_path='config.json')
    
    if args.command == 'create':
        agent = builder.create_agent(
            agent_type=args.type,
            description=args.description,
            language=args.language
        )
        print(json.dumps(agent, indent=2, ensure_ascii=False))
    
    elif args.command == 'list':
        agents = builder.list_agents()
        print(json.dumps(agents, indent=2, ensure_ascii=False))
    
    elif args.command == 'get':
        agent = builder.get_agent(args.agent_id)
        if agent:
            print(json.dumps(agent, indent=2, ensure_ascii=False))
        else:
            print(f"ایجنت {args.agent_id} یافت نشد")
            sys.exit(1)
    
    elif args.command == 'pr':
        result = builder.create_pull_request(args.agent_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == 'interactive':
        print_banner()
        main_loop()

if __name__ == '__main__':
    main()
