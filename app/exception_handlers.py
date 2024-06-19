import sentry_sdk
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

async def sentry_exception_handler(request: Request, exc: Exception):
    with sentry_sdk.push_scope() as scope:
        scope.set_extra("request", request.url.path)
        sentry_sdk.capture_exception(exc)
    return await http_exception_handler(request, exc)

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )