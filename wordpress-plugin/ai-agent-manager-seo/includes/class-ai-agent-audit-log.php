<?php
/**
 * ثبت گزارش عملیات AI Agent.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

final class AI_Agent_Audit_Log {
	/**
	 * ثبت یک عملیات بدون ذخیره توکن یا رمز عبور.
	 */
	public static function record( $action, $url, $details = array() ) {
		$entry = array(
			'time'    => current_time( 'mysql', true ),
			'action'  => sanitize_key( $action ),
			'url'     => esc_url_raw( $url ),
			'user_id' => get_current_user_id(),
			'details' => wp_json_encode( $details, JSON_UNESCAPED_UNICODE ),
		);

		$logs   = get_option( 'ai_agent_manager_audit_log', array() );
		$logs[] = $entry;

		if ( count( $logs ) > 100 ) {
			$logs = array_slice( $logs, -100 );
		}

		update_option( 'ai_agent_manager_audit_log', $logs, false );
	}
}
