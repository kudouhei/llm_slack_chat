from typing import Optional

from ..logger_config import get_logger

class LoggingMixin:
    """Mixin class for logging"""

    def __init__(self, logger_name: str):
        """Initialize the logger"""
        self.logger = get_logger(logger_name)

    def log_initialization_start(self, class_name: str, **details):
        """Log the start of the initialization of the class"""
        detail_str = (
            ", ".join([f"{k}: {v}" for k, v in details.items()]) if details else ""
        )

        msg = f"Initializing {class_name}"
        if detail_str:
            msg += f" - {detail_str}"

        self.logger.info(msg)

    def log_initialization_end(self, class_name: str):
        """Log the end of the initialization of the class"""
        self.logger.info(f"Initialize completed {class_name}")

    def log_operation_start(self, operation_name: str, **details):
        """Log the start of an operation"""
        detail_str = (
            ", ".join([f"{k}: {v}" for k, v in details.items()]) if details else ""
        )
        msg = f"Starting {operation_name}"
        if detail_str:
            msg += f" - {detail_str}"

        self.logger.info(msg)
        
    def log_operation_end(self, operation_name: str, **details):
        """Log the end of an operation"""
        detail_str = (
            ", ".join([f"{k}: {v}" for k, v in details.items()]) if details else ""
        )
        msg = f"Completed {operation_name}"
        if detail_str:
            msg += f" - {detail_str}"

        self.logger.info(msg)

    def log_api_request(self, api_name: str, method: str = "POST", **params):
        """Log an API request"""
        detail_str = (
            ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else ""
        )
        msg = f"{api_name} API {method} request"
        if detail_str:
            msg += f" - {detail_str}"
        self.logger.info(msg)

    def log_api_response(self, api_name: str, status_code: int, **details):
        """API response log"""
        detail_str = (
            ", ".join([f"{k}: {v}" for k, v in details.items()]) if details else ""
        )
        msg = f"{api_name} API response received - status: {status_code}"
        if detail_str:
            msg += f", {detail_str}"
        self.logger.info(msg)

    def log_api_success(self, api_name: str, **details):
        """API success log"""
        detail_str = (
            ", ".join([f"{k}: {v}" for k, v in details.items()]) if details else ""
        )
        msg = f"{api_name} API success"
        if detail_str:
            msg += f" - {detail_str}"
        self.logger.info(msg)

    def log_error(self, error_msg: str, exception: Optional[Exception] = None):
        """Error log"""
        if exception:
            self.logger.exception(error_msg)
        else:
            self.logger.error(error_msg)

    def log_warning(self, warning_msg: str):
        """Warning log"""
        self.logger.warning(warning_msg)

    def log_debug(self, debug_msg: str):
        """Debug log"""
        self.logger.debug(debug_msg)

    def log_user_action(self, action: str, user: str, **details):
        """User action log"""
        detail_str = (
            ", ".join([f"{k}: {v}" for k, v in details.items()]) if details else ""
        )
        msg = f"{action} - user: {user}"
        if detail_str:
            msg += f", {detail_str}"
        self.logger.info(msg)

    def log_database_operation(self, operation: str, table: str = "", **details):
        """Database operation log"""
        detail_str = (
            ", ".join([f"{k}: {v}" for k, v in details.items()]) if details else ""
        )
        msg = f"DB {operation}"
        if table:
            msg += f" - table: {table}"
        if detail_str:
            msg += f", {detail_str}"
        self.logger.debug(msg)


            

        
        