"""Exceptions thrown by this module."""

class HerrforsScraperError(Exception):
    """Base error class."""

class CreateSessionError(HerrforsScraperError):
    """Error raised when a session cannot be created."""

class UnknownTypeError(HerrforsScraperError):
    """Error raised when an unknown scrape type is given."""

class NoDataError(HerrforsScraperError):
    """Error raised when no data was received."""

class TooLittleDataReceivedError(HerrforsScraperError):
    """Error raised when too little data was received."""
