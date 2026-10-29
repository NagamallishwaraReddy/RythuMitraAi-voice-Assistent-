import pytest
from app import main as main_module
from app.services import DemoAdvisor, FarmingAgentService, GeminiService, GnaniSTTService, GnaniTTSService


@pytest.fixture(autouse=True)
def reset_demo_services_for_tests(monkeypatch):
    """Ensure unit tests have deterministic default services regardless of local .env credentials."""
    monkeypatch.setattr(main_module, 'ADVISOR', FarmingAgentService(gemini=GeminiService(''), demo=DemoAdvisor()))
    monkeypatch.setattr(main_module, 'STT_SERVICE', GnaniSTTService(''))
    monkeypatch.setattr(main_module, 'TTS_SERVICE', GnaniTTSService(''))
