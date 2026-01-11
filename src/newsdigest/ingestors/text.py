"""Text ingestor for NewsDigest."""

import hashlib
from typing import List, Optional

from newsdigest.core.article import Article, SourceType
from newsdigest.ingestors.base import BaseIngestor


class TextIngestor(BaseIngestor):
    """Ingests plain text content directly.

    Used for:
    - Direct text input from CLI
    - Copy-pasted article content
    - File content
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize text ingestor.

        Args:
            config: Configuration dictionary.
        """
        super().__init__(config)

    async def ingest(self, source: str) -> Article:
        """Create article from text content.

        Args:
            source: Plain text content.

        Returns:
            Article object.
        """
        return self.from_text(source)

    async def ingest_batch(self, sources: List[str]) -> List[Article]:
        """Create articles from multiple text sources.

        Args:
            sources: List of text content.

        Returns:
            List of Article objects.
        """
        return [self.from_text(text) for text in sources]

    def from_text(
        self,
        text: str,
        title: Optional[str] = None,
        source_name: Optional[str] = None,
        url: Optional[str] = None,
    ) -> Article:
        """Create article from plain text.

        Args:
            text: Plain text content.
            title: Optional title.
            source_name: Optional source name.
            url: Optional URL reference.

        Returns:
            Article object.
        """
        # Clean up text
        text = text.strip()

        # Generate ID from content
        article_id = hashlib.sha256(text.encode()).hexdigest()[:16]

        # Try to extract title from first line if not provided
        if not title and text:
            lines = text.split("\n")
            first_line = lines[0].strip()
            # Use first line as title if short enough
            if len(first_line) <= 200 and len(lines) > 1:
                title = first_line
                text = "\n".join(lines[1:]).strip()

        return Article(
            id=article_id,
            content=text,
            url=url,
            title=title,
            source_name=source_name or "Direct Input",
            source_type=SourceType.TEXT,
        )

    def from_file(self, file_path: str) -> Article:
        """Create article from file.

        Args:
            file_path: Path to text file.

        Returns:
            Article object.

        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        return self.from_text(content, source_name=file_path)

    def from_stdin(self) -> Article:
        """Create article from stdin.

        Returns:
            Article object.
        """
        import sys

        content = sys.stdin.read()
        return self.from_text(content, source_name="stdin")
