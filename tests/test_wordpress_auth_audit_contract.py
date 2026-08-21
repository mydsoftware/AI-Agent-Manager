<?php
/**
 * قرارداد امنیتی Writer وردپرس را به صورت ایستا بررسی می‌کند.
 */

declare(strict_types=1);

$auth = file_get_contents(__DIR__ . '/../wordpress-plugin/ai-agent-manager-seo/includes/class-ai-agent-auth.php');
$log  = file_get_contents(__DIR__ . '/../wordpress-plugin/ai-agent-manager-seo/includes/class-ai-agent-audit-log.php');

if (strpos($auth, "X-AI-Agent-Token") === false || strpos($auth, 'hash_equals') === false) {
    throw new RuntimeException('احراز هویت اختصاصی AI Agent ناقص است.');
}

if (strpos($log, 'ai_agent_manager_audit_log') === false || strpos($log, 'application_password') !== false || strpos($log, 'ai_agent_manager_token') !== false) {
    throw new RuntimeException('Audit Log نباید توکن یا رمز را ذخیره کند.');
}
