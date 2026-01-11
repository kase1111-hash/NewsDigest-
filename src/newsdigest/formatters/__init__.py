"""Output formatters for NewsDigest."""

from newsdigest.formatters.base import BaseFormatter
from newsdigest.formatters.json import JSONFormatter
from newsdigest.formatters.markdown import MarkdownFormatter
from newsdigest.formatters.text import TextFormatter


__all__ = [
    "BaseFormatter",
    "JSONFormatter",
    "MarkdownFormatter",
    "TextFormatter",
    # Future formatters:
    # "HTMLFormatter",
    # "EmailFormatter",
]
