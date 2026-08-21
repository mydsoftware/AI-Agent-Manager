<?php
/**
 * Endpoint امن تغییر Canonical برای AI Agent Manager.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

final class AI_Agent_Canonical_Endpoint {
	public static function register() {
		register_rest_route(
			'ai-agent-manager/v1',
			'/seo/canonical',
			array(
				'methods'             => 'POST',
				'permission_callback' => array( 'AI_Agent_Auth', 'check' ),
				'callback'            => array( __CLASS__, 'update' ),
			)
		);
	}

	public static function update( WP_REST_Request $request ) {
		$url           = esc_url_raw( (string) $request->get_param( 'url' ) );
		$canonical_url = esc_url_raw( (string) $request->get_param( 'canonical_url' ) );

		if ( ! $url || ! $canonical_url ) {
			return new WP_Error( 'ai_agent_invalid_url', 'URL یا Canonical معتبر نیست.', array( 'status' => 400 ) );
		}

		$site_host = wp_parse_url( home_url( '/' ), PHP_URL_HOST );
		$url_host  = wp_parse_url( $url, PHP_URL_HOST );
		$can_host  = wp_parse_url( $canonical_url, PHP_URL_HOST );

		if ( ! $site_host || $url_host !== $site_host || $can_host !== $site_host ) {
			return new WP_Error( 'ai_agent_external_url', 'فقط URLهای همین سایت مجاز هستند.', array( 'status' => 400 ) );
		}

		$post_id = url_to_postid( $url );
		if ( ! $post_id ) {
			return new WP_Error( 'ai_agent_post_not_found', 'صفحه متناظر در وردپرس پیدا نشد.', array( 'status' => 404 ) );
		}

		$old = get_post_meta( $post_id, '_ai_agent_manager_canonical', true );
		update_post_meta( $post_id, '_ai_agent_manager_canonical', $canonical_url );

		AI_Agent_Audit_Log::record(
			'set_canonical',
			$url,
			array(
				'post_id' => $post_id,
				'old'     => $old,
				'new'     => $canonical_url,
			)
		);

		return rest_ensure_response(
			array(
			'success'      => true,
			'changed'      => $old !== $canonical_url,
			'post_id'      => $post_id,
			'canonical_url' => $canonical_url,
			)
		);
	}
}

add_action( 'rest_api_init', array( 'AI_Agent_Canonical_Endpoint', 'register' ) );
