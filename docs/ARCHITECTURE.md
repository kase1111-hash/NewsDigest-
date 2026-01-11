# Architecture Design Document

**Project:** NewsDigest
**Version:** 0.1.0
**Last Updated:** 2026-01-11

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Component Architecture](#2-component-architecture)
3. [Data Flow](#3-data-flow)
4. [Module Dependencies](#4-module-dependencies)
5. [API Design](#5-api-design)
6. [Data Models](#6-data-models)
7. [Storage Architecture](#7-storage-architecture)
8. [Concurrency Model](#8-concurrency-model)
9. [Error Handling](#9-error-handling)
10. [Security Architecture](#10-security-architecture)
11. [Deployment Architecture](#11-deployment-architecture)

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACES                                 │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│         CLI         │      REST API       │       Python Library            │
│   (Click + Rich)    │     (FastAPI)       │    (Direct Import)              │
└──────────┬──────────┴──────────┬──────────┴──────────┬──────────────────────┘
           │                     │                     │
           └─────────────────────┼─────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CORE ENGINE                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Extractor                                    │    │
│  │   • Orchestrates extraction pipeline                                 │    │
│  │   • Manages analyzer chain                                           │    │
│  │   • Produces ExtractionResult                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      DigestGenerator                                 │    │
│  │   • Aggregates multiple extractions                                  │    │
│  │   • Deduplicates and clusters                                        │    │
│  │   • Produces Digest                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
           │                     │                     │
           ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────────┐
│    INGESTORS    │  │    ANALYZERS    │  │          FORMATTERS             │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  ┌───────────┐  │
│  │    URL    │  │  │  │  Filler   │  │  │  │ Markdown  │  │   JSON    │  │
│  ├───────────┤  │  │  ├───────────┤  │  │  ├───────────┤  ├───────────┤  │
│  │    RSS    │  │  │  │Speculation│  │  │  │   HTML    │  │   Text    │  │
│  ├───────────┤  │  │  ├───────────┤  │  │  ├───────────┤  └───────────┘  │
│  │  NewsAPI  │  │  │  │ Emotional │  │  │  │   Email   │                 │
│  ├───────────┤  │  │  ├───────────┤  │  │  └───────────┘                 │
│  │   Email   │  │  │  │  Sources  │  │  └─────────────────────────────────┘
│  ├───────────┤  │  │  ├───────────┤  │
│  │  Twitter  │  │  │  │Repetition │  │
│  ├───────────┤  │  │  ├───────────┤  │
│  │    PDF    │  │  │  │  Novelty  │  │
│  └───────────┘  │  │  ├───────────┤  │
└─────────────────┘  │  │  Claims   │  │
                     │  ├───────────┤  │
                     │  │  Quotes   │  │
                     │  └───────────┘  │
                     └─────────────────┘
           │                     │
           ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INFRASTRUCTURE                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Config    │  │    Cache    │  │  Analytics  │  │      Logging        │ │
│  │  (Pydantic) │  │  (In-Memory)│  │  (SQLite)   │  │ (Python logging)    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Design Principles

1. **Modularity**: Each component has a single responsibility
2. **Extensibility**: New analyzers/ingestors/formatters easy to add
3. **Testability**: All components can be unit tested in isolation
4. **Async-First**: I/O operations use async for performance
5. **Configuration-Driven**: Behavior controlled via config, not code changes
6. **Graceful Degradation**: Optional features fail gracefully

---

## 2. Component Architecture

### 2.1 Core Engine

```
┌─────────────────────────────────────────────────────────────────┐
│                          Extractor                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Ingestor   │───▶│    Parser    │───▶│   Pipeline   │       │
│  │   (fetch)    │    │  (extract)   │    │  (analyze)   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│    Raw HTML/Text      Article Object      List[Sentence]         │
│                                                 │                │
│                                                 ▼                │
│                                         ┌──────────────┐        │
│                                         │  Compressor  │        │
│                                         │  (filter)    │        │
│                                         └──────────────┘        │
│                                                 │                │
│                                                 ▼                │
│                                        ExtractionResult          │
└─────────────────────────────────────────────────────────────────┘
```

#### Extractor Class Interface

```python
class Extractor:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.ingestors = IngestorFactory(config)
        self.parser = ArticleParser(config)
        self.pipeline = AnalysisPipeline(config)

    async def extract(self, source: str) -> ExtractionResult:
        """Extract from single source (URL or text)."""

    async def extract_batch(
        self,
        sources: List[str],
        max_concurrent: int = 5
    ) -> List[ExtractionResult]:
        """Extract from multiple sources concurrently."""

    def compare(self, source: str) -> ComparisonResult:
        """Generate comparison view."""
```

### 2.2 Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                      AnalysisPipeline                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Input: Article                                                 │
│      │                                                           │
│      ▼                                                           │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    NLP Processing                         │  │
│   │   spaCy: tokenize → POS tag → NER → sentence segment     │  │
│   └──────────────────────────────────────────────────────────┘  │
│      │                                                           │
│      ▼                                                           │
│   List[Sentence] (with tokens, entities, POS tags)              │
│      │                                                           │
│      ├───────────────────────────────────────────────────────┐  │
│      │              ANALYZER CHAIN                            │  │
│      │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │  │
│      │   │ Filler  │→│Speculate│→│Emotional│→│ Sources │    │  │
│      │   └─────────┘ └─────────┘ └─────────┘ └─────────┘    │  │
│      │        │           │           │           │          │  │
│      │        ▼           ▼           ▼           ▼          │  │
│      │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │  │
│      │   │Repetition│→│ Novelty │→│ Claims  │→│ Quotes  │    │  │
│      │   └─────────┘ └─────────┘ └─────────┘ └─────────┘    │  │
│      └───────────────────────────────────────────────────────┘  │
│      │                                                           │
│      ▼                                                           │
│   List[Sentence] (with scores, flags, keep/remove decisions)    │
│      │                                                           │
│      ▼                                                           │
│   Output: AnalysisResult                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Pipeline Processing Order

The analyzer order is intentional:

1. **FillerDetector** - Remove obvious filler first
2. **SpeculationStripper** - Remove hedging/speculation
3. **EmotionalDetector** - Strip emotional language
4. **SourceValidator** - Flag/validate sources
5. **RepetitionCollapser** - Collapse duplicates (needs clean sentences)
6. **NoveltyScorer** - Score novelty (after dedup)
7. **ClaimExtractor** - Extract claims (from scored sentences)
8. **QuoteIsolator** - Classify quotes (final pass)

### 2.3 Ingestor Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      IngestorFactory                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   detect_source_type(source: str) -> SourceType                 │
│      │                                                           │
│      ├── URL pattern      → URLFetcher                          │
│      ├── RSS URL pattern  → RSSParser                           │
│      ├── File path        → FileReader                          │
│      ├── Raw HTML/text    → DirectParser                        │
│      └── Unknown          → raise UnsupportedSourceError        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      BaseIngestor (ABC)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   @abstractmethod                                                │
│   async def ingest(self, source: str) -> Article                │
│                                                                  │
│   @abstractmethod                                                │
│   async def ingest_batch(                                        │
│       self, sources: List[str]                                   │
│   ) -> List[Article]                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
         △                    △                    △
         │                    │                    │
┌────────┴────────┐ ┌────────┴────────┐ ┌────────┴────────┐
│   URLFetcher    │ │   RSSParser     │ │  NewsAPIClient  │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ • httpx client  │ │ • feedparser    │ │ • API client    │
│ • rate limiting │ │ • date filtering│ │ • query builder │
│ • retry logic   │ │ • content fetch │ │ • pagination    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 2.4 Analyzer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      BaseAnalyzer (ABC)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   def __init__(self, config: AnalyzerConfig = None)             │
│                                                                  │
│   @abstractmethod                                                │
│   def analyze(                                                   │
│       self, sentences: List[Sentence]                            │
│   ) -> List[Sentence]                                            │
│                                                                  │
│   @property                                                      │
│   def name(self) -> str                                          │
│                                                                  │
│   @property                                                      │
│   def enabled(self) -> bool                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
         △
         │
         ├── FillerDetector
         ├── SpeculationStripper
         ├── EmotionalDetector
         ├── SourceValidator
         ├── RepetitionCollapser
         ├── NoveltyScorer
         ├── ClaimExtractor
         └── QuoteIsolator
```

#### Analyzer Contract

Each analyzer:
- Receives list of Sentence objects
- Modifies sentences in-place (scores, flags)
- Returns the same list (potentially filtered)
- Must be stateless between calls
- Must handle empty input gracefully

### 2.5 Formatter Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      BaseFormatter (ABC)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   @abstractmethod                                                │
│   def format_result(self, result: ExtractionResult) -> str     │
│                                                                  │
│   @abstractmethod                                                │
│   def format_digest(self, digest: Digest) -> str                │
│                                                                  │
│   @abstractmethod                                                │
│   def format_comparison(self, result: ExtractionResult) -> str  │
│                                                                  │
│   @abstractmethod                                                │
│   def format_stats(self, result: ExtractionResult) -> str       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
         △
         │
         ├── MarkdownFormatter
         ├── JSONFormatter
         ├── HTMLFormatter
         ├── TextFormatter
         └── EmailFormatter
```

---

## 3. Data Flow

### 3.1 Single Article Extraction Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        EXTRACTION DATA FLOW                               │
└──────────────────────────────────────────────────────────────────────────┘

User Input                Processing                              Output
─────────                 ──────────                              ──────

   URL          ┌─────────────────────────────────────────┐
    │           │           URLFetcher                     │
    │           │  • HTTP GET with headers                 │
    ├──────────▶│  • Follow redirects                      │──────┐
    │           │  • Handle rate limits                    │      │
    │           └─────────────────────────────────────────┘      │
    │                                                             │
    │                                                             ▼
    │                                                      Raw HTML
    │                                                             │
    │           ┌─────────────────────────────────────────┐      │
    │           │         ArticleParser                    │      │
    │           │  • HTMLCleaner (remove scripts, ads)     │      │
    │           │  • ArticleExtractor (readability)        │◀─────┘
    │           │  • MetadataParser (title, author, date)  │
    │           └─────────────────────────────────────────┘
    │                              │
    │                              ▼
    │                        Article Object
    │                    {id, title, content,
    │                     source, published_at}
    │                              │
    │           ┌─────────────────────────────────────────┐
    │           │          NLP Pipeline                    │
    │           │  • spaCy.load("en_core_web_sm")          │
    │           │  • doc = nlp(article.content)            │◀─────┘
    │           │  • Extract sentences, entities, POS      │
    │           └─────────────────────────────────────────┘
    │                              │
    │                              ▼
    │                     List[Sentence]
    │               Each with: text, tokens,
    │               pos_tags, entities
    │                              │
    │           ┌─────────────────────────────────────────┐
    │           │         Analyzer Chain                   │
    │           │                                          │
    │           │  for analyzer in pipeline:               │
    │           │      sentences = analyzer.analyze(       │◀─────┘
    │           │          sentences                       │
    │           │      )                                   │
    │           │                                          │
    │           └─────────────────────────────────────────┘
    │                              │
    │                              ▼
    │                  Analyzed Sentences
    │              Each with: scores, flags,
    │              keep/remove, removal_reason
    │                              │
    │           ┌─────────────────────────────────────────┐
    │           │          Compressor                      │
    │           │  • Filter: keep only where keep=True     │
    │           │  • Build compressed text                 │◀─────┘
    │           │  • Calculate statistics                  │
    │           │  • Collect claims, sources               │
    │           └─────────────────────────────────────────┘
    │                              │
    │                              ▼
    │                     ExtractionResult
    │               {text, claims, sources,
    │                statistics, removed, warnings}
    │                              │
    │           ┌─────────────────────────────────────────┐
    │           │          Formatter                       │
    │           │  • MarkdownFormatter.format_result()     │◀─────┘
    │           │  • Apply template                        │
    │           │  • Render statistics table               │
    │           └─────────────────────────────────────────┘
    │                              │
    │                              ▼
                            Formatted Output
                          (Markdown/JSON/HTML)
```

### 3.2 Digest Generation Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         DIGEST DATA FLOW                                  │
└──────────────────────────────────────────────────────────────────────────┘

Config Sources              Processing                           Output
──────────────              ──────────                           ──────

sources.yml       ┌─────────────────────────────────────────┐
     │            │         Source Loading                   │
     │            │  • Parse YAML config                     │
     ├───────────▶│  • Create ingestor per source            │
     │            │  • Filter by enabled=true                │
     │            └─────────────────────────────────────────┘
     │                              │
     │                              ▼
     │                     List[SourceConfig]
     │                              │
     │            ┌─────────────────────────────────────────┐
     │            │       Parallel Fetching                  │
     │            │                                          │
     │            │  async with TaskGroup() as tg:           │
     │            │      for source in sources:              │◀─────┘
     │            │          tg.create_task(                 │
     │            │              fetch_source(source)        │
     │            │          )                               │
     │            └─────────────────────────────────────────┘
     │                              │
     │                              ▼
     │                     List[Article]
     │               (from all sources, raw)
     │                              │
     │            ┌─────────────────────────────────────────┐
     │            │         Date Filtering                   │
     │            │  • Filter by period (e.g., 24h)          │◀─────┘
     │            │  • Remove articles outside window        │
     │            └─────────────────────────────────────────┘
     │                              │
     │                              ▼
     │            ┌─────────────────────────────────────────┐
     │            │       Parallel Extraction                │
     │            │                                          │
     │            │  results = await extractor.extract_batch(│◀─────┘
     │            │      [a.url for a in articles]           │
     │            │  )                                       │
     │            └─────────────────────────────────────────┘
     │                              │
     │                              ▼
     │                  List[ExtractionResult]
     │                              │
     │            ┌─────────────────────────────────────────┐
     │            │         Deduplication                    │
     │            │  • Compute pairwise similarity           │
     │            │  • Cluster similar articles              │◀─────┘
     │            │  • Select representative per cluster     │
     │            │  • Merge source attributions             │
     │            └─────────────────────────────────────────┘
     │                              │
     │                              ▼
     │               Deduplicated Results
     │                              │
     │            ┌─────────────────────────────────────────┐
     │            │        Topic Clustering                  │
     │            │  • Classify each result by topic         │
     │            │  • Group into DigestTopic objects        │◀─────┘
     │            │  • Sort by importance                    │
     │            └─────────────────────────────────────────┘
     │                              │
     │                              ▼
     │                  Dict[Topic, List[Result]]
     │                              │
     │            ┌─────────────────────────────────────────┐
     │            │       Digest Assembly                    │
     │            │  • Create DigestItem per result          │
     │            │  • Aggregate statistics                  │◀─────┘
     │            │  • Build Digest object                   │
     │            └─────────────────────────────────────────┘
     │                              │
     │                              ▼
     │                       Digest Object
     │                 {topics, stats, metadata}
     │                              │
     │            ┌─────────────────────────────────────────┐
     │            │          Formatter                       │
     │            │  • MarkdownFormatter.format_digest()     │◀─────┘
     │            │  • Render topic sections                 │
     │            │  • Render meta-statistics                │
     │            └─────────────────────────────────────────┘
     │                              │
     │                              ▼
                           Formatted Digest
                         (Markdown/HTML/Email)
```

### 3.3 API Request Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         API REQUEST FLOW                                  │
└──────────────────────────────────────────────────────────────────────────┘

HTTP Request                Processing                           Response
────────────                ──────────                           ────────

POST /v1/extract    ┌─────────────────────────────────────────┐
{url, mode}         │         FastAPI Router                   │
     │              │  @router.post("/extract")                │
     ├─────────────▶│  async def extract(req: ExtractRequest)  │
     │              └─────────────────────────────────────────┘
     │                              │
     │                              ▼
     │              ┌─────────────────────────────────────────┐
     │              │        Request Validation                │
     │              │  • Pydantic model validation             │
     │              │  • URL format check                      │
     │              │  • Rate limit check                      │
     │              └─────────────────────────────────────────┘
     │                              │
     │                     ┌───────┴───────┐
     │                     ▼               ▼
     │                  Valid          Invalid
     │                     │               │
     │                     │               ▼
     │                     │        HTTP 400/422
     │                     │        {error: "..."}
     │                     │
     │                     ▼
     │              ┌─────────────────────────────────────────┐
     │              │         Extraction                       │
     │              │  extractor = Extractor(config)           │
     │              │  result = await extractor.extract(url)   │
     │              └─────────────────────────────────────────┘
     │                              │
     │                     ┌───────┴───────┐
     │                     ▼               ▼
     │                 Success          Error
     │                     │               │
     │                     │               ▼
     │                     │        HTTP 500
     │                     │        {error: "..."}
     │                     │
     │                     ▼
     │              ┌─────────────────────────────────────────┐
     │              │        Response Building                 │
     │              │  • Convert ExtractionResult to dict      │
     │              │  • Apply response model                  │
     │              │  • Add metadata (request_id, timing)     │
     │              └─────────────────────────────────────────┘
     │                              │
     │                              ▼
                             HTTP 200
                         ExtractResponse
                      {id, url, extracted,
                       statistics, warnings}
```

---

## 4. Module Dependencies

### 4.1 Import Dependency Graph

```
newsdigest
│
├── cli
│   ├── main.py ─────────────────────┐
│   ├── extract.py ──────────────────┼──▶ core.extractor
│   ├── compare.py ──────────────────┤    core.result
│   ├── stats.py ────────────────────┤    formatters.*
│   ├── digest.py ───────────────────┤    digest.generator
│   ├── sources.py ──────────────────┤    storage.sources
│   ├── watch.py ────────────────────┤    config.settings
│   ├── analytics.py ────────────────┤
│   └── setup.py ────────────────────┘
│
├── core
│   ├── extractor.py ────────────────┬──▶ ingestors.*
│   ├── pipeline.py ─────────────────┤    parsers.*
│   ├── article.py ──────────────────┤    analyzers.*
│   └── result.py ───────────────────┘
│
├── analyzers
│   ├── base.py ◀────────────────────┬─── filler.py
│   │                                ├─── speculation.py
│   │                                ├─── emotional.py
│   │                                ├─── sources.py
│   │                                ├─── repetition.py
│   │                                ├─── novelty.py
│   │                                ├─── claims.py
│   │                                └─── quotes.py
│   │
│   └── (all analyzers depend on)
│       └── core.article (Sentence model)
│
├── ingestors
│   ├── base.py ◀────────────────────┬─── url.py
│   │                                ├─── rss.py
│   │                                ├─── newsapi.py
│   │                                ├─── email.py
│   │                                ├─── twitter.py
│   │                                └─── pdf.py
│   │
│   └── (all ingestors depend on)
│       ├── core.article (Article model)
│       └── utils.http (HTTP client)
│
├── parsers
│   ├── html.py ─────────────────────┐
│   ├── article.py ──────────────────┼──▶ (no internal deps)
│   └── metadata.py ─────────────────┘
│
├── formatters
│   ├── base.py ◀────────────────────┬─── markdown.py
│   │                                ├─── json.py
│   │                                ├─── html.py
│   │                                ├─── text.py
│   │                                └─── email.py
│   │
│   └── (all formatters depend on)
│       └── core.result (ExtractionResult, Digest)
│
├── digest
│   ├── generator.py ────────────────┬──▶ core.extractor
│   ├── clustering.py ───────────────┤    ingestors.*
│   ├── dedup.py ────────────────────┤
│   └── threading.py ────────────────┘
│
├── api
│   ├── app.py ──────────────────────┬──▶ core.extractor
│   ├── routes/ ─────────────────────┤    digest.generator
│   └── models.py ───────────────────┘    config.settings
│
├── storage
│   ├── cache.py ────────────────────┐
│   ├── analytics.py ────────────────┼──▶ (no internal deps)
│   └── sources.py ──────────────────┘
│
├── config
│   ├── settings.py ─────────────────┐
│   ├── schema.py ───────────────────┼──▶ (no internal deps)
│   └── defaults.py ─────────────────┘
│
└── utils
    ├── http.py ─────────────────────┐
    ├── text.py ─────────────────────┼──▶ (no internal deps)
    ├── logging.py ──────────────────┤
    └── metrics.py ──────────────────┘
```

### 4.2 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│                    (cli, api)                                    │
│         • User interaction                                       │
│         • Request/response handling                              │
│         • Output formatting                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                             │
│                    (core, digest)                                │
│         • Business logic                                         │
│         • Orchestration                                          │
│         • Domain models                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                                  │
│                    (analyzers, parsers)                          │
│         • Domain-specific logic                                  │
│         • Text analysis                                          │
│         • Content parsing                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                          │
│                    (ingestors, storage, utils)                   │
│         • External integrations                                  │
│         • Data persistence                                       │
│         • Utilities                                              │
└─────────────────────────────────────────────────────────────────┘
```

**Dependency Rule:** Higher layers can depend on lower layers, not vice versa.

---

## 5. API Design

### 5.1 REST API Structure

```
/v1
├── /extract
│   └── POST    Extract content from URL
│
├── /digest
│   └── POST    Generate digest from sources
│
├── /webhooks
│   ├── POST    Register webhook
│   ├── GET     List webhooks
│   ├── DELETE  Remove webhook
│   └── POST    /:id/test   Test webhook
│
└── /health
    └── GET     Health check
```

### 5.2 Request/Response Models

```python
# Request Models (Pydantic)

class ExtractRequest(BaseModel):
    url: HttpUrl
    mode: Literal["conservative", "standard", "aggressive"] = "standard"
    include_stats: bool = True
    include_removed: bool = False

class DigestRequest(BaseModel):
    sources: List[SourceConfig]
    period: str = "24h"  # Duration string
    format: Literal["json", "markdown", "html"] = "json"
    cluster: bool = True
    dedupe: bool = True

class WebhookRequest(BaseModel):
    url: HttpUrl
    triggers: WebhookTriggers

class WebhookTriggers(BaseModel):
    min_novelty: float = 0.8
    topics: List[str] = []
    keywords: List[str] = []

# Response Models

class ExtractResponse(BaseModel):
    id: str
    url: str
    title: Optional[str]
    source: Optional[str]
    published: Optional[datetime]
    processed: datetime
    extracted: ExtractedContent
    statistics: Optional[ExtractionStats]
    warnings: List[Warning]

class ExtractedContent(BaseModel):
    text: str
    claims: List[Claim]

class ExtractionStats(BaseModel):
    original_words: int
    compressed_words: int
    compression_ratio: float
    original_density: float
    compressed_density: float
    novel_claims: int
    named_sources: int
    unnamed_sources: int
    emotional_words_removed: int
    speculation_sentences_removed: int
    repeated_sentences_collapsed: int

class DigestResponse(BaseModel):
    generated_at: datetime
    period: str
    sources_processed: int
    articles_analyzed: int
    topics: List[DigestTopic]
    meta_stats: DigestStats

class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    uptime: int  # seconds
```

### 5.3 Error Response Format

```python
class ErrorResponse(BaseModel):
    error: str
    code: str
    details: Optional[dict] = None
    request_id: str

# Error Codes
# - INVALID_URL: URL format invalid or unreachable
# - EXTRACTION_FAILED: Could not extract content
# - RATE_LIMITED: Too many requests
# - UNAUTHORIZED: Invalid or missing API key
# - INTERNAL_ERROR: Server error
```

### 5.4 API Authentication Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                            │
└──────────────────────────────────────────────────────────────────┘

Request                    Middleware                    Handler
───────                    ──────────                    ───────

Authorization:      ┌─────────────────────┐
Bearer <token>      │   Extract Token     │
     │              │   from header       │
     ├─────────────▶│                     │
     │              └─────────────────────┘
     │                        │
     │                        ▼
     │              ┌─────────────────────┐
     │              │   Validate Token    │
     │              │   • Check format    │
     │              │   • Check expiry    │
     │              │   • Lookup in DB    │
     │              └─────────────────────┘
     │                        │
     │               ┌────────┴────────┐
     │               ▼                 ▼
     │            Valid            Invalid
     │               │                 │
     │               ▼                 ▼
     │        ┌───────────┐     ┌───────────┐
     │        │ Set user  │     │  Return   │
     │        │ context   │     │  401      │
     │        └───────────┘     └───────────┘
     │               │
     │               ▼
     │        ┌───────────────────────┐
     │        │   Check Rate Limit    │
     │        │   by user tier        │
     │        └───────────────────────┘
     │               │
     │        ┌──────┴──────┐
     │        ▼             ▼
     │    Under Limit   Over Limit
     │        │             │
     │        ▼             ▼
     │   Continue      Return 429
     │   to handler
     │        │
     │        ▼
              Handler executes
```

---

## 6. Data Models

### 6.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA MODEL RELATIONSHIPS                          │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Article    │         │   Sentence   │         │    Claim     │
├──────────────┤         ├──────────────┤         ├──────────────┤
│ id           │◀───┐    │ text         │    ┌───▶│ text         │
│ url          │    │    │ index        │    │    │ claim_type   │
│ title        │    │    │ tokens[]     │    │    │ source       │
│ content      │    │    │ pos_tags[]   │    │    │ confidence   │
│ source_name  │    │    │ entities[]   │    │    │ sentence_idx │
│ source_type  │    │    │ density_score│    │    └──────────────┘
│ author       │    │    │ novelty_score│    │
│ published_at │    │    │ category     │    │
│ fetched_at   │    │    │ keep         │    │
│ word_count   │    │    │ removal_rsn  │    │
│ language     │    └────│ article_id   │────┘
└──────────────┘         └──────────────┘
       │                        │
       │                        │
       ▼                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                       ExtractionResult                            │
├──────────────────────────────────────────────────────────────────┤
│ id                                                                │
│ url                                                               │
│ title                                                             │
│ source                                                            │
│ published_at                                                      │
│ processed_at                                                      │
│ text                        ◀─── Compressed output                │
│ claims[]                    ◀─── List[Claim]                      │
│ sources_named[]             ◀─── List[str]                        │
│ warnings[]                  ◀─── List[Warning]                    │
│ removed[]                   ◀─── List[RemovedContent]             │
│ statistics                  ◀─── ExtractionStatistics             │
│ original_text               ◀─── For comparison mode              │
│ sentences[]                 ◀─── List[Sentence]                   │
└──────────────────────────────────────────────────────────────────┘
       │
       │ (aggregated into)
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                           Digest                                  │
├──────────────────────────────────────────────────────────────────┤
│ generated_at                                                      │
│ period                                                            │
│ topics[]                    ◀─── List[DigestTopic]                │
│ sources_processed                                                 │
│ articles_analyzed                                                 │
│ total_original_words                                              │
│ total_compressed_words                                            │
│ emotional_removed                                                 │
│ unnamed_sources_flagged                                           │
│ speculation_stripped                                              │
│ duplicates_collapsed                                              │
└──────────────────────────────────────────────────────────────────┘
       │
       │ contains
       ▼
┌──────────────┐         ┌──────────────┐
│ DigestTopic  │         │  DigestItem  │
├──────────────┤         ├──────────────┤
│ name         │    ┌───▶│ id           │
│ emoji        │    │    │ summary      │
│ items[]      │────┘    │ article_count│
└──────────────┘         │ sources[]    │
                         │ urls[]       │
                         │ topic        │
                         │ subtopic     │
                         │ earliest     │
                         │ latest       │
                         │ orig_words   │
                         │ comp_words   │
                         └──────────────┘
```

### 6.2 State Transitions

```
┌─────────────────────────────────────────────────────────────────┐
│                   SENTENCE STATE MACHINE                         │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │   CREATED   │
                    │ (from NLP)  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
              ┌─────│  ANALYZING  │─────┐
              │     └─────────────┘     │
              │            │            │
              ▼            │            ▼
       ┌───────────┐       │     ┌───────────┐
       │  FLAGGED  │       │     │  REMOVED  │
       │(warning)  │       │     │           │
       └───────────┘       │     └───────────┘
              │            │
              │            │
              ▼            ▼
              └────▶┌───────────┐
                    │   KEPT    │
                    │           │
                    └───────────┘
```

---

## 7. Storage Architecture

### 7.1 Storage Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     STORAGE ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        In-Memory Cache                           │
├─────────────────────────────────────────────────────────────────┤
│ • URL content cache (TTL: 1 hour)                                │
│ • NLP model cache (singleton)                                    │
│ • Configuration cache                                            │
│                                                                  │
│ Implementation: dict with TTL wrapper or cachetools              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      File-Based Storage                          │
├─────────────────────────────────────────────────────────────────┤
│ Location: ~/.newsdigest/                                         │
│                                                                  │
│ ├── config.yml          # User configuration                    │
│ ├── sources.yml         # Saved sources                         │
│ ├── cache/                                                       │
│ │   └── articles/       # Cached article content                │
│ ├── data/                                                        │
│ │   └── analytics.db    # SQLite for analytics                  │
│ └── logs/                                                        │
│     └── newsdigest.log  # Application logs                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Analytics Database (SQLite)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ extractions                                                      │
│ ├── id (TEXT, PK)                                               │
│ ├── url (TEXT)                                                  │
│ ├── source_name (TEXT)                                          │
│ ├── extracted_at (DATETIME)                                     │
│ ├── original_words (INT)                                        │
│ ├── compressed_words (INT)                                      │
│ ├── compression_ratio (REAL)                                    │
│ ├── density_before (REAL)                                       │
│ ├── density_after (REAL)                                        │
│ ├── claims_count (INT)                                          │
│ ├── emotional_removed (INT)                                     │
│ └── speculation_removed (INT)                                   │
│                                                                  │
│ sources                                                          │
│ ├── id (TEXT, PK)                                               │
│ ├── name (TEXT)                                                 │
│ ├── type (TEXT)                                                 │
│ ├── url (TEXT)                                                  │
│ ├── added_at (DATETIME)                                         │
│ ├── last_fetched (DATETIME)                                     │
│ └── article_count (INT)                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Cache Strategy

```python
class CacheConfig:
    # Content cache
    content_ttl: int = 3600  # 1 hour
    content_max_size: int = 1000  # entries

    # NLP model (loaded once)
    nlp_model: str = "en_core_web_sm"

    # Analytics write buffer
    analytics_batch_size: int = 100
    analytics_flush_interval: int = 60  # seconds
```

---

## 8. Concurrency Model

### 8.1 Async Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONCURRENCY MODEL                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Event Loop (asyncio)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│   │  HTTP I/O   │   │  File I/O   │   │   Timers    │          │
│   │  (httpx)    │   │  (aiofiles) │   │ (scheduling)│          │
│   └─────────────┘   └─────────────┘   └─────────────┘          │
│          │                 │                 │                   │
│          └─────────────────┼─────────────────┘                   │
│                            │                                     │
│                            ▼                                     │
│                    ┌───────────────┐                            │
│                    │  Task Queue   │                            │
│                    └───────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Batch Processing:
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│   async def extract_batch(urls: List[str], max_concurrent=5):   │
│       semaphore = asyncio.Semaphore(max_concurrent)              │
│                                                                  │
│       async def extract_one(url):                                │
│           async with semaphore:                                  │
│               return await extractor.extract(url)                │
│                                                                  │
│       tasks = [extract_one(url) for url in urls]                │
│       results = await asyncio.gather(*tasks,                    │
│                                       return_exceptions=True)    │
│       return results                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Rate Limiting

```python
class RateLimiter:
    """Per-domain rate limiting."""

    def __init__(self, requests_per_second: float = 1.0):
        self.rps = requests_per_second
        self.last_request: Dict[str, float] = {}
        self.lock = asyncio.Lock()

    async def acquire(self, domain: str):
        async with self.lock:
            now = time.time()
            last = self.last_request.get(domain, 0)
            wait_time = max(0, (1 / self.rps) - (now - last))
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.last_request[domain] = time.time()
```

---

## 9. Error Handling

### 9.1 Error Hierarchy

```
NewsDigestError (base)
├── ConfigError
│   ├── ConfigNotFoundError
│   ├── ConfigValidationError
│   └── ConfigPermissionError
│
├── IngestError
│   ├── FetchError
│   │   ├── NetworkError
│   │   ├── TimeoutError
│   │   └── RateLimitError
│   ├── ParseError
│   │   ├── HTMLParseError
│   │   ├── RSSParseError
│   │   └── PDFParseError
│   └── UnsupportedSourceError
│
├── ExtractionError
│   ├── NLPError
│   ├── AnalysisError
│   └── EmptyContentError
│
├── FormatterError
│   └── TemplateError
│
└── APIError
    ├── AuthenticationError
    ├── RateLimitError
    └── ValidationError
```

### 9.2 Error Handling Strategy

```python
# Retry with backoff for transient errors
@retry(
    retry=retry_if_exception_type(NetworkError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def fetch_url(url: str) -> str:
    ...

# Graceful degradation
async def extract_with_fallback(url: str) -> ExtractionResult:
    try:
        return await full_extraction(url)
    except NLPError:
        logger.warning("NLP failed, using basic extraction")
        return await basic_extraction(url)
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise ExtractionError(f"Could not extract: {url}") from e
```

---

## 10. Security Architecture

### 10.1 Security Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY BOUNDARIES                           │
└─────────────────────────────────────────────────────────────────┘

    UNTRUSTED                    BOUNDARY                 TRUSTED
    ─────────                    ────────                 ───────

    User URLs          ──▶    URL Validator       ──▶    Fetcher
    (arbitrary)               • Scheme whitelist         (sanitized)
                              • SSRF prevention
                              • Domain blocklist

    HTML Content       ──▶    HTML Sanitizer      ──▶    Parser
    (potentially               • Remove scripts          (clean)
     malicious)               • Remove iframes
                              • Limit nesting

    User Config        ──▶    YAML Safe Load     ──▶    Config
    (yaml files)              • No code execution        (validated)
                              • Schema validation

    API Input          ──▶    Pydantic Models    ──▶    Handlers
    (json payloads)           • Type validation          (typed)
                              • Size limits
                              • Sanitization
```

### 10.2 Security Checklist

| Concern | Mitigation |
|---------|------------|
| SSRF | Validate URL schemes (http/https only), block private IPs |
| XSS | HTML output escaped, CSP headers in API |
| Injection | Parameterized queries, no shell execution |
| DoS | Rate limiting, request size limits, timeouts |
| Secrets | Environment variables, not in config files |
| Dependencies | Regular audits with pip-audit |

---

## 11. Deployment Architecture

### 11.1 Local Installation

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL INSTALLATION                            │
└─────────────────────────────────────────────────────────────────┘

User Machine
├── Python 3.11+
├── pip/pipx
│
└── newsdigest (installed package)
    ├── CLI binary in PATH
    ├── ~/.newsdigest/
    │   ├── config.yml
    │   ├── sources.yml
    │   ├── cache/
    │   ├── data/analytics.db
    │   └── logs/
    │
    └── spaCy model (~12-560MB)
        └── ~/.cache/spacy/
```

### 11.2 Docker Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER DEPLOYMENT                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Docker Container                              │
├─────────────────────────────────────────────────────────────────┤
│  Base: python:3.11-slim                                          │
│                                                                  │
│  /app                                                            │
│  ├── newsdigest/       (application code)                       │
│  └── models/           (spaCy models, pre-downloaded)           │
│                                                                  │
│  Volumes:                                                        │
│  ├── /config           (mounted: config.yml)                    │
│  └── /data             (mounted: persistent data)               │
│                                                                  │
│  Ports:                                                          │
│  └── 8080              (API server)                             │
│                                                                  │
│  Environment:                                                    │
│  ├── NEWSDIGEST_CONFIG=/config/config.yml                       │
│  ├── NEWSAPI_KEY=xxx                                            │
│  └── SMTP_*=xxx                                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 11.3 Production API Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                  PRODUCTION DEPLOYMENT                           │
└─────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │   Internet   │
                         └──────┬───────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     Load Balancer     │
                    │     (nginx/HAProxy)   │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
      ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
      │   API Pod 1   │ │   API Pod 2   │ │   API Pod 3   │
      │   (uvicorn)   │ │   (uvicorn)   │ │   (uvicorn)   │
      └───────────────┘ └───────────────┘ └───────────────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
            ┌───────────────┐       ┌───────────────┐
            │     Redis     │       │   PostgreSQL  │
            │   (caching)   │       │  (analytics)  │
            └───────────────┘       └───────────────┘
```

---

*End of Architecture Document*
