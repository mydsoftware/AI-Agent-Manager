def test_import_chain_does_not_create_circular_import():
    import agents.public_site_scanner  # noqa: F401
    import agents.site_audit_report  # noqa: F401
    import agents.seo_health  # noqa: F401
    import agents.seo_execution_engine  # noqa: F401
    import agents.site_audit_actions  # noqa: F401
    import agents.website_audit  # noqa: F401
