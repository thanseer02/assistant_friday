from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.logging import logger

class AssistantException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class PendingActionException(AssistantException):
    """Raised when a tool requires explicit user confirmation."""
    def __init__(self, tool_name: str, arguments: dict):
        self.tool_name = tool_name
        self.arguments = arguments
        super().__init__(f"Tool '{tool_name}' requires confirmation.", status_code=400)

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(AssistantException)
    async def assistant_exception_handler(request: Request, exc: AssistantException):
        logger.error(f"Assistant error: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
