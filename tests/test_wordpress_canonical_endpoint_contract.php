<?php
/**
 * بررسی ایستای اتصال Endpoint به Auth و Audit Log.
 */

declare(strict_types=1);

$file = file_get_contents(__DIR__ . '/../wordpress-plugin/ai-agent-manager-seo/includes/class-ai-agent-canonical-endpoint.php');

foreach (array('AI_Agent_Auth', 'permission_callback', 'AI_Agent_Audit_Log', 'set_canonical', 'url_to_postid') as $required) {
    if (strpos($file, $required) === false) {
        throw new RuntimeException("جزء موردنیاز Endpoint پیدا نشد: {$required}");
    }
}

if (strpos($file, 'home_url') === false || strpos($file, 'url_host !== $site_host') === false) {
    throw new RuntimeException('محدودسازی دامنه داخلی Endpoint ناقص است.');
}
