from pathlib import Path


def replace_once(path: str, old: str, new: str) -> bool:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    if new in text:
        return False
    if old not in text:
        raise SystemExit(f"pattern not found: {path}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


changed = False
changed |= replace_once(
    "manager/executor.py",
    '''                    except Exception as error:\n                        task.error = str(error)\n                        if task.can_retry():\n                            task.status = TaskStatus.RETRYING\n                            continue\n                        task.fail(str(error))\n                        break''',
    '''                    except Exception as error:\n                        # شکست این تلاش باید قبل از can_retry ثبت شود.\n                        task.fail(str(error))\n                        if task.can_retry():\n                            task.status = TaskStatus.RETRYING\n                            continue\n                        break''',
)

changed |= replace_once(
    "manager/intention.py",
    '''        selected_agent = None\n        for keyword, agent in self.KEYWORDS.items():\n            if keyword in text.lower():\n                selected_agent = agent\n                break''',
    '''        selected_agent = None\n        # برای درخواست‌های مرکب، هدف اصلی ساخت/توسعه بر عملیات جانبی مقدم است.\n        # بنابراین «تحقیق + کدنویسی + تست + GitHub» باید Manager را developer نگه دارد.\n        priority = (\n            ("developer", ("کدنویسی", "توسعه", "برنامه")),\n            ("research", ("بررسی", "تحقیق")),\n            ("qa", ("تست", "test")),\n            ("github", ("github", "گیتهاب")),\n        )\n        for agent, keywords in priority:\n            if any(keyword in text.lower() for keyword in keywords):\n                selected_agent = agent\n                break''',
)

print("core fixes applied" if changed else "core fixes already present")
