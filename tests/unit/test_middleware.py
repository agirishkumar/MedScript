# tests/unit/test_middleware.py

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.utils.middleware import RequestIDMiddleware, LoggingMiddleware

# Initialize the FastAPI app and add the middlewares
app = FastAPI()

# Add middlewares in the order they should be applied
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

# Define an endpoint to test middleware functionalities
@app.get("/test-middleware")
async def test_middleware_endpoint():
    return {"message": "Middleware test successful!"}


# Define an endpoint to test error handling in the middleware
@app.get("/test-error")
async def test_error():
    """
    Endpoint to test error handling in the LoggingMiddleware.
    This endpoint raises a ValueError intentionally to test that the
    LoggingMiddleware captures and logs the error correctly.
    """
    raise ValueError("Intentional Error")


@pytest.fixture
def client():
    return TestClient(app)


def test_request_id_middleware(client):
    response = client.get("/test-middleware")
    assert response.status_code == 200
    assert response.json() == {"message": "Middleware test successful!"}

    # Check if the request ID header is present in the response
    request_id = response.headers.get("X-Request-ID")
    assert request_id is not None
    assert len(request_id) > 0  # Ensure that the request ID is not an empty string


def test_logging_middleware(client, caplog):
    with caplog.at_level("INFO"):
        response = client.get("/test-middleware")
        assert response.status_code == 200

        # Check if the log messages contain the expected content
        log_messages = [record.message for record in caplog.records]
        assert any("Request" in message for message in log_messages)
        assert any("Status" in message for message in log_messages)
        assert any("Process Time" in message for message in log_messages)
        assert any("Request ID" in message for message in log_messages)


def test_middleware_error_handling(client, caplog):
    """
    Test that the LoggingMiddleware logs the error message when an exception is raised during the request.

    This test sends a GET request to the /test-error endpoint, which raises a ValueError.
    The test uses the caplog fixture to capture the log output during the test and checks
    that the log output contains the expected log message for the error.
    """
    with caplog.at_level("ERROR"):
        response = client.get("/test-error")  # Removed await and converted to sync
        assert response.status_code == 500  # Check that the status code is 500 for the error

        # Check if the log messages contain the expected content
        log_messages = [record.message for record in caplog.records]
        assert any("Intentional Error" in message for message in log_messages)


@pytest.mark.asyncio
async def test_error(client, caplog):
    """
    Test that the /test-error endpoint raises a ValueError and the LoggingMiddleware logs it correctly.

    This test sends a GET request to the /test-error endpoint, which raises a ValueError.
    The test uses the caplog fixture to capture the log output during the test and checks
    that the log output contains the expected log message for the error.
    """
    with caplog.at_level("ERROR"):
        try:
            client.get("/test-error")
        except ValueError:
            pass  # Handle the expected exception

        # Check if the log messages contain the expected content for the error
        log_messages = [record.message for record in caplog.records]
        assert any("Intentional Error" in message for message in log_messages)

