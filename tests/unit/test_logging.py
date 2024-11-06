# tests/unit/test_logging.py

'''
Tests logger setup, ensuring it's named 'app' and contains at least one StreamHandler.
'''

import logging
from app.core.logging import setup_logging

def test_logger_setup():
    """
    Tests that the logger is set up correctly.

    Checks that the logger's name is 'app' and that it has at least one
    StreamHandler.
    """
    logger = setup_logging()
    assert logger.name == "app"
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)  
