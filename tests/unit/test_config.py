# tests/unit/test_config.py

'''
Test for validating the app's configuration values, including project name, API version, and origins.
'''

from app.core.config import settings

def test_config_values():
    """
    Tests that the app's configuration is properly set up.

    The values tested are the ones that are not set by environment variables.
    """
    assert settings.PROJECT_NAME == "Medical Diagnostic Assistant API"
    assert settings.API_V1_STR == "/api/v1"
    assert isinstance(settings.ALLOWED_ORIGINS, list)
