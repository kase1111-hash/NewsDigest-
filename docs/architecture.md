# NewsDigest Architecture

This document describes the system architecture, component interactions, and data flow of NewsDigest.

## System Overview

NewsDigest is a semantic compression engine that transforms news content into concise, factual summaries by removing speculation, emotional language, and redundant content.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              NewsDigest System                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   CLI/API   │───▶│  Ingestors  │───▶│   Parsers   │───▶│  Analyzers  │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                                                        │          │
│         │                                                        ▼          │
│         │          ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│         └─────────▶│  Formatters │◀───│    Core     │◀───│   Digest    │   │
│                    └─────────────┘    └─────────────┘    └─────────────┘   │
│                          │                   │                              │
│                          ▼                   ▼                              │
│                    ┌─────────────┐    ┌─────────────┐                      │
│                    │   Output    │    │   Storage   │                      │
│                    └─────────────┘    └─────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

```mermaid
graph TB
    subgraph "Entry Points"
        CLI[CLI Interface]
        API[REST API]
        SDK[Python SDK]
    end

    subgraph "Ingestors"
        URL[URL Fetcher]
        RSS[RSS Parser]
        TXT[Text Ingestor]
    end

    subgraph "Parsers"
        HTML[HTML Parser]
        ART[Article Extractor]
    end

    subgraph "Core Engine"
        EXT[Extractor]
        PIPE[Analysis Pipeline]
    end

    subgraph "Analyzers"
        NLP[NLP Analyzer]
        SENT[Sentence Analyzer]
        SPEC[Speculation Detector]
        EMO[Emotion Detector]
        QUOTE[Quote Analyzer]
    end

    subgraph "Digest"
        CLUST[Clustering]
        DEDUP[Deduplication]
        GEN[Digest Generator]
    end

    subgraph "Formatters"
        JSON[JSON Formatter]
        MD[Markdown Formatter]
        TEXT[Text Formatter]
    end

    subgraph "Infrastructure"
        CFG[Config]
        LOG[Logging]
        ERR[Error Handling]
        MET[Metrics]
        TEL[Telemetry]
    end

    CLI --> EXT
    API --> EXT
    SDK --> EXT

    EXT --> URL
    EXT --> RSS
    EXT --> TXT

    URL --> HTML
    RSS --> ART
    TXT --> ART
    HTML --> ART

    ART --> PIPE

    PIPE --> NLP
    PIPE --> SENT
    PIPE --> SPEC
    PIPE --> EMO
    PIPE --> QUOTE

    EXT --> GEN
    GEN --> CLUST
    GEN --> DEDUP

    EXT --> JSON
    EXT --> MD
    EXT --> TEXT
    GEN --> JSON
    GEN --> MD
    GEN --> TEXT

    CFG -.-> EXT
    LOG -.-> EXT
    ERR -.-> EXT
    MET -.-> EXT
    TEL -.-> EXT
```

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph Input
        A[URL/RSS/Text]
    end

    subgraph Ingestion
        B[Fetch Content]
        C[Parse HTML]
        D[Extract Article]
    end

    subgraph Analysis
        E[Tokenize]
        F[NLP Processing]
        G[Sentence Analysis]
        H[Content Filtering]
    end

    subgraph Output
        I[Format Results]
        J[JSON/MD/Text]
    end

    A --> B --> C --> D --> E --> F --> G --> H --> I --> J
