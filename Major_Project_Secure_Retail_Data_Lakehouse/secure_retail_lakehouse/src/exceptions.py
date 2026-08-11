"""
exceptions.py
-------------
Custom exceptions so pipeline failures are specific and actionable
instead of generic tracebacks. Each one maps to a distinct failure
mode an operator would need to react to differently.
"""


class LakehousePipelineError(Exception):
    """Base class for all pipeline-specific errors."""


class SourceFileError(LakehousePipelineError):
    """Raised when the raw source file is missing, empty, or unreadable."""


class SchemaValidationError(LakehousePipelineError):
    """Raised when an input dataset is missing required columns."""


class NoValidRowsError(LakehousePipelineError):
    """Raised when every row in a batch fails data-quality checks --
    i.e. there is nothing left to safely process."""


class PIILeakageError(LakehousePipelineError):
    """Raised if a raw, unmasked identifier is detected in a layer that
    must never contain it. This is the last line of defense: even if
    an upstream transform is buggy, this stops the pipeline before a
    sensitive column reaches Silver/Gold output."""
