"""HTML cleaner for NewsDigest."""

import re
from typing import List, Optional, Set

from bs4 import BeautifulSoup, Comment, NavigableString, Tag


# Elements to completely remove
REMOVE_ELEMENTS: Set[str] = {
    "script",
    "style",
    "noscript",
    "iframe",
    "embed",
    "object",
    "svg",
    "canvas",
    "video",
    "audio",
    "map",
    "form",
    "input",
    "button",
    "select",
    "textarea",
}

# Elements typically containing non-content
NON_CONTENT_ELEMENTS: Set[str] = {
    "nav",
    "header",
    "footer",
    "aside",
    "menu",
    "menuitem",
}

# Classes/IDs that typically indicate non-content
NON_CONTENT_PATTERNS: List[str] = [
    r"nav",
    r"menu",
    r"sidebar",
    r"widget",
    r"ad[s-]?",
    r"advert",
    r"sponsor",
    r"promo",
    r"banner",
    r"social",
    r"share",
    r"comment",
    r"footer",
    r"header",
    r"masthead",
    r"breadcrumb",
    r"pagination",
    r"related",
    r"recommend",
    r"popular",
    r"trending",
    r"subscribe",
    r"newsletter",
    r"signup",
    r"login",
    r"modal",
    r"popup",
    r"overlay",
    r"cookie",
    r"consent",
    r"gdpr",
]


class HTMLCleaner:
    """Cleans HTML and extracts text content.

    Removes:
    - Scripts, styles, iframes
    - Navigation, headers, footers
    - Ads, sidebars
    - Comments
    - Non-content elements based on class/id patterns
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize HTML cleaner.

        Args:
            config: Configuration dictionary.
        """
        self.config = config or {}
        self._non_content_pattern = re.compile(
            "|".join(NON_CONTENT_PATTERNS), re.IGNORECASE
        )
        self.preserve_links = self.config.get("preserve_links", False)
        self.preserve_images = self.config.get("preserve_images", False)

    def clean(self, html: str) -> str:
        """Remove non-content elements and extract clean text.

        Args:
            html: Raw HTML content.

        Returns:
            Cleaned text content.
        """
        if not html:
            return ""

        # Parse HTML
        soup = BeautifulSoup(html, "lxml")

        # Remove comments
        for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
            comment.extract()

        # Remove script, style, and other non-content elements
        for element in soup.find_all(REMOVE_ELEMENTS):
            element.decompose()

        # Remove non-content structural elements
        for element in soup.find_all(NON_CONTENT_ELEMENTS):
            element.decompose()

        # Remove elements with non-content class/id patterns
        self._remove_by_attribute(soup)

        # Get text
        text = self._extract_text(soup)

        # Clean up whitespace
        text = self._clean_whitespace(text)

        return text

    def _remove_by_attribute(self, soup: BeautifulSoup) -> None:
        """Remove elements based on class/id attributes.

        Args:
            soup: BeautifulSoup object to modify in place.
        """
        for element in soup.find_all(True):  # True matches all tags
            if not isinstance(element, Tag):
                continue

            # Check class attribute
            classes = element.get("class", [])
            if isinstance(classes, list):
                class_str = " ".join(classes)
            else:
                class_str = str(classes)

            # Check id attribute
            elem_id = element.get("id", "") or ""

            # Check role attribute
            role = element.get("role", "") or ""

            # Remove if matches non-content pattern
            combined = f"{class_str} {elem_id} {role}"
            if self._non_content_pattern.search(combined):
                element.decompose()

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract text from cleaned soup.

        Args:
            soup: Cleaned BeautifulSoup object.

        Returns:
            Extracted text.
        """
        # Get main content area if identifiable
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find(attrs={"role": "main"})
            or soup.find(class_=re.compile(r"content|article|post|entry"))
        )

        target = main if main else soup

        # Extract text with paragraph preservation
        paragraphs = []
        for element in target.descendants:
            if isinstance(element, NavigableString):
                text = str(element).strip()
                if text:
                    paragraphs.append(text)
            elif isinstance(element, Tag) and element.name in [
                "p",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "li",
                "blockquote",
            ]:
                text = element.get_text(separator=" ", strip=True)
                if text:
                    paragraphs.append(text)

        # Deduplicate adjacent identical paragraphs
        unique_paragraphs = []
        for p in paragraphs:
            if not unique_paragraphs or p != unique_paragraphs[-1]:
                unique_paragraphs.append(p)

        return "\n\n".join(unique_paragraphs)

    def _clean_whitespace(self, text: str) -> str:
        """Clean up whitespace in text.

        Args:
            text: Text to clean.

        Returns:
            Cleaned text.
        """
        # Replace multiple spaces with single space
        text = re.sub(r"[ \t]+", " ", text)

        # Replace multiple newlines with double newline (paragraph break)
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        return text.strip()

    def get_links(self, html: str) -> List[dict]:
        """Extract links from HTML.

        Args:
            html: HTML content.

        Returns:
            List of link dictionaries with href and text.
        """
        soup = BeautifulSoup(html, "lxml")
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if href and text:
                links.append({"href": href, "text": text})

        return links

    def get_images(self, html: str) -> List[dict]:
        """Extract images from HTML.

        Args:
            html: HTML content.

        Returns:
            List of image dictionaries with src and alt.
        """
        soup = BeautifulSoup(html, "lxml")
        images = []

        for img in soup.find_all("img", src=True):
            src = img["src"]
            alt = img.get("alt", "")
            if src:
                images.append({"src": src, "alt": alt})

        return images
