import json
import requests

from typing import Any, Dict, Optional, Union

from ..logger_config import get_logger

class APIUtils:
    """API utility functions"""

    @staticmethod
    def _get_logger(logger_name: str):
        """Get the logger"""
        return get_logger(logger_name)
    
    @staticmethod
    def make_api_request(
        method: str,
        url: str,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        logger_name: str = "api_utils",
    ) -> requests.Response:
        """Make an API request"""
        logger = APIUtils._get_logger(logger_name)

        try:
            logger.debug(f"HTTP {method} request started - URL: {url}")
            if payload:
                logger.debug(f"Payload size: {len(json.dumps(payload))} bytes")

            response = requests.request(
                method=method, url=url, json=payload, headers=headers, timeout=timeout
            )

            logger.debug(f"HTTP response received - status: {response.status_code}")
            return response

        except requests.exceptions.Timeout:
            logger.error(
                f"HTTP request timeout - URL: {url}, timeout: {timeout} seconds"
            )
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"HTTP connection error - URL: {url}, error: {str(e)}")
            raise
        except Exception as e:
            logger.exception(
                f"Unexpected error during HTTP request - URL: {url}, error: {str(e)}"
            )
            raise

    @staticmethod
    def handle_api_response(
        response: requests.Response,
        success_codes: tuple = (200, 201, 202),
        logger_name: str = "api_utils",
    ) -> Union[Dict[str, Any], str]:
        """Common processing of API responses"""
        logger = APIUtils._get_logger(logger_name)

        if response.status_code in success_codes:
            try:
                result = response.json()
                logger.debug(
                    f"API response parsing successful - data size: {len(str(result))}"
                )
                return result
            except (json.JSONDecodeError, ValueError):
                logger.warning(
                    "API response is not JSON - returned as text"
                )
                return response.text
        else:
            error_msg = f"API error - status: {response.status_code}, content: {response.text}"
            logger.error(error_msg)
            raise requests.HTTPError(error_msg, response=response)    
        
    @staticmethod
    def extract_api_error_info(exception: Exception) -> Dict[str, Any]:
        """Extract detailed information from API exception"""
        error_info = {
            "type": type(exception).__name__,
            "message": str(exception),
            "is_timeout": False,
            "is_connection_error": False,
            "is_http_error": False,
            "status_code": None,
            "response_text": None,
        }

        if isinstance(exception, requests.exceptions.Timeout):
            error_info["is_timeout"] = True
        elif isinstance(exception, requests.exceptions.ConnectionError):
            error_info["is_connection_error"] = True
        elif isinstance(exception, requests.HTTPError):
            error_info["is_http_error"] = True
            if hasattr(exception, "response") and exception.response:
                error_info["status_code"] = exception.response.status_code
                error_info["response_text"] = exception.response.text

        return error_info

    @staticmethod
    def format_user_friendly_error(
        exception: Exception, service_name: str = "API"
    ) -> str:
        """Generate a user-friendly error message"""
        error_info = APIUtils.extract_api_error_info(exception)

        if error_info["is_timeout"]:
            return f"{service_name} request timed out"
        elif error_info["is_connection_error"]:
            return f"{service_name} could not connect to the server"
        elif error_info["is_http_error"]:
            status = error_info["status_code"]
            return f"{service_name} error occurred: {status}"
        else:
            return f"{service_name} unexpected error occurred: {str(exception)}"

    @staticmethod
    def create_request_headers(
        content_type: str = "application/json",
        auth_token: Optional[str] = None,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Create request headers"""
        headers = {"Content-Type": content_type}

        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        if additional_headers:
            headers.update(additional_headers)

        return headers
