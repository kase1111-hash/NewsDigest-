# NewsDigest Technical Specification

**Version:** 0.1.0
**Last Updated:** 2026-01-11
**Status:** Implementation Ready

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Project Structure](#3-project-structure)
4. [Core Data Models](#4-core-data-models)
5. [Module Specifications](#5-module-specifications)
6. [CLI Specification](#6-cli-specification)
7. [API Specification](#7-api-specification)
8. [Configuration Schema](#8-configuration-schema)
9. [Dependencies](#9-dependencies)
10. [Testing Requirements](#10-testing-requirements)
11. [Implementation Phases](#11-implementation-phases)

---

## 1. Overview

### 1.1 Purpose
NewsDigest is a semantic compression engine that extracts signal from news articles by removing filler, speculation, and engagement-optimized content while preserving factual claims and attributed sources.

### 1.2 Core Capabilities
- **Filler Detection**: Identify sentences with no information content
- **Speculation Stripping**: Remove "could," "might," "may indicate" padding
- **Source Validation**: Flag "sources say" without named attribution
- **Emotional Deactivation**: Strip "shocking," "alarming," "unprecedented"
- **Repetition Collapse**: Merge repeated information across paragraphs
- **Novelty Scoring**: Identify what's new vs. restated background
- **Claim Extraction**: Pull falsifiable statements from narrative wrapper
- **Quote Isolation**: Separate direct quotes from paraphrase

### 1.3 Tech Stack
- **Language**: Python 3.11+
- **Package Manager**: pip/pipx
- **NLP Libraries**: spaCy, transformers (optional for enhanced extraction)
- **HTTP Client**: httpx (async support)
- **HTML Parsing**: BeautifulSoup4, lxml
- **RSS Parsing**: feedparser
- **CLI Framework**: Click or Typer
- **Configuration**: PyYAML, python-dotenv
- **Testing**: pytest, pytest-asyncio, pytest-cov

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          INPUT LAYER                                 │
├───────────┬───────────┬───────────┬───────────┬───────────┬─────────┤
│    URL    │    RSS    │  NewsAPI  │   Email   │  Twitter  │   PDF   │
│  Fetcher  │  Parser   │  Client   │  Ingester │  Client   │ Parser  │
└─────┬─────┴─────┬─────┴─────┬─────┴─────┬─────┴─────┬─────┴────┬────┘
      │           │           │           │           │          │
      └───────────┴───────────┴─────┬─────┴───────────┴──────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       CONTENT PARSER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │   HTML      │  │   Article   │  │  Metadata   │                  │
│  │   Cleaner   │  │   Extractor │  │   Parser    │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     EXTRACTION ENGINE                                │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    NLP Pipeline                              │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │    │
│  │  │Tokenizer│→│  POS    │→│  NER    │→│Sentence │            │    │
│  │  │         │ │ Tagger  │ │         │ │Segmenter│            │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │  Filler     │ │ Speculation │ │  Source     │ │  Emotional  │   │
│  │  Detector   │ │  Stripper   │ │  Validator  │ │  Detector   │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ Repetition  │ │  Novelty    │ │   Claim     │ │   Quote     │   │
│  │  Collapser  │ │   Scorer    │ │  Extractor  │ │  Isolator   │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │  Markdown   │ │    HTML     │ │    JSON     │ │    Email    │   │
│  │  Formatter  │ │  Formatter  │ │  Formatter  │ │   Sender    │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
Article URL/Content
        │
        ▼
┌───────────────────┐
│   Fetch/Parse     │ → Raw HTML/Text
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Content Extraction│ → Article object (title, body, metadata)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  NLP Processing   │ → Sentences, Entities, POS tags
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Semantic Analysis │ → Scored sentences, claims, sources
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│    Compression    │ → ExtractionResult
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   Formatting      │ → Output (md/html/json/email)
└───────────────────┘
```

---

## 3. Project Structure

```
newsdigest/
├── pyproject.toml              # Project metadata, dependencies
├── setup.py                    # Backward compat (optional)
├── README.md                   # Documentation
├── SPEC.md                     # This file
├── LICENSE.md                  # Polyform Small Business License
├── CHANGELOG.md                # Version history
├── .env.example                # Environment template
├── .gitignore
│
├── src/
│   └── newsdigest/
│       ├── __init__.py         # Package exports
│       ├── __main__.py         # CLI entry point
│       ├── version.py          # Version info
│       │
│       ├── cli/                # CLI commands
│       │   ├── __init__.py
│       │   ├── main.py         # Main CLI app
│       │   ├── extract.py      # extract command
│       │   ├── compare.py      # compare command
│       │   ├── stats.py        # stats command
│       │   ├── digest.py       # digest command
│       │   ├── watch.py        # watch command
│       │   ├── sources.py      # sources command
│       │   ├── analytics.py    # analytics command
│       │   └── setup.py        # setup command
│       │
│       ├── core/               # Core extraction engine
│       │   ├── __init__.py
│       │   ├── extractor.py    # Main Extractor class
│       │   ├── pipeline.py     # NLP pipeline orchestration
│       │   ├── article.py      # Article data structures
│       │   └── result.py       # ExtractionResult class
│       │
│       ├── analyzers/          # Semantic analysis modules
│       │   ├── __init__.py
│       │   ├── base.py         # BaseAnalyzer abstract class
│       │   ├── filler.py       # FillerDetector
│       │   ├── speculation.py  # SpeculationStripper
│       │   ├── sources.py      # SourceValidator
│       │   ├── emotional.py    # EmotionalDetector
│       │   ├── repetition.py   # RepetitionCollapser
│       │   ├── novelty.py      # NoveltyScorer
│       │   ├── claims.py       # ClaimExtractor
│       │   └── quotes.py       # QuoteIsolator
│       │
│       ├── ingestors/          # Input source handlers
│       │   ├── __init__.py
│       │   ├── base.py         # BaseIngestor abstract class
│       │   ├── url.py          # URLFetcher
│       │   ├── rss.py          # RSSParser
│       │   ├── newsapi.py      # NewsAPIClient
│       │   ├── email.py        # EmailIngester
│       │   ├── twitter.py      # TwitterClient
│       │   └── pdf.py          # PDFParser
│       │
│       ├── parsers/            # Content parsing
│       │   ├── __init__.py
│       │   ├── html.py         # HTMLCleaner
│       │   ├── article.py      # ArticleExtractor (readability)
│       │   └── metadata.py     # MetadataParser
│       │
│       ├── formatters/         # Output formatters
│       │   ├── __init__.py
│       │   ├── base.py         # BaseFormatter abstract class
│       │   ├── markdown.py     # MarkdownFormatter
│       │   ├── html.py         # HTMLFormatter
│       │   ├── json.py         # JSONFormatter
│       │   ├── text.py         # TextFormatter
│       │   └── email.py        # EmailFormatter
│       │
│       ├── digest/             # Digest generation
│       │   ├── __init__.py
│       │   ├── generator.py    # DigestGenerator class
│       │   ├── clustering.py   # TopicClusterer
│       │   ├── dedup.py        # Deduplicator
│       │   └── threading.py    # StoryThreader
│       │
│       ├── api/                # REST API (v0.2)
│       │   ├── __init__.py
│       │   ├── app.py          # FastAPI application
│       │   ├── routes/
│       │   │   ├── extract.py
│       │   │   ├── digest.py
│       │   │   └── webhooks.py
│       │   └── models.py       # Pydantic models
│       │
│       ├── storage/            # Data persistence
│       │   ├── __init__.py
│       │   ├── cache.py        # Content cache
│       │   ├── analytics.py    # Analytics storage
│       │   └── sources.py      # Source management
│       │
│       ├── config/             # Configuration
│       │   ├── __init__.py
│       │   ├── settings.py     # Settings class
│       │   ├── schema.py       # Config validation
│       │   └── defaults.py     # Default values
│       │
│       └── utils/              # Utilities
│           ├── __init__.py
│           ├── http.py         # HTTP client wrapper
│           ├── text.py         # Text utilities
│           ├── logging.py      # Logging setup
│           └── metrics.py      # Metrics collection
│
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/
│   │   ├── test_extractor.py
│   │   ├── test_analyzers/
│   │   ├── test_ingestors/
│   │   ├── test_parsers/
│   │   └── test_formatters/
│   ├── integration/
│   │   ├── test_pipeline.py
│   │   ├── test_digest.py
│   │   └── test_api.py
│   └── fixtures/
│       ├── articles/           # Sample articles
│       └── expected/           # Expected outputs
│
├── docs/
│   ├── api.md                  # API documentation
│   ├── configuration.md        # Config reference
│   └── architecture.md         # Architecture details
│
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

---

## 4. Core Data Models

### 4.1 Article

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

class SourceType(Enum):
    URL = "url"
    RSS = "rss"
    NEWSAPI = "newsapi"
    EMAIL = "email"
    TWITTER = "twitter"
    PDF = "pdf"

@dataclass
class Article:
    """Represents a parsed news article."""

    # Required fields
    id: str                          # Unique identifier (hash of URL/content)
    content: str                     # Raw text content

    # Metadata
    url: Optional[str] = None
    title: Optional[str] = None
    source_name: Optional[str] = None
    source_type: SourceType = SourceType.URL
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    fetched_at: datetime = field(default_factory=datetime.utcnow)

    # Computed fields
    word_count: int = 0
    language: str = "en"
```

### 4.2 Sentence

```python
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class SentenceCategory(Enum):
    FACTUAL = "factual"
    SPECULATION = "speculation"
    EMOTIONAL = "emotional"
    BACKGROUND = "background"
    QUOTE = "quote"
    FILLER = "filler"
    ENGAGEMENT_HOOK = "engagement_hook"

@dataclass
class Sentence:
    """Represents an analyzed sentence."""

    text: str
    index: int                       # Position in article

    # NLP data
    tokens: List[str] = field(default_factory=list)
    pos_tags: List[str] = field(default_factory=list)
    entities: List[dict] = field(default_factory=list)

    # Analysis scores
    density_score: float = 0.0       # 0.0 - 1.0
    novelty_score: float = 0.0       # 0.0 - 1.0
    speculation_score: float = 0.0   # 0.0 - 1.0
    emotional_score: float = 0.0     # 0.0 - 1.0

    # Classification
    category: SentenceCategory = SentenceCategory.FACTUAL
    keep: bool = True
    removal_reason: Optional[str] = None

    # Source attribution
    has_named_source: bool = False
    has_unnamed_source: bool = False
    source_name: Optional[str] = None
```

### 4.3 Claim

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class ClaimType(Enum):
    FACTUAL = "factual"
    STATISTICAL = "statistical"
    QUOTE = "quote"
    ATTRIBUTION = "attribution"

@dataclass
class Claim:
    """Represents an extracted falsifiable claim."""

    text: str
    claim_type: ClaimType

    # Attribution
    source: Optional[str] = None     # Named source if available
    source_type: str = "unknown"     # primary, quoted, official, etc.

    # Confidence
    confidence: float = 0.0          # 0.0 - 1.0

    # Position
    sentence_index: int = 0
```

### 4.4 RemovedContent

```python
from dataclasses import dataclass
from enum import Enum

class RemovalReason(Enum):
    EMOTIONAL_ACTIVATION = "EMOTIONAL_ACTIVATION"
    SPECULATION = "SPECULATION"
    UNNAMED_SOURCE = "UNNAMED_SOURCE"
    BACKGROUND_REPEAT = "BACKGROUND_REPEAT"
    CIRCULAR_QUOTE = "CIRCULAR_QUOTE"
    HEDGE_PADDING = "HEDGE_PADDING"
    ENGAGEMENT_HOOK = "ENGAGEMENT_HOOK"
    LOW_DENSITY = "LOW_DENSITY"

@dataclass
class RemovedContent:
    """Represents content that was removed during extraction."""

    text: str
    reason: RemovalReason
    sentence_index: int
    original_length: int = 0         # Word count of original

    # For hedge padding
    compressed_version: Optional[str] = None
```

### 4.5 ExtractionResult

```python
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class ExtractionStatistics:
    """Statistics about the extraction process."""

    original_words: int = 0
    compressed_words: int = 0
    compression_ratio: float = 0.0
    original_density: float = 0.0
    compressed_density: float = 0.0

    # Breakdown
    novel_claims: int = 0
    background_removed: int = 0      # Sentence count
    speculation_removed: int = 0     # Sentence count
    repetition_collapsed: int = 0    # Sentence count
    emotional_words_removed: int = 0 # Word count
    unnamed_sources: int = 0         # Count flagged
    named_sources: int = 0

@dataclass
class ExtractionResult:
    """Complete result of article extraction."""

    # Identifiers
    id: str
    url: Optional[str] = None

    # Article metadata
    title: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    processed_at: datetime = field(default_factory=datetime.utcnow)

    # Extracted content
    text: str = ""                   # Compressed text
    claims: List[Claim] = field(default_factory=list)

    # Named sources found
    sources_named: List[str] = field(default_factory=list)

    # Warnings (kept but flagged)
    warnings: List[dict] = field(default_factory=list)

    # Removed content
    removed: List[RemovedContent] = field(default_factory=list)

    # Statistics
    statistics: ExtractionStatistics = field(default_factory=ExtractionStatistics)

    # Original for comparison mode
    original_text: Optional[str] = None
    sentences: List[Sentence] = field(default_factory=list)
```

### 4.6 DigestItem

```python
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class DigestItem:
    """A single item in a digest."""

    id: str
    summary: str

    # Aggregation info
    article_count: int = 1
    sources: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)

    # Topic
    topic: Optional[str] = None
    subtopic: Optional[str] = None

    # Timestamps
    earliest: Optional[datetime] = None
    latest: Optional[datetime] = None

    # Compression stats
    original_words: int = 0
    compressed_words: int = 0

@dataclass
class DigestTopic:
    """A topic cluster in a digest."""

    name: str
    emoji: str = ""                  # Optional emoji for formatting
    items: List[DigestItem] = field(default_factory=list)

@dataclass
class Digest:
    """Complete digest output."""

    # Metadata
    generated_at: datetime = field(default_factory=datetime.utcnow)
    period: str = "24h"

    # Content
    topics: List[DigestTopic] = field(default_factory=list)

    # Aggregate stats
    sources_processed: int = 0
    articles_analyzed: int = 0
    total_original_words: int = 0
    total_compressed_words: int = 0

    # Meta-stats
    emotional_removed: int = 0
    unnamed_sources_flagged: int = 0
    speculation_stripped: int = 0
    duplicates_collapsed: int = 0
```

---

## 5. Module Specifications

### 5.1 Core Extractor

**File:** `src/newsdigest/core/extractor.py`

```python
class Extractor:
    """Main extraction engine."""

    def __init__(
        self,
        config: Optional[Config] = None,
        mode: str = "standard"  # conservative, standard, aggressive
    ):
        """Initialize extractor with configuration."""

    def extract(self, source: str) -> ExtractionResult:
        """
        Extract content from a single source.

        Args:
            source: URL string or raw text content

        Returns:
            ExtractionResult with compressed content and statistics
        """

    def extract_batch(
        self,
        sources: List[str],
        parallel: bool = True,
        max_workers: int = 5
    ) -> List[ExtractionResult]:
        """
        Extract content from multiple sources.

        Args:
            sources: List of URLs or text content
            parallel: Whether to process in parallel
            max_workers: Maximum concurrent workers

        Returns:
            List of ExtractionResult objects
        """

    def compare(self, source: str) -> ComparisonResult:
        """
        Generate side-by-side comparison view.

        Returns original text with annotations alongside extracted version.
        """
```

### 5.2 Analyzers

Each analyzer follows the same interface:

```python
from abc import ABC, abstractmethod

class BaseAnalyzer(ABC):
    """Base class for all semantic analyzers."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}

    @abstractmethod
    def analyze(self, sentences: List[Sentence]) -> List[Sentence]:
        """
        Analyze sentences and update their properties.

        Args:
            sentences: List of Sentence objects

        Returns:
            Modified list of Sentence objects with updated scores/flags
        """
        pass
```

#### 5.2.1 FillerDetector

**File:** `src/newsdigest/analyzers/filler.py`

Detects sentences with no information content.

**Patterns to detect:**
- "Here's what you need to know"
- "What happened next will surprise you"
- "But that's not the whole story"
- "Stay tuned for more updates"
- "We'll keep you posted"
- "Breaking news" (without actual content)

**Implementation:**
- Pattern matching for known filler phrases
- Low entity density detection
- Short sentences with no nouns/verbs

#### 5.2.2 SpeculationStripper

**File:** `src/newsdigest/analyzers/speculation.py`

Detects and removes speculative content.

**Keywords to detect:**
- Modal verbs: "could", "might", "may", "would", "should"
- Hedging: "potentially", "possibly", "perhaps", "apparently"
- Uncertainty: "seems to", "appears to", "it is thought"
- Future speculation: "is expected to", "is likely to"

**Scoring:**
- Count speculation keywords
- Weight by position (speculation at end of sentence scores higher)
- Threshold: >2 speculation markers = remove

#### 5.2.3 SourceValidator

**File:** `src/newsdigest/analyzers/sources.py`

Validates and extracts source attribution.

**Named source patterns:**
- Direct attribution: `"said [Name]"`, `"according to [Name]"`
- Title attribution: `"[Title] [Name] said"`
- Organization: `"the [Organization] announced"`

**Unnamed source patterns (flag):**
- "sources say"
- "sources familiar with"
- "according to sources"
- "officials say" (without naming)
- "experts say" (without naming)
- "people close to the matter"

#### 5.2.4 EmotionalDetector

**File:** `src/newsdigest/analyzers/emotional.py`

Detects emotional activation language.

**Word lists:**

```python
EMOTIONAL_WORDS = {
    "activation": [
        "shocking", "stunning", "alarming", "unprecedented",
        "bombshell", "explosive", "devastating", "terrifying",
        "outrageous", "scandalous", "horrifying", "incredible"
    ],
    "superlatives": [
        "historic", "groundbreaking", "game-changing", "revolutionary",
        "monumental", "earth-shattering", "jaw-dropping"
    ],
    "urgency": [
        "breaking", "urgent", "critical", "emergency",
        "must-read", "don't miss"
    ]
}
```

**Behavior:**
- Remove words from sentence but keep factual content
- Track count of removed words for statistics
- If sentence becomes empty after removal, mark entire sentence as filler

#### 5.2.5 RepetitionCollapser

**File:** `src/newsdigest/analyzers/repetition.py`

Detects and collapses repeated information.

**Algorithm:**
1. Compute semantic similarity between sentences (cosine similarity on embeddings or simpler TF-IDF)
2. Identify clusters of similar sentences
3. Keep first occurrence in each cluster
4. Mark subsequent occurrences for removal with reason `BACKGROUND_REPEAT`

**Threshold:** Similarity > 0.85 = duplicate

#### 5.2.6 NoveltyScorer

**File:** `src/newsdigest/analyzers/novelty.py`

Scores sentences by information novelty.

**Algorithm:**
1. Extract key entities and facts from each sentence
2. Compare against:
   - Earlier sentences in same article (internal novelty)
   - Background knowledge base (external novelty) - optional
3. Score based on new information introduced

**Output:** `novelty_score` 0.0-1.0 on each sentence

#### 5.2.7 ClaimExtractor

**File:** `src/newsdigest/analyzers/claims.py`

Extracts falsifiable claims.

**Claim identification:**
- Sentences with concrete data (numbers, dates, names)
- Attributed statements
- Declarative sentences with clear subjects/predicates

**Output:**
- List of `Claim` objects
- Each claim linked to source sentence
- Confidence score based on attribution strength

#### 5.2.8 QuoteIsolator

**File:** `src/newsdigest/analyzers/quotes.py`

Separates direct quotes from paraphrase.

**Detection:**
- Quotation marks
- Attribution verbs: "said", "stated", "announced", "claimed"

**Classification:**
- Informative quote: adds new information
- Circular quote: restates what was just reported (remove)
- Attribution quote: names a source (keep)

---

### 5.3 Ingestors

#### 5.3.1 URLFetcher

**File:** `src/newsdigest/ingestors/url.py`

```python
class URLFetcher:
    """Fetches article content from URLs."""

    async def fetch(self, url: str) -> Article:
        """
        Fetch and parse article from URL.

        Features:
        - Async HTTP with httpx
        - Automatic redirect handling
        - Respect robots.txt
        - User-agent rotation
        - Rate limiting per domain
        - Timeout handling
        """

    async def fetch_batch(
        self,
        urls: List[str],
        max_concurrent: int = 5
    ) -> List[Article]:
        """Fetch multiple URLs concurrently."""
```

**Rate Limiting:**
- Default: 1 request per second per domain
- Configurable per-domain overrides
- Exponential backoff on 429 responses

#### 5.3.2 RSSParser

**File:** `src/newsdigest/ingestors/rss.py`

```python
class RSSParser:
    """Parses RSS/Atom feeds."""

    def parse(self, feed_url: str) -> List[Article]:
        """
        Parse RSS feed and return list of articles.

        Uses feedparser library.
        Extracts: title, link, published, summary, content.
        """

    def get_new_items(
        self,
        feed_url: str,
        since: datetime
    ) -> List[Article]:
        """Get only items published since given time."""
```

#### 5.3.3 NewsAPIClient

**File:** `src/newsdigest/ingestors/newsapi.py`

```python
class NewsAPIClient:
    """Client for NewsAPI.org."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(
        self,
        query: str,
        language: str = "en",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        sources: Optional[List[str]] = None
    ) -> List[Article]:
        """Search for articles matching query."""

    def top_headlines(
        self,
        country: str = "us",
        category: Optional[str] = None
    ) -> List[Article]:
        """Get top headlines."""
```

---

### 5.4 Parsers

#### 5.4.1 HTMLCleaner

**File:** `src/newsdigest/parsers/html.py`

```python
class HTMLCleaner:
    """Cleans HTML and extracts text content."""

    def clean(self, html: str) -> str:
        """
        Remove non-content elements and extract clean text.

        Removes:
        - Scripts, styles, iframes
        - Navigation, headers, footers
        - Ads, sidebars
        - Comments
        """
```

#### 5.4.2 ArticleExtractor

**File:** `src/newsdigest/parsers/article.py`

```python
class ArticleExtractor:
    """Extracts main article content from web pages."""

    def extract(self, html: str, url: str) -> Article:
        """
        Extract article using readability algorithms.

        Uses: readability-lxml or similar

        Extracts:
        - Title
        - Author
        - Published date
        - Main body text
        """
```

#### 5.4.3 MetadataParser

**File:** `src/newsdigest/parsers/metadata.py`

```python
class MetadataParser:
    """Extracts metadata from HTML."""

    def parse(self, html: str) -> dict:
        """
        Extract metadata from:
        - <meta> tags
        - Open Graph tags
        - Twitter cards
        - JSON-LD structured data
        - Schema.org markup
        """
```

---

### 5.5 Formatters

#### 5.5.1 MarkdownFormatter

**File:** `src/newsdigest/formatters/markdown.py`

```python
class MarkdownFormatter:
    """Formats output as Markdown."""

    def format_result(self, result: ExtractionResult) -> str:
        """Format single extraction result."""

    def format_comparison(self, result: ExtractionResult) -> str:
        """Format side-by-side comparison."""

    def format_digest(self, digest: Digest) -> str:
        """Format complete digest."""

    def format_stats(self, result: ExtractionResult) -> str:
        """Format statistics only."""
```

**Output format for extraction:**
```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARTICLE: "{title}"
SOURCE:  {source_name}
DATE:    {published_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXTRACTED CONTENT:
──────────────────
{extracted_text}

STATISTICS:
──────────────────
Original length:        {original_words} words
Compressed length:      {compressed_words} words
Compression ratio:      {compression_ratio}%
Semantic density:       {original_density} → {compressed_density}

...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### 5.5.2 JSONFormatter

**File:** `src/newsdigest/formatters/json.py`

Outputs structured JSON matching the API response format defined in section 7.

---

### 5.6 Digest Generator

**File:** `src/newsdigest/digest/generator.py`

```python
class DigestGenerator:
    """Generates daily/periodic digests from multiple sources."""

    def __init__(self, config: Config):
        self.config = config
        self.extractor = Extractor(config)
        self.clusterer = TopicClusterer()
        self.deduplicator = Deduplicator()

    def add_rss(self, url: str, name: Optional[str] = None):
        """Add RSS feed to digest sources."""

    def add_newsapi(self, query: str, **kwargs):
        """Add NewsAPI search to digest sources."""

    def generate(
        self,
        period: str = "24h",
        format: str = "markdown"
    ) -> Union[str, Digest]:
        """
        Generate digest for specified period.

        Steps:
        1. Fetch all sources
        2. Extract each article
        3. Deduplicate across sources
        4. Cluster by topic
        5. Merge related items
        6. Format output
        """
```

#### 5.6.1 TopicClusterer

**File:** `src/newsdigest/digest/clustering.py`

```python
class TopicClusterer:
    """Clusters articles by topic."""

    TOPICS = [
        ("World", "🌍"),
        ("Politics", "🏛️"),
        ("Markets", "💰"),
        ("Technology", "🔬"),
        ("Science", "🧪"),
        ("Sports", "⚽"),
        ("Entertainment", "🎬"),
    ]

    def cluster(self, articles: List[ExtractionResult]) -> Dict[str, List]:
        """
        Cluster articles into topics.

        Methods:
        - Keyword-based classification
        - Entity type analysis
        - Optional: ML-based topic modeling
        """
```

#### 5.6.2 Deduplicator

**File:** `src/newsdigest/digest/dedup.py`

```python
class Deduplicator:
    """Deduplicates articles across sources."""

    def deduplicate(
        self,
        articles: List[ExtractionResult],
        threshold: float = 0.85
    ) -> List[ExtractionResult]:
        """
        Remove duplicate articles, keeping the most complete.

        Algorithm:
        1. Compute similarity between all pairs
        2. Cluster similar articles
        3. Select representative from each cluster
        4. Merge sources/links from duplicates
        """
```

---

## 6. CLI Specification

### 6.1 Command Structure

```bash
newsdigest <command> [options] [arguments]
```

### 6.2 Commands

#### 6.2.1 `extract`

Extract content from article(s).

```bash
newsdigest extract <url_or_file> [options]

Arguments:
  url_or_file    URL to article or path to file (use - for stdin)

Options:
  -m, --mode     Extraction mode: conservative|standard|aggressive (default: standard)
  -f, --format   Output format: text|markdown|json|html (default: markdown)
  -o, --output   Output file path (default: stdout)
  --no-stats     Omit statistics from output
  --no-sources   Omit source information
  -v, --verbose  Show detailed processing info

Examples:
  newsdigest extract https://example.com/article
  newsdigest extract https://example.com/article -f json -o result.json
  cat article.html | newsdigest extract -
```

#### 6.2.2 `compare`

Show side-by-side comparison.

```bash
newsdigest compare <url> [options]

Options:
  -f, --format   Output format: text|markdown|html (default: text)
  -w, --width    Terminal width for formatting (default: auto)
  -o, --output   Output file path

Examples:
  newsdigest compare https://example.com/article
  newsdigest compare https://example.com/article -f html -o comparison.html
```

#### 6.2.3 `stats`

Show extraction statistics only.

```bash
newsdigest stats <url> [options]

Options:
  -f, --format   Output format: text|json (default: text)
  --detailed     Show per-category breakdown

Examples:
  newsdigest stats https://example.com/article
  newsdigest stats https://example.com/article -f json
```

#### 6.2.4 `digest`

Generate digest from configured sources.

```bash
newsdigest digest [options]

Options:
  -p, --period   Time period: 1h|6h|12h|24h|48h|7d (default: 24h)
  -f, --format   Output format: text|markdown|html|json|email (default: markdown)
  -o, --output   Output file path
  -c, --config   Config file path (default: ~/.newsdigest/config.yml)
  --email        Email address to send digest to
  --no-cluster   Don't cluster by topic
  --no-dedup     Don't deduplicate across sources

Examples:
  newsdigest digest
  newsdigest digest --period 12h --email me@example.com
  newsdigest digest --format json --output digest.json
```

#### 6.2.5 `sources`

Manage news sources.

```bash
newsdigest sources <subcommand> [options]

Subcommands:
  list           List configured sources
  add            Add a new source
  remove         Remove a source
  test           Test source connectivity

newsdigest sources add [options]
  --rss <url>    Add RSS feed
  --newsapi <query>  Add NewsAPI search
  --name <name>  Friendly name for source
  --category <cat>  Category for clustering

Examples:
  newsdigest sources list
  newsdigest sources add --rss https://feeds.reuters.com/reuters/topNews --name Reuters
  newsdigest sources remove Reuters
  newsdigest sources test --rss https://feeds.reuters.com/reuters/topNews
```

#### 6.2.6 `watch`

Real-time monitoring mode.

```bash
newsdigest watch [options]

Options:
  -s, --sources  Sources config file
  -i, --interval Polling interval: 5m|15m|30m|1h (default: 30m)
  -o, --output   Output directory for results
  --daemon       Run as background daemon
  --alert        Enable alert notifications

Examples:
  newsdigest watch --sources feeds.yml --interval 15m
  newsdigest watch --sources feeds.yml --output ~/news/ --daemon
```

#### 6.2.7 `analytics`

View consumption analytics.

```bash
newsdigest analytics [options]

Options:
  -p, --period   Time period: 7d|30d|90d|all (default: 30d)
  -f, --format   Output format: text|json (default: text)
  --export       Export to file

Examples:
  newsdigest analytics
  newsdigest analytics --period 90d --format json --export analytics.json
```

#### 6.2.8 `setup`

Initial setup and model download.

```bash
newsdigest setup [options]

Options:
  --models       Download/update language models
  --config       Create default config file
  --all          Full setup (models + config)

Examples:
  newsdigest setup --all
  newsdigest setup --models
```

#### 6.2.9 `serve`

Start REST API server.

```bash
newsdigest serve [options]

Options:
  -p, --port     Port number (default: 8080)
  -h, --host     Host to bind (default: 127.0.0.1)
  --workers      Number of workers (default: 4)
  --reload       Enable auto-reload (development)

Examples:
  newsdigest serve
  newsdigest serve --port 3000 --host 0.0.0.0
```

---

## 7. API Specification

### 7.1 REST Endpoints

Base URL: `https://api.newsdigest.dev/v1` (hosted) or `http://localhost:8080/v1` (self-hosted)

#### 7.1.1 POST /extract

Extract content from URL.

**Request:**
```json
{
  "url": "https://example.com/article",
  "mode": "standard",
  "include_stats": true,
  "include_removed": false
}
```

**Response:**
```json
{
  "id": "ext_abc123",
  "url": "https://example.com/article",
  "title": "Article Title",
  "source": "Example News",
  "published": "2025-01-11T14:30:00Z",
  "processed": "2025-01-11T15:42:17Z",

  "extracted": {
    "text": "Compressed article text...",
    "claims": [
      {
        "text": "Claim text",
        "type": "factual",
        "source": "Named Source",
        "confidence": 0.95
      }
    ]
  },

  "statistics": {
    "original_words": 1247,
    "compressed_words": 48,
    "compression_ratio": 0.961,
    "original_density": 0.09,
    "compressed_density": 0.84,
    "novel_claims": 4,
    "named_sources": 3,
    "unnamed_sources": 2,
    "emotional_words_removed": 14,
    "speculation_sentences_removed": 8,
    "repeated_sentences_collapsed": 6
  },

  "warnings": [
    {
      "type": "UNNAMED_SOURCE",
      "text": "sources familiar with the matter",
      "location": "paragraph 4"
    }
  ]
}
```

#### 7.1.2 POST /digest

Generate digest from sources.

**Request:**
```json
{
  "sources": [
    {"type": "rss", "url": "https://feeds.reuters.com/reuters/topNews"},
    {"type": "rss", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"}
  ],
  "period": "24h",
  "format": "markdown",
  "cluster": true,
  "dedupe": true
}
```

**Response (format=json):**
```json
{
  "generated_at": "2025-01-11T08:00:00Z",
  "period": "24h",
  "sources_processed": 12,
  "articles_analyzed": 847,

  "topics": [
    {
      "name": "World",
      "emoji": "🌍",
      "items": [
        {
          "summary": "Summary text...",
          "sources": ["Reuters", "AP"],
          "article_count": 5,
          "compression": {"original": 2500, "compressed": 45}
        }
      ]
    }
  ],

  "meta_stats": {
    "total_words_processed": 412847,
    "total_words_delivered": 847,
    "compression_ratio": 0.998,
    "emotional_removed": 2847,
    "speculation_stripped": 1847,
    "duplicates_collapsed": 394
  }
}
```

#### 7.1.3 POST /webhooks

Register webhook for alerts.

**Request:**
```json
{
  "url": "https://your-server.com/webhook",
  "triggers": {
    "min_novelty": 0.8,
    "topics": ["technology", "markets"],
    "keywords": ["Federal Reserve", "SpaceX"]
  }
}
```

**Response:**
```json
{
  "id": "whk_xyz789",
  "url": "https://your-server.com/webhook",
  "created": "2025-01-11T10:00:00Z",
  "status": "active"
}
```

#### 7.1.4 GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime": 3600
}
```

### 7.2 Authentication

API key in Authorization header:
```
Authorization: Bearer <api_key>
```

### 7.3 Rate Limits

| Tier | Extractions/min | Digests/hour |
|------|-----------------|--------------|
| Free | 10 | 1 |
| Pro | 100 | 10 |
| Team | 500 | 50 |

---

## 8. Configuration Schema

### 8.1 Config File Location

- Default: `~/.newsdigest/config.yml`
- Override: `--config` flag or `NEWSDIGEST_CONFIG` env var

### 8.2 Schema

```yaml
# ~/.newsdigest/config.yml

# Version for config schema
version: 1

#──────────────────────────────────────────────────────────────────
# SOURCES
#──────────────────────────────────────────────────────────────────
sources:
  - type: rss          # rss | newsapi | scrape | twitter | email
    url: string        # Feed URL
    name: string       # Display name
    category: string   # Topic category (optional)
    enabled: bool      # default: true

#──────────────────────────────────────────────────────────────────
# EXTRACTION SETTINGS
#──────────────────────────────────────────────────────────────────
extraction:
  mode: standard              # conservative | standard | aggressive
  min_sentence_density: 0.3   # 0.0 - 1.0
  unnamed_sources: flag       # keep | flag | remove
  speculation: remove         # keep | flag | remove
  max_hedges_per_sentence: 2
  emotional_language: remove  # keep | flag | remove

  quotes:
    keep_attributed: true
    keep_unattributed: false
    flag_circular: true

#──────────────────────────────────────────────────────────────────
# DIGEST SETTINGS
#──────────────────────────────────────────────────────────────────
digest:
  period: 24h                 # Duration string
  max_items: 100

  clustering:
    enabled: true
    min_cluster_size: 3

  deduplication:
    enabled: true
    similarity_threshold: 0.85

  novelty:
    enabled: true
    min_score: 0.3
    window: 7d

  threading:
    enabled: true
    max_thread_age: 72h

#──────────────────────────────────────────────────────────────────
# OUTPUT SETTINGS
#──────────────────────────────────────────────────────────────────
output:
  format: markdown            # markdown | html | json | text | email
  show_stats: true
  include_links: true
  show_warnings: true

  file:
    enabled: false
    path: ~/Documents/news/
    filename_format: "digest-{date}.md"

#──────────────────────────────────────────────────────────────────
# EMAIL DELIVERY
#──────────────────────────────────────────────────────────────────
email:
  enabled: false
  to: string
  from: digest@newsdigest.dev
  subject: "NewsDigest: {date}"
  schedule: "0 7 * * *"       # Cron format

  smtp:
    host: string
    port: 587
    user: ${SMTP_USER}        # Environment variable reference
    pass: ${SMTP_PASS}
    tls: true

#──────────────────────────────────────────────────────────────────
# ALERTS
#──────────────────────────────────────────────────────────────────
alerts:
  breaking:
    enabled: false
    min_novelty: 0.9
    min_sources: 3
    notify:
      - type: pushover | webhook | email
        # type-specific fields

  keywords:
    - term: string
      notify: [pushover, webhook]

#──────────────────────────────────────────────────────────────────
# ANALYTICS
#──────────────────────────────────────────────────────────────────
analytics:
  enabled: true
  retention: 90d
  export_format: json

#──────────────────────────────────────────────────────────────────
# API
#──────────────────────────────────────────────────────────────────
api:
  host: 127.0.0.1
  port: 8080
  workers: 4

  # For hosted API
  key: ${NEWSDIGEST_API_KEY}

#──────────────────────────────────────────────────────────────────
# ADVANCED
#──────────────────────────────────────────────────────────────────
advanced:
  cache:
    enabled: true
    ttl: 3600               # seconds
    max_size: 1000          # entries

  rate_limiting:
    requests_per_second: 1
    per_domain: true

  http:
    timeout: 30             # seconds
    retries: 3
    user_agent: "NewsDigest/0.1"

  logging:
    level: INFO             # DEBUG | INFO | WARNING | ERROR
    file: ~/.newsdigest/logs/newsdigest.log
    max_size: 10MB
    backup_count: 5
```

---

## 9. Dependencies

### 9.1 Core Dependencies

```toml
# pyproject.toml

[project]
name = "newsdigest"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # CLI
    "click>=8.1.0",
    "rich>=13.0.0",              # Terminal formatting

    # HTTP
    "httpx>=0.25.0",             # Async HTTP client

    # HTML/XML Parsing
    "beautifulsoup4>=4.12.0",
    "lxml>=4.9.0",
    "readability-lxml>=0.8.0",   # Article extraction
    "feedparser>=6.0.0",         # RSS parsing

    # NLP
    "spacy>=3.7.0",              # NLP pipeline

    # Configuration
    "pyyaml>=6.0.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",           # Validation

    # Utilities
    "python-dateutil>=2.8.0",
    "tenacity>=8.2.0",           # Retry logic
]

[project.optional-dependencies]
api = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
]

email = [
    "aiosmtplib>=2.0.0",
]

newsapi = [
    "newsapi-python>=0.2.7",
]

twitter = [
    "tweepy>=4.14.0",
]

pdf = [
    "pdfplumber>=0.10.0",
]

ml = [
    # Enhanced extraction with transformers
    "transformers>=4.35.0",
    "torch>=2.1.0",
    "sentence-transformers>=2.2.0",
]

dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
    "pre-commit>=3.6.0",
]

all = [
    "newsdigest[api,email,newsapi,twitter,pdf,ml]",
]
```

### 9.2 spaCy Model

```bash
# Download English model during setup
python -m spacy download en_core_web_sm  # ~12MB, fast
# OR for better accuracy:
python -m spacy download en_core_web_md  # ~40MB
# OR for best accuracy:
python -m spacy download en_core_web_lg  # ~560MB
```

---

## 10. Testing Requirements

### 10.1 Test Coverage Targets

| Module | Coverage Target |
|--------|-----------------|
| Core extraction | 90% |
| Analyzers | 85% |
| Ingestors | 80% |
| Parsers | 85% |
| Formatters | 80% |
| CLI | 75% |
| API | 80% |

### 10.2 Test Categories

#### Unit Tests
- Each analyzer tested independently
- Mock NLP pipeline for speed
- Test edge cases (empty input, malformed HTML, etc.)

#### Integration Tests
- Full pipeline with real spaCy models
- End-to-end extraction from sample articles
- Digest generation with multiple sources

#### Fixture Articles
Provide test fixtures for:
- Standard news article (expected ~90% compression)
- Opinion piece (lower compression expected)
- Press release (higher density, lower compression)
- Speculation-heavy article
- Quote-heavy article
- Minimal filler article

### 10.3 Test Fixtures Location

```
tests/fixtures/
├── articles/
│   ├── standard_news.html
│   ├── standard_news.txt
│   ├── opinion_piece.html
│   ├── press_release.html
│   ├── speculation_heavy.html
│   ├── quote_heavy.html
│   └── minimal_filler.html
└── expected/
    ├── standard_news_extract.json
    ├── standard_news_stats.json
    └── ...
```

---

## 11. Implementation Phases

### Phase 1: Core Engine (v0.1)
**Priority: Critical**

1. Project setup (pyproject.toml, structure)
2. Basic HTTP fetching (URLFetcher)
3. HTML cleaning and article extraction
4. NLP pipeline setup (spaCy integration)
5. Core analyzers:
   - FillerDetector
   - SpeculationStripper
   - EmotionalDetector
   - SourceValidator
6. Basic Extractor class
7. CLI: `extract`, `stats` commands
8. Markdown output formatter
9. JSON output formatter
10. Unit tests for core functionality

**Deliverables:**
- Working `newsdigest extract <url>` command
- Basic compression with statistics

### Phase 2: Enhanced Analysis (v0.1.x)
**Priority: High**

1. RepetitionCollapser
2. NoveltyScorer
3. ClaimExtractor
4. QuoteIsolator
5. Comparison mode (`compare` command)
6. RSS ingestion
7. Basic digest generation
8. CLI: `compare`, `digest`, `sources` commands

**Deliverables:**
- Complete analyzer suite
- Digest from RSS feeds

### Phase 3: API & Integrations (v0.2)
**Priority: Medium**

1. FastAPI REST server
2. API endpoints (extract, digest)
3. Authentication
4. Rate limiting
5. NewsAPI integration
6. Email delivery
7. CLI: `serve` command

**Deliverables:**
- Working REST API
- Email digest delivery

### Phase 4: Advanced Features (v0.3)
**Priority: Lower**

1. Watch mode (real-time monitoring)
2. Topic clustering (ML-based)
3. Story threading
4. Alert system (webhooks, push)
5. Analytics dashboard
6. CLI: `watch`, `analytics` commands

**Deliverables:**
- Real-time monitoring
- Alert notifications

### Phase 5: Extensions (v0.4+)
**Priority: Future**

1. Browser extension
2. Telegram/Slack bots
3. Twitter/X ingestion
4. PDF parsing
5. Multi-language support

---

## Appendix A: Filler Word Lists

### A.1 Emotional Activation Words

```python
EMOTIONAL_ACTIVATION = [
    "shocking", "stunning", "alarming", "unprecedented", "bombshell",
    "explosive", "devastating", "terrifying", "outrageous", "scandalous",
    "horrifying", "incredible", "unbelievable", "jaw-dropping", "mind-blowing",
    "earth-shattering", "groundbreaking", "game-changing", "revolutionary",
    "historic", "monumental", "seismic", "dramatic", "remarkable",
    "extraordinary", "sensational", "staggering", "astonishing"
]
```

### A.2 Speculation Markers

```python
SPECULATION_MARKERS = [
    "could", "might", "may", "would", "should",
    "potentially", "possibly", "perhaps", "apparently",
    "seemingly", "reportedly", "allegedly", "supposedly",
    "it appears", "it seems", "is thought to", "is believed to",
    "is expected to", "is likely to", "is set to", "is poised to",
    "could potentially", "might possibly", "may perhaps"
]
```

### A.3 Engagement Hooks

```python
ENGAGEMENT_HOOKS = [
    "here's what you need to know",
    "what happened next will surprise you",
    "but that's not the whole story",
    "stay tuned for more",
    "we'll keep you posted",
    "you won't believe",
    "what this means for you",
    "the real story behind",
    "everything you need to know",
    "here's why that matters",
    "here's the bottom line",
    "the takeaway"
]
```

### A.4 Unnamed Source Patterns

```python
UNNAMED_SOURCE_PATTERNS = [
    r"sources?\s+(?:say|said|indicate|suggest|claim)",
    r"sources?\s+familiar\s+with",
    r"sources?\s+close\s+to",
    r"according\s+to\s+sources?",
    r"officials?\s+(?:say|said)",
    r"experts?\s+(?:say|said|believe|think)",
    r"people\s+(?:familiar|close|briefed)",
    r"(?:a|an)\s+(?:person|official|source)\s+who",
    r"those\s+with\s+knowledge",
    r"insiders?\s+(?:say|said)"
]
```

---

## Appendix B: Density Calculation

Semantic density is calculated as:

```python
def calculate_density(text: str, claims: List[Claim]) -> float:
    """
    Calculate semantic density score (0.0 - 1.0).

    Formula:
    density = (claim_count * avg_claim_confidence) / word_count * scaling_factor

    Where scaling_factor normalizes to 0.0-1.0 range based on
    empirical analysis of high-quality news sources.
    """
    word_count = len(text.split())
    if word_count == 0:
        return 0.0

    claim_count = len(claims)
    if claim_count == 0:
        return 0.0

    avg_confidence = sum(c.confidence for c in claims) / claim_count

    raw_density = (claim_count * avg_confidence) / word_count

    # Scaling: 0.1 claims per word with 1.0 confidence = 1.0 density
    scaling_factor = 10.0
    density = min(1.0, raw_density * scaling_factor)

    return round(density, 2)
```

---

*End of Specification*
