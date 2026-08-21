<?php
// تست پایه برای منطق محدودسازی Canonical به دامنه داخلی.
function aamm_test_canonical_host($site, $target) {
    $site_host = wp_parse_url($site, PHP_URL_HOST);
    $target_host = wp_parse_url($target, PHP_URL_HOST);
    return $site_host && $target_host && strtolower($site_host) === strtolower($target_host);
}

assert(aamm_test_canonical_host('https://example.com', 'https://example.com/page') === true);
assert(aamm_test_canonical_host('https://example.com', 'https://evil.example/page') === false);