```

## Detailed Data Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           EXTRACTION DATA FLOW                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────┐     ┌─────────┐     ┌─────────┐     ┌──────────┐                │
│  │ Source │────▶│ Ingest  │────▶│  Parse  │────▶│ Tokenize │                │
│  │URL/RSS │     │ Content │     │  HTML   │     │   Text   │                │
│  └────────┘     └─────────┘     └─────────┘     └──────────┘                │
│                                                       │                      │
│                                                       ▼                      │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        ANALYSIS PIPELINE                                │ │
│  ├────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │ │
│  │  │    NLP      │  │  Sentence   │  │ Speculation │  │  Emotional  │   │ │
│  │  │  Analysis   │──│  Density    │──│  Detection  │──│  Language   │   │ │
│  │  │ (spaCy)     │  │   Score     │  │             │  │  Detection  │   │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │ │
│  │         │                                                  │           │ │
│  │         ▼                                                  ▼           │ │
│  │  ┌─────────────┐                                   ┌─────────────┐    │ │
│  │  │   Quote     │                                   │   Hedge     │    │ │
│  │  │  Analysis   │                                   │  Detection  │    │ │
│  │  └─────────────┘                                   └─────────────┘    │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                       │                                      │
│                                       ▼                                      │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                    │
│  │   Filter    │────▶│  Compress   │────▶│   Format    │                    │
│  │  Content    │     │   Output    │     │   Result    │                    │
│  └─────────────┘     └─────────────┘     └─────────────┘                    │
│                                                 │                            │
│                                                 ▼                            │
│                                          ┌───────────┐                       │
│                                          │  Output   │                       │
│                                          │JSON/MD/TXT│                       │
│                                          └───────────┘                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Digest Generation Flow

```mermaid
flowchart TB
    subgraph Sources
        S1[RSS Feed 1]
        S2[RSS Feed 2]
        S3[URL]
    end

    subgraph Extraction
        E1[Extract Articles]
        E2[Compress Content]
    end

    subgraph Processing
        C[Cluster by Topic]
        D[Deduplicate]
        R[Rank by Relevance]
    end

    subgraph Output
        G[Generate Digest]
        F[Format Output]
    end

    S1 --> E1
    S2 --> E1
    S3 --> E1
    E1 --> E2
    E2 --> C
    C --> D
    D --> R
    R --> G
    G --> F
```

## Module Dependencies

```
newsdigest/
├── __init__.py          # Package exports
├── version.py           # Version info
├── exceptions.py        # Custom exceptions
│
├── config/              # Configuration management
│   └── settings.py      # Config dataclasses
│
├── core/                # Core extraction engine
│   ├── extractor.py     # Main Extractor class
│   ├── pipeline.py      # Analysis pipeline
│   ├── article.py       # Article model
│   └── result.py        # Result models
│
├── ingestors/           # Content ingestion
│   ├── url.py           # URL fetcher
│   ├── rss.py           # RSS parser
│   └── text.py          # Text ingestor
│
├── parsers/             # Content parsing
│   └── article.py       # HTML/article extraction
│
├── analyzers/           # Content analysis
│   ├── nlp.py           # NLP processing
│   ├── sentence.py      # Sentence analysis
│   ├── speculation.py   # Speculation detection
│   ├── emotion.py       # Emotion detection
│   └── quotes.py        # Quote analysis
│
├── digest/              # Digest generation
│   ├── generator.py     # Digest generator
│   ├── clustering.py    # Topic clustering
│   └── dedup.py         # Deduplication
│
├── formatters/          # Output formatting
│   ├── json.py          # JSON formatter
│   ├── markdown.py      # Markdown formatter
│   └── text.py          # Plain text formatter
│
├── utils/               # Utilities
│   ├── http.py          # HTTP client
│   ├── logging.py       # Logging setup
│   ├── errors.py        # Error handling
│   ├── metrics.py       # Metrics collection
│   ├── telemetry.py     # Telemetry
│   ├── text.py          # Text utilities
│   └── validation.py    # Input validation
│
├── cli/                 # Command-line interface
│   └── main.py          # CLI entry point
│
├── api/                 # REST API
│   └── routes/          # API route handlers
│
└── storage/             # Data persistence
    └── cache.py         # Caching layer
