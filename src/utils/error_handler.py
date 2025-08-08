import functools
from typing import Any, Callable, Optional, TypeVar, Union

from ..logger_config import get_logger

T = TypeVar("T")

class ErrorHandler:
    """Error handler"""

    @staticmethod
    def _get_logger(logger_name: str):
        """Get the logger"""
        return get_logger(logger_name)
    
    @staticmethod
    def handle_sync(
        logger_name: str,
        operation_name: str,
        fallback_value: Any = None,
        reraise: bool = False,   
    ):
        """Handle synchronous operations"""
        def decorator(func: Callable[..., T]) -> Callable[..., Union[T, Any]]:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Union[T, Any]:
                logger = ErrorHandler._get_logger(logger_name)
                try:
                    logger.debug(f"{operation_name} started")
                    result = func(*args, **kwargs)
                    logger.debug(f"{operation_name} completed")
                    return result
                except Exception as e:
                    error_msg = f"{operation_name} error occurred: {str(e)}"
                    logger.exception(error_msg)
                    if reraise:
                        raise
                    return fallback_value
            return wrapper

        return decorator
    
    @staticmethod
    def handle_async(
        logger_name: str,
        operation_name: str,
        fallback_value: Any = None,
        reraise: bool = False,
    ):
        """Error handling decorator for asynchronous processing"""

        def decorator(func: Callable[..., T]) -> Callable[..., Union[T, Any]]:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Union[T, Any]:
                logger = ErrorHandler._get_logger(logger_name)
                try:
                    logger.debug(f"{operation_name} started")
                    result = await func(*args, **kwargs)
                    logger.debug(f"{operation_name} completed")
                    return result
                except Exception as e:
                    error_msg = f"{operation_name} error occurred: {str(e)}"
                    logger.exception(error_msg)
                    if reraise:
                        raise
                    return fallback_value

            return wrapper

        return decorator
    
    @staticmethod
    def log_and_return_error(
        logger_name: str,
        operation_name: str,
        error: Exception,
        error_message_template: str = "{operation} error occurred: {error}",
    ) -> str:
        """Log the error and return a user-friendly error message"""
        logger = ErrorHandler._get_logger(logger_name)
        error_msg = f"{operation_name} error occurred: {str(error)}"
        logger.exception(error_msg)
        return error_message_template.format(operation=operation_name, error=str(error))
    
    
    @staticmethod
    def handle_api_error(
        logger_name: str,
        operation_name: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
        exception: Optional[Exception] = None,
    ) -> str:
        """Process API-related errors"""
        logger = ErrorHandler._get_logger(logger_name)

        if exception:
            if "Timeout" in str(type(exception).__name__):
                error_msg = f"{operation_name} timeout"
                logger.error(error_msg)
                return f"{operation_name} timed out"
            elif "ConnectionError" in str(type(exception).__name__):
                error_msg = f"{operation_name} connection error: {str(exception)}"
                logger.error(error_msg)
                return f"{operation_name} connection error occurred"
            else:
                error_msg = f"{operation_name} unexpected error: {str(exception)}"
                logger.exception(error_msg)
                return f"{operation_name} unexpected error occurred: {str(exception)}"

        if status_code and status_code != 200:
            error_msg = f"{operation_name} API error - status: {status_code}, content: {response_text}"
            logger.error(error_msg)
            return f"{operation_name} error occurred: {status_code}"

        return f"{operation_name} unknown error occurred"
                