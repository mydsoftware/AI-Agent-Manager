<?php
/**
 * احراز هویت اختصاصی ارتباط AI Agent Manager با سایت وردپرس.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

final class AI_Agent_Auth {
	/**
	 * بررسی توکن اختصاصی Agent.
	 */
	public static function check( WP_REST_Request $request ) {
		$provided = (string) $request->get_header( 'X-AI-Agent-Token' );
		$stored   = (string) get_option( 'ai_agent_manager_token', '' );

		if ( $provided === '' || $stored === '' ) {
			return new WP_Error(
				'ai_agent_unauthorized',
				'توکن AI Agent ارائه نشده یا در سایت تنظیم نشده است.',
				array( 'status' => 401 )
			);
		}

		if ( ! hash_equals( $stored, $provided ) ) {
			return new WP_Error(
				'ai_agent_unauthorized',
				'توکن AI Agent معتبر نیست.',
				array( 'status' => 401 )
			);
		}

		return true;
	}
}
