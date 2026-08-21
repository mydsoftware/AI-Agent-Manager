<?php
/**
 * Plugin Name: AI Agent Manager SEO Connector
 * Description: اتصال امن WordPress به AI-Agent-Manager برای اقدامات محدود SEO.
 * Version: 0.1.0
 * Author: AI-Agent-Manager
 */

defined('ABSPATH') || exit;

add_action('rest_api_init', function () {
    register_rest_route('ai-agent-manager/v1', '/seo/canonical', [
        'methods' => 'POST',
        'callback' => 'aamm_set_canonical',
        'permission_callback' => 'aamm_can_write_seo',
        'args' => [
            'url' => ['required' => true, 'sanitize_callback' => 'esc_url_raw'],
            'canonical_url' => ['required' => true, 'sanitize_callback' => 'esc_url_raw'],
        ],
    ]);
});

/**
 * بررسی مجوز اجرای عملیات SEO.
 */
function aamm_can_write_seo(WP_REST_Request $request) {
    return current_user_can('manage_options');
}

/**
 * تغییر Canonical فقط برای یک URL داخلی سایت.
 */
function aamm_set_canonical(WP_REST_Request $request) {
    $url = $request->get_param('url');
    $canonical = $request->get_param('canonical_url');

    $site_host = wp_parse_url(home_url('/'), PHP_URL_HOST);
    $target_host = wp_parse_url($canonical, PHP_URL_HOST);

    if (!$site_host || !$target_host || strtolower($site_host) !== strtolower($target_host)) {
        return new WP_Error('invalid_canonical', 'Canonical باید به دامنه همین سایت اشاره کند.', ['status' => 400]);
    }

    $post_id = url_to_postid($url);
    if (!$post_id) {
        return new WP_Error('post_not_found', 'برای URL موردنظر نوشته یا برگه‌ای پیدا نشد.', ['status' => 404]);
    }

    update_post_meta($post_id, '_aamm_canonical_url', $canonical);

    return new WP_REST_Response([
        'success' => true,
        'changed' => true,
        'post_id' => $post_id,
        'url' => $url,
        'canonical_url' => $canonical,
    ], 200);
}