```

## Sequence Diagram: Single Article Extraction

```mermaid
sequenceDiagram
    participant User
    participant Extractor
    participant URLFetcher
    participant ArticleExtractor
    participant Pipeline
    participant Analyzers
    participant Formatter

    User->>Extractor: extract(url)
    Extractor->>URLFetcher: fetch(url)
    URLFetcher-->>Extractor: HTML content
    Extractor->>ArticleExtractor: extract(html)
    ArticleExtractor-->>Extractor: Article object
    Extractor->>Pipeline: analyze(article)

    loop For each analyzer
        Pipeline->>Analyzers: process(sentences)
        Analyzers-->>Pipeline: analysis results
    end

    Pipeline-->>Extractor: ExtractionResult
    Extractor->>Formatter: format(result)
    Formatter-->>User: Formatted output
```

## Sequence Diagram: Digest Generation

```mermaid
sequenceDiagram
    participant User
    participant DigestGenerator
    participant Extractor
    participant Clustering
    participant Dedup
    participant Formatter

    User->>DigestGenerator: generate()

    loop For each source
        DigestGenerator->>Extractor: extract(source)
        Extractor-->>DigestGenerator: ExtractionResult
    end

    DigestGenerator->>Clustering: cluster(articles)
    Clustering-->>DigestGenerator: clustered articles

    DigestGenerator->>Dedup: deduplicate(clusters)
    Dedup-->>DigestGenerator: unique articles

    DigestGenerator->>Formatter: format(digest)
    Formatter-->>User: Formatted digest
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DEPLOYMENT OPTIONS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Option 1: Python Package                        │   │
│  │  ┌─────────┐                                                        │   │
│  │  │  pip    │──▶ newsdigest (from PyPI or local)                     │   │
│  │  │ install │                                                        │   │
│  │  └─────────┘                                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Option 2: Docker Container                      │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │   │
│  │  │   Docker    │───▶│  NewsDigest │───▶│  REST API   │              │   │
│  │  │   Image     │    │  Container  │    │  :8080      │              │   │
│  │  └─────────────┘    └─────────────┘    └─────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Option 3: Standalone Binary                     │   │
│  │  ┌─────────────┐                                                    │   │
│  │  │ PyInstaller │──▶ newsdigest executable (Linux/Mac/Windows)       │   │
│  │  │   Binary    │                                                    │   │
│  │  └─────────────┘                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```mermaid
flowchart TB
    A[Operation] --> B{Success?}
    B -->|Yes| C[Return Result]
    B -->|No| D{Error Type}

    D -->|Network| E[FetchError]
    D -->|Parse| F[ParseError]
    D -->|Analysis| G[AnalysisError]
    D -->|Config| H[ConfigurationError]

    E --> I[Log Error]
    F --> I
    G --> I
    H --> I

    I --> J[Capture Metrics]
    J --> K[Return Error Response]
```

## Configuration Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    Configuration Sources                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Priority (highest to lowest):                                  │
│                                                                 │
│  1. ┌─────────────────┐                                        │
│     │ Runtime Args    │  CLI flags, API parameters              │
│     └────────┬────────┘                                        │
│              ▼                                                  │
│  2. ┌─────────────────┐                                        │
│     │ Environment     │  NEWSDIGEST_* variables                 │
│     │ Variables       │                                        │
│     └────────┬────────┘                                        │
│              ▼                                                  │
│  3. ┌─────────────────┐                                        │
│     │ Config File     │  config/*.yaml                          │
│     └────────┬────────┘                                        │
│              ▼                                                  │
│  4. ┌─────────────────┐                                        │
│     │ Defaults        │  Built-in defaults                      │
│     └─────────────────┘                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| NLP | spaCy |
| HTTP Client | httpx (async) |
| HTML Parsing | BeautifulSoup4, lxml |
| Article Extraction | readability-lxml |
| RSS Parsing | feedparser |
| Configuration | Pydantic, python-dotenv |
| CLI | Click, Rich |
| API Framework | FastAPI (planned) |
| Testing | pytest, pytest-asyncio |
| Type Checking | mypy |
| Linting | ruff |
| Documentation | MkDocs |
