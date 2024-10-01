import logging
from typing import Any, Callable, Optional

import fire
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from .routers import execution_router, integrations_router

# Initialize the FastAPI app
app: FastAPI = FastAPI()

# Add routers
app.include_router(integrations_router)
app.include_router(execution_router)

# Configure the logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger: logging.Logger = logging.getLogger(__name__)


def make_exception_handler(http_status: int) -> Callable[[Any, Any], Any]:
    """
    Creates a custom exception handler for the application.

    Parameters:
    - http_status (int): The HTTP status code to return for this exception.

    Returns:
    A callable exception handler that logs the exception and returns a JSON response with the specified status code.
    """

    async def _handler(request: Request, exc: Exception):
        exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
        logger.error(f"Exception: {exc_str}", exc_info=True)
        content = {"status_code": http_status, "message": exc_str, "data": None}
        return JSONResponse(content=content, status_code=http_status)

    return _handler


def register_exceptions(app: FastAPI) -> None:
    """
    Registers custom exception handlers for the FastAPI application.

    Parameters:
    - app (FastAPI): The FastAPI application instance to register the exception handlers for.
    """
    app.add_exception_handler(
        RequestValidationError,
        make_exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTPException.
    """
    logger.warning(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"message": exc.detail}},
    )


def main(
    host: str = "0.0.0.0",
    port: int = 8000,
    backlog: int = 4096,
    timeout_keep_alive: int = 30,
    workers: Optional[int] = None,
    log_level: str = "info",
) -> None:
    """
    Entry point to run the FastAPI app with Uvicorn.

    Parameters:
    - host (str): The host IP address.
    - port (int): The port number to listen on.
    - backlog (int): The maximum number of connections to hold.
    - timeout_keep_alive (int): Keep-alive timeout.
    - workers (Optional[int]): Number of worker processes.
    - log_level (str): Logging level for Uvicorn.
    """
    uvicorn.run(
        "your_module_name:app",  # Replace with your actual module and app reference
        host=host,
        port=port,
        log_level=log_level,
        timeout_keep_alive=timeout_keep_alive,
        backlog=backlog,
        workers=workers,
    )


if __name__ == "__main__":
    fire.Fire(main)
