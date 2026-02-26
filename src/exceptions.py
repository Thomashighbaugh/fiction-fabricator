"""
Custom exception classes for Fiction Fabricator.

This module provides structured exception handling with specific exception types
for different error scenarios across the application.
"""


class FictionFabricatorError(Exception):
    """Base exception for all Fiction Fabricator errors."""

    pass


# LLM-related exceptions
class LLMError(FictionFabricatorError):
    """Base exception for LLM-related errors."""

    pass


class LLMAPIError(LLMError):
    """Raised when LLM API calls fail."""

    pass


class LLMRateLimitError(LLMError):
    """Raised when LLM API rate limit is exceeded."""

    pass


class LLMAuthenticationError(LLMError):
    """Raised when LLM API authentication fails."""

    pass


class LLMContextLengthError(LLMError):
    """Raised when LLM context length is exceeded."""

    pass


class LLMResponseError(LLMError):
    """Raised when LLM response is invalid or incomplete."""

    pass


# Project-related exceptions
class ProjectError(FictionFabricatorError):
    """Base exception for project-related errors."""

    pass


class ProjectNotFoundError(ProjectError):
    """Raised when a project cannot be found."""

    pass


class ProjectLoadError(ProjectError):
    """Raised when a project fails to load."""

    pass


class ProjectSaveError(ProjectError):
    """Raised when a project fails to save."""

    pass


class ProjectValidationError(ProjectError):
    """Raised when project data fails validation."""

    pass


# XML-related exceptions
class XMLError(FictionFabricatorError):
    """Base exception for XML processing errors."""

    pass


class XMLParseError(XMLError):
    """Raised when XML parsing fails."""

    pass


class XMLValidationError(XMLError):
    """Raised when XML validation fails."""

    pass


class XMLStructureError(XMLError):
    """Raised when XML structure is invalid or incomplete."""

    pass


# Export-related exceptions
class ExportError(FictionFabricatorError):
    """Base exception for export-related errors."""

    pass


class ExportFormatError(ExportError):
    """Raised when export format is invalid or unsupported."""

    pass


class ExportGenerationError(ExportError):
    """Raised when export generation fails."""

    pass


# Lorebook-related exceptions
class LorebookError(FictionFabricatorError):
    """Base exception for lorebook-related errors."""

    pass


class LorebookLoadError(LorebookError):
    """Raised when lorebook fails to load."""

    pass


class LorebookSaveError(LorebookError):
    """Raised when lorebook fails to save."""

    pass


class LorebookValidationError(LorebookError):
    """Raised when lorebook data fails validation."""

    pass


# Configuration-related exceptions
class ConfigurationError(FictionFabricatorError):
    """Base exception for configuration-related errors."""

    pass


class ConfigurationValidationError(ConfigurationError):
    """Raised when configuration validation fails."""

    pass


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""

    pass


# User input exceptions
class UserInputError(FictionFabricatorError):
    """Base exception for user input errors."""

    pass


class UserCancelledError(UserInputError):
    """Raised when user cancels an operation."""

    pass


class InvalidInputError(UserInputError):
    """Raised when user provides invalid input."""

    pass


# Content generation exceptions
class ContentGenerationError(FictionFabricatorError):
    """Base exception for content generation errors."""

    pass


class OutlineGenerationError(ContentGenerationError):
    """Raised when outline generation fails."""

    pass


class ChapterGenerationError(ContentGenerationError):
    """Raised when chapter generation fails."""

    pass


class ContentOptimizationError(ContentGenerationError):
    """Raised when content optimization fails."""

    pass
