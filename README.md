# NewsDigest

**Your 4-hour news habit, compressed to 5 minutes of actual information.**

[![License: Polyform Small Business](https://img.shields.io/badge/License-Polyform%20Small%20Business-blue.svg)](./LICENSE.md)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)]()

---

## What Is This?

NewsDigest is a semantic compression engine for news. It ingests articles, strips the filler, and outputs only what's actually new, actually sourced, and actually informative.

It doesn't summarize. It **extracts signal from noise**.

---

## The Problem

Modern news is optimized for engagement, not information transfer.

A typical news article:

```
BREAKING: Shocking New Study Reveals Alarming Trend That Has 
Experts Worried About What This Means For You And Your Family

In a stunning development that has sent shockwaves through the 
scientific community, researchers have discovered something that 
many are calling unprecedented...

[800 words later]

...the study found a 3% increase in X among Y population.

Experts say more research is needed.
```

**Actual information content: 2 sentences.**
**Filler: 94%**

You're not reading news. You're reading engagement architecture wrapped around a few facts.

---

## The Solution

NewsDigest performs semantic extraction:

```
INPUT: 847-word article about economic policy

OUTPUT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Federal Reserve held interest rates at 5.25-5.50% (unchanged 
from December). Powell indicated potential cuts in "latter half 
of 2025" but declined to specify timing. Vote was 11-1 
(Bowman dissented, favoring 0.25% cut).

Source: Federal Reserve press release, January 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPRESSION: 847 words → 52 words (94% filler removed)
NOVEL CLAIMS: 3
NAMED SOURCES: 1
SPECULATION REMOVED: 12 sentences
```

---

## Features

### Core Analysis

| Feature | Description |
|---------|-------------|
| **Filler Detection** | Identifies sentences with no information content |
| **Speculation Stripping** | Removes "could," "might," "may indicate" padding |
| **Source Validation** | Flags "sources say" without named attribution |
| **Emotional Deactivation** | Strips "shocking," "alarming," "unprecedented" |
| **Repetition Collapse** | Merges repeated information across paragraphs |
| **Novelty Scoring** | Identifies what's actually new vs. restated background |
| **Claim Extraction** | Pulls falsifiable statements from narrative wrapper |
| **Quote Isolation** | Separates direct quotes from paraphrase |

### Output Modes

| Mode | Description |
|------|-------------|
| **Extract** | Just the facts, minimal prose |
| **Compress** | Readable summary, filler removed |
| **Compare** | Side-by-side original vs. compressed |
| **Annotate** | Original with filler highlighted |
| **Stats** | Metadata only (density, sources, claims) |

### Input Sources

- **Single URL** — Paste any article
- **RSS Feeds** — Subscribe to publications
- **News APIs** — NewsAPI, GDELT, MediaStack integration
- **Email Newsletters** — Forward to your NewsDigest inbox
- **Twitter/X Lists** — Extract claims from threads
- **PDF/Documents** — Press releases, reports

---

## Installation

### CLI Tool

```bash
# Via pip
pip install newsdigest

# Via pipx (recommended)
pipx install newsdigest

# From source
git clone https://github.com/yourusername/newsdigest.git
cd newsdigest
pip install -e .
```

### Requirements

- Python 3.11+
- ~1.5GB disk space (language models)
- Internet connection (for fetching articles)

### First Run

```bash
# Download models
newsdigest setup

# Verify installation
newsdigest --version
```

---

## Quick Start

### Single Article

```bash
# Analyze a URL
newsdigest extract https://example.com/article

# From stdin
curl -s https://example.com/article | newsdigest extract -

# With comparison view
newsdigest compare https://example.com/article

# Just the stats
newsdigest stats https://example.com/article
```

### Daily Digest

```bash
# Set up your sources
newsdigest sources add --rss https://feeds.example.com/news
newsdigest sources add --rss https://other.example.com/feed

# Generate morning digest
newsdigest digest --period 24h

# Email it to yourself
newsdigest digest --period 24h --email you@example.com
```

### Watch Mode

```bash
# Real-time monitoring
newsdigest watch --sources my-feeds.yml --interval 30m

# Output to file
newsdigest watch --sources my-feeds.yml --output ~/news/
```

---

## Understanding the Output

### Compression Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARTICLE: "Markets React to Federal Reserve Decision"
SOURCE:  Example News Network
DATE:    2025-01-11
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXTRACTED CONTENT:
──────────────────
Federal Reserve held rates at 5.25-5.50%. Chair Powell cited 
"persistent inflation concerns" but noted labor market 
"remains solid." Vote was 11-1. S&P 500 closed down 0.3% 
following announcement.

STATISTICS:
──────────────────
Original length:        1,247 words
Compressed length:      48 words
Compression ratio:      96.1%
Semantic density:       0.09 → 0.84

Content breakdown:
  ├─ Novel claims:      4
  ├─ Background/context: 23 sentences (removed)
  ├─ Speculation:       8 sentences (removed)
  ├─ Repetition:        6 sentences (collapsed)
  ├─ Emotional language: 14 instances (stripped)
  └─ Unnamed sources:   2 (flagged)

Named sources:          
  ├─ Federal Reserve (primary)
  ├─ Jerome Powell (quoted)
  └─ Michelle Bowman (dissent noted)

Unnamed sources (⚠️):
  ├─ "analysts say" (sentence 7)
  └─ "sources familiar with" (sentence 19)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Filler Categories

The system identifies and categorizes removed content:

#### `EMOTIONAL_ACTIVATION`
Words designed to trigger response, not convey information.

```
REMOVED: "In a shocking development that has experts alarmed..."
REASON:  "shocking," "alarmed" are activation words
KEPT:    (nothing—sentence contained no facts)
```

#### `SPECULATION`
Statements about what might/could/may happen.

```
REMOVED: "This could potentially signal a shift in policy 
         that might have implications for markets."
REASON:  "could potentially," "might have"—no falsifiable claim
```

#### `UNNAMED_SOURCE`
Attribution without accountability.

```
FLAGGED: "Sources familiar with the matter say..."
REASON:  Who? How familiar? Verify or treat as rumor.
STATUS:  Kept but marked ⚠️
```

#### `BACKGROUND_REPEAT`
Context restated across paragraphs.

```
REMOVED: Paragraphs 3, 7, 12 (all restating Fed's mandate)
REASON:  Information appeared in paragraph 1
```

#### `CIRCULAR_QUOTE`
Quotes that restate what was just reported.

```
REMOVED: '"This is an important decision," said analyst 
         John Smith. "The Fed\'s decision today is significant."'
REASON:  Quote adds no information beyond "decision happened"
```

#### `HEDGE_PADDING`
Excessive qualification that obscures claims.

```
ORIGINAL: "It would appear that there may be some indication 
          that the economy could perhaps be showing signs of 
          what some might characterize as improvement."
          
COMPRESSED: "Economic indicators suggest improvement."
REMOVED:   18 words of hedging
```

#### `ENGAGEMENT_HOOK`
Sentences designed to retain attention, not inform.

```
REMOVED: "What happened next will surprise you."
REMOVED: "But that's not the whole story."
REMOVED: "Here's what you need to know."
REASON:  Zero information content
```

---

## Comparison Mode

The killer feature. See exactly what was removed:

```bash
newsdigest compare https://example.com/article
```

Output:
```
┌─────────────────────────────────┬────────────────────────────────┐
│ ORIGINAL                        │ EXTRACTED                      │
├─────────────────────────────────┼────────────────────────────────┤
│ In a stunning development that  │                                │
│ has sent shockwaves through     │                                │
│ Washington, [EMOTIONAL]         │                                │
│                                 │                                │
│ President Biden announced       │ Biden announced $2B            │
│ today a sweeping new $2 billion │ infrastructure program for     │
│ infrastructure program that     │ rural broadband. Funding       │
│ officials say will bring high-  │ from Inflation Reduction Act.  │
│ speed internet to rural         │ Rollout begins March 2025.     │
│ communities across America.     │                                │
│                                 │                                │
│ "This is a game-changer," said  │ [CIRCULAR_QUOTE removed]       │
│ one administration official who │                                │
│ spoke on condition of           │                                │
│ anonymity. [UNNAMED_SOURCE ⚠️]  │                                │
│                                 │                                │
│ The program, which draws        │                                │
│ funding from the historic       │                                │
│ Inflation Reduction Act passed  │                                │
│ in 2022, represents the latest  │                                │
│ effort by the administration    │                                │
│ to address what experts call    │                                │
│ [BACKGROUND continues 200       │                                │
│ words...]                       │                                │
│                                 │                                │
│ Implementation is expected to   │                                │
│ begin in March 2025, according  │                                │
│ to the White House.             │                                │
│                                 │                                │
├─────────────────────────────────┼────────────────────────────────┤
│ WORDS: 487                      │ WORDS: 24                      │
│ DENSITY: 0.11                   │ DENSITY: 0.89                  │
│ NOVEL CLAIMS: 3                 │ NOVEL CLAIMS: 3                │
│ FILLER: 95%                     │ FILLER: 0%                     │
└─────────────────────────────────┴────────────────────────────────┘
```

Once you see it, you can't unsee it.

---

## Daily Digest

### Configuration

```yaml
# ~/.newsdigest/config.yml

# Your information diet
sources:
  # RSS feeds
  - type: rss
    url: https://feeds.reuters.com/reuters/topNews
    name: Reuters
    
  - type: rss
    url: https://rss.nytimes.com/services/xml/rss/nyt/World.xml
    name: NYT World
    
  # News API (requires key)
  - type: newsapi
    query: "technology"
    language: en
    
  # Specific publication
  - type: rss
    url: https://www.economist.com/finance-and-economics/rss.xml
    name: Economist Finance

# Digest settings
digest:
  # How far back to look
  period: 24h
  
  # Maximum items before summarizing
  max_items: 50
  
  # Group by topic
  clustering: true
  
  # Dedup across sources
  deduplication: true
  
  # Minimum novelty to include
  min_novelty: 0.3
  
# Output
output:
  format: markdown  # or: html, json, email
  
  # Include comparison stats
  show_compression: true
  
  # Include source links
  include_links: true

# Email delivery (optional)
email:
  enabled: true
  to: you@example.com
  schedule: "0 7 * * *"  # 7 AM daily
  smtp:
    host: smtp.example.com
    user: ${SMTP_USER}
    pass: ${SMTP_PASS}
```

### Sample Digest Output

```markdown
# NewsDigest: January 11, 2025

**Coverage period:** 24 hours
**Sources processed:** 12
**Articles analyzed:** 847
**After compression:** 43 items (95% noise removed)

---

## 🌍 World

### Ukraine-Russia

Russian forces claimed control of Chasiv Yar (Donetsk region). 
Ukraine's General Staff confirmed "difficult situation" but not 
full capture. 3 Russian ammunition depots struck overnight per 
Ukrainian military. EU announced €5B additional military aid 
package, disbursement begins February.

*Sources: Reuters, AP, Ukrainian General Staff*
*Compression: 12 articles → 4 sentences*

### Middle East

Israeli cabinet approved expanded operations in northern Gaza. 
UN reported 47 casualties in Jabaliya over 48 hours. Ceasefire 
negotiations "ongoing" per Qatari foreign ministry; no timeline 
provided.

*Sources: Al Jazeera, Reuters, Times of Israel*
*Compression: 8 articles → 3 sentences*

---

## 💰 Markets

Fed held rates at 5.25-5.50% (11-1 vote). Powell: cuts possible 
in "latter half of 2025." S&P 500 closed -0.3%. 10-year Treasury 
yield rose to 4.68%. Bitcoin crossed $97,000, +4.2% in 24h.

*Sources: Federal Reserve, Bloomberg, Reuters*
*Compression: 23 articles → 5 sentences*

---

## 🔬 Science/Tech

SpaceX launched Starlink batch (23 satellites, Group 9-14). 
Total constellation now 6,847 active. Falcon 9 booster completed 
20th flight, landed successfully.

DeepMind published AlphaFold 3 paper in Nature. Claims 3x 
accuracy improvement on protein-ligand binding prediction. 
Code release: "coming weeks."

*Sources: SpaceX, Nature, Ars Technica*
*Compression: 15 articles → 6 sentences*

---

## 📊 Today's Meta-Stats

| Metric | Value |
|--------|-------|
| Total words processed | 412,847 |
| Total words delivered | 847 |
| Compression ratio | 99.8% |
| Emotional language removed | 2,847 instances |
| Unnamed sources flagged | 124 |
| Speculation stripped | 1,847 sentences |
| Duplicate stories collapsed | 394 |

**Your time saved: ~3.5 hours**

---

*Generated by [NewsDigest](https://github.com/yourusername/newsdigest)*
```

---

## API Usage

### Python Library

```python
from newsdigest import Extractor, Digest, Config

# Single article extraction
extractor = Extractor()
result = extractor.extract("https://example.com/article")

print(f"Original: {result.original_length} words")
print(f"Compressed: {result.compressed_length} words")
print(f"Density: {result.original_density:.2f} → {result.compressed_density:.2f}")
print(f"\nExtracted:\n{result.text}")

# Access detailed breakdown
for claim in result.claims:
    print(f"  - {claim.text}")
    print(f"    Source: {claim.source or 'unattributed'}")
    print(f"    Confidence: {claim.confidence:.2f}")

for removed in result.removed:
    print(f"  Removed ({removed.reason}): {removed.text[:50]}...")

# Batch processing
urls = [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3",
]

results = extractor.extract_batch(urls, parallel=True)

# Generate digest
config = Config.from_file("~/.newsdigest/config.yml")
digest = Digest(config)

# From RSS feeds
digest.add_rss("https://feeds.reuters.com/reuters/topNews")
digest.add_rss("https://rss.nytimes.com/services/xml/rss/nyt/World.xml")

# Generate
output = digest.generate(period="24h", format="markdown")
print(output)

# Or get structured data
data = digest.generate(period="24h", format="dict")
for topic in data["topics"]:
    print(f"\n{topic['name']}:")
    for item in topic["items"]:
        print(f"  - {item['summary']}")
```

### REST API

```bash
# Start local server
newsdigest serve --port 8080

# Or use hosted API
export NEWSDIGEST_API_KEY=your_key_here
```

**Extract endpoint:**

```bash
curl -X POST https://api.newsdigest.dev/v1/extract \
  -H "Authorization: Bearer $NEWSDIGEST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "mode": "extract",
    "include_stats": true
  }'
```

**Response:**

```json
{
  "id": "ext_abc123",
  "url": "https://example.com/article",
  "title": "Markets React to Federal Reserve Decision",
  "source": "Example News",
  "published": "2025-01-11T14:30:00Z",
  "processed": "2025-01-11T15:42:17Z",
  
  "extracted": {
    "text": "Federal Reserve held rates at 5.25-5.50%. Chair Powell cited \"persistent inflation concerns\" but noted labor market \"remains solid.\" Vote was 11-1. S&P 500 closed down 0.3% following announcement.",
    "claims": [
      {
        "text": "Federal Reserve held rates at 5.25-5.50%",
        "type": "factual",
        "source": "Federal Reserve",
        "confidence": 0.98
      },
      {
        "text": "Vote was 11-1",
        "type": "factual", 
        "source": "Federal Reserve",
        "confidence": 0.98
      },
      {
        "text": "S&P 500 closed down 0.3%",
        "type": "factual",
        "source": "market_data",
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
  
  "removed": [
    {
      "type": "EMOTIONAL_ACTIVATION",
      "count": 14,
      "examples": ["shocking", "stunning", "alarming", "unprecedented"]
    },
    {
      "type": "SPECULATION",
      "count": 8,
      "examples": ["could potentially signal", "might indicate"]
    },
    {
      "type": "BACKGROUND_REPEAT",
      "count": 6,
      "description": "Fed mandate explanation repeated 3x"
    }
  ],
  
  "warnings": [
    {
      "type": "UNNAMED_SOURCE",
      "text": "sources familiar with the matter",
      "location": "paragraph 4"
    }
  ]
}
```

**Digest endpoint:**

```bash
curl -X POST https://api.newsdigest.dev/v1/digest \
  -H "Authorization: Bearer $NEWSDIGEST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {"type": "rss", "url": "https://feeds.reuters.com/reuters/topNews"},
      {"type": "rss", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"}
    ],
    "period": "24h",
    "format": "markdown",
    "cluster": true,
    "dedupe": true
  }'
```

### Webhooks

Get notified when high-signal news breaks:

```bash
curl -X POST https://api.newsdigest.dev/v1/webhooks \
  -H "Authorization: Bearer $NEWSDIGEST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/news-webhook",
    "triggers": {
      "min_novelty": 0.8,
      "topics": ["technology", "markets"],
      "keywords": ["Federal Reserve", "SpaceX", "AI"]
    }
  }'
```

---

## Integrations

### Browser Extension

Install from Chrome Web Store / Firefox Add-ons: `NewsDigest`

Features:
- One-click extraction on any article
- Overlay mode: highlights filler in-page
- Side panel with compressed version
- Auto-extract on supported news sites
- Right-click → "Extract with NewsDigest"

### RSS Reader Integration

**Feedbin:**
```
Filter URL: https://api.newsdigest.dev/v1/filter?key=YOUR_KEY&url=
```

**Miniflux:**
```yaml
# docker-compose.yml
services:
  miniflux:
    environment:
      - FILTER_ENTRY_URL=https://api.newsdigest.dev/v1/filter
```

**Inoreader:**
Rules → Create Rule → Filter through NewsDigest API

### Telegram Bot

```
1. Start chat with @NewsDigestBot
2. /subscribe https://feeds.reuters.com/reuters/topNews
3. /digest - Get daily summary
4. /extract <url> - Analyze single article
```

### Slack Integration

```
/newsdigest subscribe https://feeds.example.com/tech
/newsdigest digest #news-channel
/newsdigest extract https://example.com/article
```

### Raycast Extension

```bash
# Install from Raycast Store
raycast://extensions/newsdigest/newsdigest
```

Commands:
- `Extract Article` — Analyze URL from clipboard
- `Daily Digest` — Generate and display digest
- `News Stats` — Show consumption analytics

---

## Analytics Dashboard

Track your information diet:

```bash
newsdigest analytics --period 30d
```

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    YOUR NEWS CONSUMPTION: 30 DAYS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VOLUME PROCESSED
────────────────
Articles analyzed:        2,847
Total words processed:    3,412,847
Total words delivered:    28,472
Overall compression:      99.2%

TIME ANALYSIS
────────────────
Estimated reading time (original):   142 hours
Actual reading time (compressed):    2.4 hours
Time saved:                          139.6 hours

QUALITY METRICS
────────────────
Average source density:              0.08 (very low)
Average output density:              0.81 (high)
Emotional language filtered:         34,847 instances
Unnamed sources flagged:             1,247
Speculation removed:                 18,472 sentences

SOURCE BREAKDOWN
────────────────
                        Articles    Avg Density    Filler %
Reuters                    412         0.14          86%
AP News                    387         0.16          84%
NYT                        298         0.11          89%
CNN                        245         0.06          94%
Fox News                   234         0.05          95%
BBC                        312         0.13          87%
The Economist              89          0.31          69%
Ars Technica               76          0.28          72%

TOPIC DISTRIBUTION
────────────────
Politics:        34% ████████████████
Technology:      24% ████████████
Markets:         18% █████████
World:           15% ███████
Science:          9% ████

INSIGHT
────────────────
Your highest-signal source: The Economist (0.31 density)
Your lowest-signal source:  Fox News (0.05 density)

Suggestion: Consider replacing low-density sources with 
higher-signal alternatives, or rely on digest mode to 
filter automatically.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Methodology

### What Gets Kept

1. **Falsifiable claims** — Statements that could be proven true or false
2. **Named sources** — Attributed quotes and official statements
3. **Concrete data** — Numbers, dates, locations, names
4. **Novel information** — First appearance of a fact in the news cycle
5. **Direct quotes** — When they add information beyond paraphrase

### What Gets Removed

1. **Emotional activation** — Words designed to trigger, not inform
2. **Speculation** — "Could," "might," "may," "potentially" chains
3. **Background repetition** — Context restated across paragraphs
4. **Engagement hooks** — "Here's what you need to know"
5. **Circular quotes** — Sources restating what was just reported
6. **Hedge stacking** — Excessive qualification
7. **False attribution** — "Experts say" without naming experts

### What Gets Flagged (But Kept)

1. **Unnamed sources** — Kept but marked with ⚠️
2. **Contested claims** — Multiple sources disagree
3. **Corrections** — Article has been updated
4. **Opinion labeled as news** — Analysis presented as reporting

### Limitations

- **Cannot verify truth** — Extracts claims, doesn't fact-check them
- **Loses nuance** — Compression sacrifices context and caveats
- **Source-dependent** — Garbage in, garbage out
- **English-primary** — Other languages supported but less refined
- **Bias-blind** — Detects filler, not ideological slant

---

## Configuration Reference

### Full Config File

```yaml
# ~/.newsdigest/config.yml

#──────────────────────────────────────────────────────────────────
# SOURCES
#──────────────────────────────────────────────────────────────────
sources:
  # RSS/Atom feeds
  - type: rss
    url: https://feeds.reuters.com/reuters/topNews
    name: Reuters Top
    category: world
    
  - type: rss
    url: https://hnrss.org/frontpage
    name: Hacker News
    category: technology
    
  # NewsAPI (requires NEWSAPI_KEY env var)
  - type: newsapi
    query: "artificial intelligence"
    language: en
    category: technology
    
  # Direct site scraping (use responsibly)
  - type: scrape
    url: https://example.com/news
    selector: article.post
    name: Example News
    
  # Twitter/X list (requires API access)
  - type: twitter
    list_id: "1234567890"
    name: Tech Journalists
    
  # Email forwarding
  - type: email
    address: digest-abc123@ingest.newsdigest.dev
    name: Newsletter Inbox

#──────────────────────────────────────────────────────────────────
# EXTRACTION SETTINGS
#──────────────────────────────────────────────────────────────────
extraction:
  # Aggressiveness (conservative, standard, aggressive)
  mode: standard
  
  # Minimum sentence density to keep (0.0 - 1.0)
  min_sentence_density: 0.3
  
  # Keep unnamed sources? (keep, flag, remove)
  unnamed_sources: flag
  
  # Keep speculation? (keep, flag, remove)
  speculation: remove
  
  # Maximum hedge words before removal
  max_hedges_per_sentence: 2
  
  # Emotional word handling (keep, flag, remove)
  emotional_language: remove
  
  # Quote handling
  quotes:
    keep_attributed: true
    keep_unattributed: false
    flag_circular: true

#──────────────────────────────────────────────────────────────────
# DIGEST SETTINGS  
#──────────────────────────────────────────────────────────────────
digest:
  # Lookback period
  period: 24h
  
  # Maximum items (before auto-summarizing)
  max_items: 100
  
  # Topic clustering
  clustering:
    enabled: true
    min_cluster_size: 3
    
  # Cross-source deduplication
  deduplication:
    enabled: true
    similarity_threshold: 0.85
    
  # Novelty filtering
  novelty:
    enabled: true
    min_score: 0.3
    # Compare against rolling window
    window: 7d
    
  # Story threading (connect related items)
  threading:
    enabled: true
    max_thread_age: 72h

#──────────────────────────────────────────────────────────────────
# OUTPUT SETTINGS
#──────────────────────────────────────────────────────────────────
output:
  # Format: markdown, html, json, text, email
  format: markdown
  
  # Include compression statistics
  show_stats: true
  
  # Include source links
  include_links: true
  
  # Include warnings (unnamed sources, etc.)
  show_warnings: true
  
  # File output
  file:
    enabled: true
    path: ~/Documents/news/
    filename_format: "digest-{date}.md"
    
#──────────────────────────────────────────────────────────────────
# EMAIL DELIVERY
#──────────────────────────────────────────────────────────────────
email:
  enabled: false
  to: you@example.com
  from: digest@newsdigest.dev
  subject: "NewsDigest: {date}"
  
  # Cron schedule (server mode only)
  schedule: "0 7 * * *"  # 7 AM daily
  
  # SMTP settings (if self-hosting)
  smtp:
    host: smtp.example.com
    port: 587
    user: ${SMTP_USER}
    pass: ${SMTP_PASS}
    tls: true

#──────────────────────────────────────────────────────────────────
# ALERTS
#──────────────────────────────────────────────────────────────────
alerts:
  # Breaking news threshold
  breaking:
    enabled: true
    min_novelty: 0.9
    min_sources: 3
    notify:
      - type: pushover
        token: ${PUSHOVER_TOKEN}
        user: ${PUSHOVER_USER}
      - type: webhook
        url: https://your-server.com/alert
        
  # Keyword alerts
  keywords:
    - term: "Federal Reserve"
      notify: [pushover, webhook]
    - term: "your-company-name"
      notify: [email]

#──────────────────────────────────────────────────────────────────
# ANALYTICS
#──────────────────────────────────────────────────────────────────
analytics:
  # Track consumption patterns
  enabled: true
  
  # Retention period
  retention: 90d
  
  # Export format
  export_format: json
```

---

## Self-Hosting

### Docker

```bash
# Quick start
docker run -p 8080:8080 \
  -v ~/.newsdigest:/config \
  newsdigest/server:latest

# With persistent data
docker run -p 8080:8080 \
  -v ~/.newsdigest:/config \
  -v newsdigest-data:/data \
  newsdigest/server:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  newsdigest:
    image: newsdigest/server:latest
    ports:
      - "8080:8080"
    volumes:
      - ./config:/config
      - newsdigest-data:/data
    environment:
      - NEWSAPI_KEY=${NEWSAPI_KEY}
      - SMTP_HOST=smtp.example.com
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASS=${SMTP_PASS}
    restart: unless-stopped

volumes:
  newsdigest-data:
```

### Kubernetes

See [k8s/](./k8s/) for Helm charts and manifests.

---

## Privacy

### Local Mode (Default)

- All processing on your machine
- URLs fetched directly by your client
- Nothing sent to NewsDigest servers
- Zero telemetry

### API Mode

- Article URLs sent to our servers
- Content fetched and processed server-side
- Not stored beyond request processing
- Not used for training
- See [Privacy Policy](./PRIVACY.md)

### Self-Hosted

- You control everything
- Your infrastructure, your data
- No external dependencies (except source feeds)

---

## Pricing

### Free Tier
- 10 extractions/day
- 3 RSS sources
- Daily digest (email)
- Basic analytics

### Pro ($10/month)
- Unlimited extractions
- Unlimited sources
- Real-time monitoring
- Advanced analytics
- API access (1,000 calls/month)
- Priority support

### Team ($25/user/month)
- Everything in Pro
- Shared source lists
- Team digest channels
- Slack/Teams integration
- API access (10,000 calls/month)

### Enterprise
- Self-hosted option
- Custom integrations
- SLA
- Dedicated support
- Volume API pricing

---

## Roadmap

### v0.1 (Current)
- [x] Core extraction engine
- [x] CLI tool
- [x] Python library
- [x] RSS ingestion
- [x] Markdown/JSON output

### v0.2 (In Progress)
- [x] REST API with FastAPI
- [x] API authentication (API keys)
- [x] Rate limiting middleware
- [x] Storage layer (cache, database)
- [x] Email delivery integration
- [x] Topic clustering
- [x] End-to-end test suite
- [ ] Browser extension

### v0.3
- [x] Telegram/Slack integrations
- [x] Monitoring utilities (health checks, alerts)
- [ ] Real-time monitoring UI
- [ ] Analytics dashboard

### v0.4
- [x] NewsAPI integration
- [x] Twitter/X integration
- [ ] Podcast transcript support
- [ ] Multi-language (ES, FR, DE)

### Future
- [ ] Video news extraction (transcript analysis)
- [ ] Fact-check integration
- [ ] Source credibility scoring
- [ ] Personalized signal detection

---

## FAQ

**Q: Isn't this just summarization?**

No. Summarization compresses meaning. Extraction removes non-meaning. A summary of an empty article is still empty. Extraction of an empty article returns nothing—which is the correct answer.

**Q: Won't I miss important context?**

Sometimes. The tool optimizes for density, not completeness. For deep understanding of complex topics, read original sources. For staying informed across many topics efficiently, use the digest.

**Q: What about bias detection?**

Not in scope. NewsDigest detects filler, not ideology. A biased article with high information density will pass through with its bias intact. We may add bias flagging in the future, but it's a different problem.

**Q: Can I use this to scrape paywalled sites?**

No. NewsDigest respects robots.txt and won't bypass paywalls. You can analyze content you have legitimate access to.

**Q: My favorite source has low density. Does that mean it's bad?**

Not necessarily. Some publications prioritize narrative and context over density. That's a legitimate editorial choice. Low density just means more words per fact—whether that's "bad" depends on what you want.

**Q: Why is compression so high (95%+)?**

Because modern news really is that padded. This surprises people until they see the side-by-side comparison. The 95% isn't an artifact—it's the actual filler ratio.

**Q: Can I trust the extraction?**

Trust but verify. The tool makes extraction decisions that are usually right but not infallible. For important decisions, check original sources. The tool is for efficiency, not authority.

---

## Development

### Quick Start

```bash
# Clone the repository
git clone https://github.com/kase1111-hash/newsdigest.git
cd newsdigest

# Create and activate virtual environment
make venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install development dependencies
make install-dev

# Download spaCy model
make setup-models

# Run tests
make test

# Run linting
make lint
```

### Project Structure

```
newsdigest/
├── src/newsdigest/     # Main package
│   ├── cli/            # CLI commands
│   ├── core/           # Extraction engine
│   ├── analyzers/      # Semantic analyzers
│   ├── ingestors/      # Input handlers
│   ├── parsers/        # Content parsing
│   ├── formatters/     # Output formatting
│   ├── digest/         # Digest generation
│   ├── api/            # REST API
│   │   ├── routes/     # API endpoints
│   │   ├── middleware.py  # Auth, rate limiting, tracking
│   │   └── utils.py    # Shared utilities
│   ├── storage/        # Storage layer
│   │   ├── cache.py    # Memory and file caching
│   │   ├── database.py # SQLite persistence
│   │   └── analytics.py # Analytics storage
│   ├── integrations/   # External integrations
│   │   ├── email.py    # Email notifications
│   │   ├── newsapi.py  # NewsAPI client
│   │   ├── twitter.py  # Twitter/X integration
│   │   ├── telegram.py # Telegram bot
│   │   └── slack.py    # Slack integration
│   └── utils/          # Utilities
│       └── monitoring.py # Health checks, alerts, metrics
├── tests/              # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── e2e/            # End-to-end tests
├── docs/               # Documentation
└── docker/             # Docker configuration
```

### Common Commands

```bash
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linter (ruff)
make format        # Format code
make type-check    # Run mypy
make check         # Run all checks
make docs-serve    # Serve documentation locally
```

### Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run only end-to-end tests
pytest tests/e2e/

# Run specific E2E test file
pytest tests/e2e/test_middleware.py -v

# Run with coverage report
pytest --cov=newsdigest --cov-report=html
```

#### E2E Test Suite

The end-to-end test suite (`tests/e2e/`) includes:

| Test File | Description |
|-----------|-------------|
| `test_extraction_pipeline.py` | Tests complete extraction flow, compression, and formatters |
| `test_api_endpoints.py` | Tests REST API endpoints (health, extract, compare, digest) |
| `test_storage.py` | Tests cache, database persistence, and analytics storage |
| `test_middleware.py` | Tests API authentication, rate limiting, and request tracking |

### Docker Development

```bash
# Build and start API server
make docker-up

# View logs
make docker-logs

# Stop containers
make docker-down
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run checks (`make check`)
5. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

See [STYLE_GUIDE.md](./docs/STYLE_GUIDE.md) for coding conventions.

---

## Support

- **Documentation**: [docs.newsdigest.dev](https://docs.newsdigest.dev)
- **Issues**: [GitHub Issues](https://github.com/kase1111-hash/newsdigest/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kase1111-hash/newsdigest/discussions)
- **Email**: support@newsdigest.dev
- **Twitter**: [@newsdigest](https://twitter.com/newsdigest)

---

## License

NewsDigest is licensed under the [Polyform Small Business License 1.0.0](./LICENSE.md).

**In short:**
- ✅ Free for individuals, academics, nonprofits, and small organizations (<100 people, <$1M revenue)
- ❌ Large commercial entities need a separate license

See [LICENSE-SUMMARY.md](./LICENSE-SUMMARY.md) for details.

---

## Acknowledgments

NewsDigest is built on the [Lexicon](https://github.com/kase1111-hash/lexicon) framework for computational semantic analysis.

---

*The news isn't broken. The signal-to-noise ratio is.*

*We fix the ratio.*

**Stay informed. Not overwhelmed.**
