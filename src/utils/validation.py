import re
import os

from typing import Optional, Dict, Any, List, Union

from ..logger_config import get_logger

class ValidationError(ValueError):
    """ validation error"""
    pass

class Validator:
    """Validator class"""

    @staticmethod
    def _get_logger(logger_name: str):
        """Get the logger"""
        return get_logger(logger_name)
    
    @staticmethod
    def require_non_empty(value: Any, field_name: str, logger_name: str = "validator") -> None:
        """Require non-empty value"""
        logger = Validator._get_logger(logger_name)

        if not value or (isinstance(value, str) and not value.strip()):
            logger.error(f"Field {field_name} cannot be empty")
            raise ValidationError(f"Field {field_name} cannot be empty")
        
        logger.debug(f"Validation successful: {field_name}")
        
    @staticmethod
    def validate_url(url: str, field_name: str, logger_name: str = "validator") -> None:
        """Validate URL"""
        logger = Validator._get_logger(logger_name)
        
        url_pattern = re.compile(
            r"^https?://"  # schema
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain name
            r"localhost|"  # localhost allowed
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP address
            r"(?::\d+)?"  # port number
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if not url_pattern.match(url):
            logger.error(f"Invalid URL: {url}")
            raise ValidationError(f"Invalid URL: {url}")
        
        logger.debug(f"Validation successful: {field_name}")
        
    @staticmethod
    def validate_positive_integer(
        value: Union[int, str],
        field_name: str,
        min_value: int = 1,
        max_value: Optional[int] = None,
        logger_name: str = "validator",
    ) -> int:   
        """Validate positive integer"""
        logger = Validator._get_logger(logger_name)
        
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            error_msg = f"{field_name} must be an integer"
            logger.error(f"Validation error: {error_msg}")
            raise ValidationError(error_msg)

        if int_value < min_value:
            error_msg = f"{field_name} must be at least {min_value}"
            logger.error(f"Validation error: {error_msg}")
            raise ValidationError(error_msg)

        if max_value is not None and int_value > max_value:
            error_msg = f"{field_name} must be at most {max_value}"
            logger.error(f"Validation error: {error_msg}")
            raise ValidationError(error_msg)

        logger.debug(f"Integer validation successful: {field_name} = {int_value}")
        return int_value
    
    @staticmethod
    def validate_enum(
        value: str,
        valid_values: List[str],
        field_name: str,
        case_sensitive: bool = False,
        logger_name: str = "validator",
    ) -> str:
        """Validate enum"""
        logger = Validator._get_logger(logger_name)

        check_value = value if case_sensitive else value.upper()
        check_list = (
            valid_values if case_sensitive else [v.upper() for v in valid_values]
        )

        if check_value not in check_list:
            error_msg = f"{field_name} must be one of {valid_values}"
            logger.error(f"Validation error: {error_msg}")
            raise ValidationError(error_msg)

        logger.debug(f"Enum validation successful: {field_name} = {value}")
        return value
    
    @staticmethod
    def validate_token_format(
        token: str,
        field_name: str,
        expected_prefix: Optional[str] = None,
        logger_name: str = "validator",
    ) -> None:
        """Validate token format"""
        logger = Validator._get_logger(logger_name)

        if not token or not isinstance(token, str):
            error_msg = f"{field_name} must be a non-empty string"
            logger.error(f"Validation error: {error_msg}")
            raise ValidationError(error_msg)

        if expected_prefix and not token.startswith(expected_prefix):
            error_msg = f"{field_name} must start with '{expected_prefix}'"
            logger.error(f"Validation error: {error_msg}")
            raise ValidationError(error_msg)

        # Basic token format check (alphanumeric and hyphens)
        if not re.match(r"^[a-zA-Z0-9\-_]+$", token):
            error_msg = f"{field_name} contains invalid characters"
            logger.error(f"Validation error: {error_msg}")
            raise ValidationError(error_msg)

        logger.debug(f"Token validation successful: {field_name}")

    @staticmethod
    def validate_batch(
        validations: List[Dict[str, Any]], logger_name: str = "validator"
    ) -> None:
        """Execute multiple validations in batch"""
        logger = Validator._get_logger(logger_name)
        errors = []

        for validation in validations:
            try:
                method = validation["method"]
                args = validation.get("args", [])
                kwargs = validation.get("kwargs", {})
                method(*args, **kwargs)
            except ValidationError as e:
                errors.append(str(e))

        if errors:
            combined_error = "; ".join(errors)
            logger.error(f"Batch validation error: {combined_error}")
            raise ValidationError(combined_error)

        logger.debug("Batch validation successful")
        
        
        

