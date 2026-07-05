"""Custom application exceptions."""


class AnalysisError(Exception):
    """Base exception for analysis failures."""


class UploadValidationError(AnalysisError):
    """Raised when an uploaded archive is invalid."""


class NotFoundError(AnalysisError):
    """Raised when a stored analysis does not exist."""

