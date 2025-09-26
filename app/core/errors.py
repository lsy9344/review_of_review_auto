"""Application error types."""


class LoginError(Exception):
    """Raised when login fails or credentials are invalid."""


class DomMismatchError(Exception):
    """Raised when the expected DOM structure is not present."""


class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""


class RateLimitError(Exception):
    """Raised when an action is blocked due to rate limiting or throttling."""


class StoreEnumerationError(Exception):
    """Raised when store enumeration fails."""


class ReviewAPIAuthError(Exception):
    """Raised when review API authentication fails."""
