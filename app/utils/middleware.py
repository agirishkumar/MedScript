# app/utils/middleware.py

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from app.core.logging import logger

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        log_dict = {
            "request_id": getattr(request.state, "request_id", None),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": f"{process_time:.2f}s"
        }
        
        log_msg = f"Request: {log_dict['method']} {log_dict['path']} | " \
                  f"Status: {log_dict['status_code']} | " \
                  f"Process Time: {log_dict['process_time']} | " \
                  f"Request ID: {log_dict['request_id']}"
        
        logger.info(log_msg, extra=log_dict)
        
        return response                               