class FocusAnalyticsError(Exception):
    """Base exception for focus analytics module"""
    pass

class InvalidDateError(FocusAnalyticsError):
    """Raised when date parameters are invalid"""
    pass

class EmptyDataError(FocusAnalyticsError):
    """Raised when required data is empty"""
    pass

class InvalidSessionError(FocusAnalyticsError):
    """Raised when focus session data is invalid"""
    pass

class FileExportError(FocusAnalyticsError):
    """Raised when file export fails"""
    pass