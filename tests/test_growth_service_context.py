from manager.growth_service_context import GrowthServiceContext


def test_context_reads_configuration_from_environment(monkeypatch):
    monkeypatch.setenv("GROWTH_CRM_BASE_URL", "https://crm.example")
    monkeypatch.setenv("GROWTH_CRM_API_KEY", "secret")

    context = GrowthServiceContext.from_env()

    assert context.configured("crm") is True
    assert context.crm_base_url == "https://crm.example"
    assert context.crm_api_key == "secret"


def test_context_reports_missing_configuration(monkeypatch):
    monkeypatch.delenv("GROWTH_WHATSAPP_BASE_URL", raising=False)
    monkeypatch.delenv("GROWTH_WHATSAPP_API_KEY", raising=False)

    assert GrowthServiceContext.from_env().configured("whatsapp") is False



def test_context_builds_only_configured_adapters(monkeypatch):
    monkeypatch.setenv("GROWTH_CRM_BASE_URL", "https://crm.example")
    monkeypatch.setenv("GROWTH_CRM_API_KEY", "secret")
    monkeypatch.delenv("GROWTH_WHATSAPP_BASE_URL", raising=False)
    monkeypatch.delenv("GROWTH_WHATSAPP_API_KEY", raising=False)

    from manager.growth_service_context import build_http_adapters

    adapters = build_http_adapters(GrowthServiceContext.from_env())
    assert set(adapters) == {"create_lead", "qualify_lead", "record_sale"}
