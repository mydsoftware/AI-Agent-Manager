from agents.seo_action_policy import SeoActionPolicyAnalyzer
from agents.seo_priority import SeoPriorityItem


def test_action_policy_classifies_actions_safely():
    analyzer = SeoActionPolicyAnalyzer()

    assert analyzer.decide(SeoPriorityItem("Canonical وجود ندارد", "زیاد", 2)).mode == "قابل اصلاح خودکار"
    assert analyzer.decide(SeoPriorityItem("عنوان صفحه وجود ندارد", "زیاد", 2)).mode == "نیازمند تأیید"
    assert analyzer.decide(SeoPriorityItem("پاسخ HTTP خطادار", "بحرانی", 1)).mode == "گزارش شود"
