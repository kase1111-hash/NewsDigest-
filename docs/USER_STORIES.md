# User Stories & Acceptance Criteria

**Project:** NewsDigest
**Version:** 0.1.0
**Last Updated:** 2026-01-11

---

## Table of Contents

1. [Epic: Single Article Extraction](#epic-single-article-extraction)
2. [Epic: Daily Digest Generation](#epic-daily-digest-generation)
3. [Epic: Source Management](#epic-source-management)
4. [Epic: Output & Formatting](#epic-output--formatting)
5. [Epic: Real-time Monitoring](#epic-real-time-monitoring)
6. [Epic: Analytics & Insights](#epic-analytics--insights)
7. [Epic: REST API](#epic-rest-api)
8. [Epic: Configuration & Setup](#epic-configuration--setup)

---

## Epic: Single Article Extraction

### US-001: Extract Content from URL

**As a** news reader
**I want to** extract the essential content from a news article URL
**So that** I can quickly understand the key facts without reading filler content

**Acceptance Criteria:**
- [ ] Given a valid news article URL, when I run `newsdigest extract <url>`, then I receive compressed content with only factual information
- [ ] The output includes the article title, source name, and publication date
- [ ] Compression ratio is displayed (e.g., "847 words → 52 words")
- [ ] Emotional activation words are stripped from the output
- [ ] Speculative statements are removed
- [ ] Named sources are preserved and listed
- [ ] Unnamed sources are flagged with ⚠️ warning
- [ ] The command completes within 10 seconds for a typical article
- [ ] Invalid URLs return a clear error message

**Priority:** Critical
**Phase:** 1

---

### US-002: Extract Content from Stdin

**As a** developer
**I want to** pipe article content directly to NewsDigest
**So that** I can integrate it into my existing workflows

**Acceptance Criteria:**
- [ ] Given HTML or text content piped to stdin, when I run `newsdigest extract -`, then the content is processed
- [ ] Works with `curl -s <url> | newsdigest extract -`
- [ ] Handles both HTML and plain text input
- [ ] Returns same output format as URL extraction

**Priority:** High
**Phase:** 1

---

### US-003: Compare Original vs Extracted

**As a** user skeptical of the extraction quality
**I want to** see a side-by-side comparison of original and extracted content
**So that** I can verify what was removed and understand the extraction decisions

**Acceptance Criteria:**
- [ ] Given an article URL, when I run `newsdigest compare <url>`, then I see a two-column comparison
- [ ] Original text shows annotations for removed content (e.g., `[EMOTIONAL]`, `[SPECULATION]`)
- [ ] Extracted text appears in the right column
- [ ] Word counts and density scores shown for both versions
- [ ] Filler percentage is calculated and displayed
- [ ] Output is readable in terminal (respects terminal width)
- [ ] HTML output option available with `--format html`

**Priority:** High
**Phase:** 2

---

### US-004: View Extraction Statistics Only

**As a** researcher analyzing news quality
**I want to** see only the statistics about an article without the extracted content
**So that** I can quickly assess information density across many articles

**Acceptance Criteria:**
- [ ] Given an article URL, when I run `newsdigest stats <url>`, then I see only metadata and statistics
- [ ] Statistics include: original words, compressed words, compression ratio
- [ ] Statistics include: novel claims count, named sources count, unnamed sources count
- [ ] Statistics include: emotional words removed, speculation sentences removed
- [ ] Statistics include: semantic density (before and after)
- [ ] JSON output available with `--format json`
- [ ] Detailed breakdown available with `--detailed` flag

**Priority:** Medium
**Phase:** 1

---

### US-005: Batch Extract Multiple URLs

**As a** power user
**I want to** extract content from multiple URLs at once
**So that** I can efficiently process many articles

**Acceptance Criteria:**
- [ ] Given a file with URLs (one per line), when I run `newsdigest extract --batch urls.txt`, then all URLs are processed
- [ ] Processing happens in parallel for speed
- [ ] Progress indicator shows completion status
- [ ] Failed URLs are reported but don't stop the batch
- [ ] Output can be directed to a directory with `--output-dir`
- [ ] Summary statistics shown at the end

**Priority:** Medium
**Phase:** 2

---

## Epic: Daily Digest Generation

### US-006: Generate Digest from RSS Feeds

**As a** busy professional
**I want to** receive a compressed digest of news from my favorite sources
**So that** I can stay informed in minutes instead of hours

**Acceptance Criteria:**
- [ ] Given configured RSS feeds, when I run `newsdigest digest`, then I receive a consolidated digest
- [ ] Digest covers the configured time period (default: 24h)
- [ ] Articles are deduplicated across sources
- [ ] Articles are clustered by topic
- [ ] Each topic section shows merged summaries from related articles
- [ ] Source attribution is maintained for each item
- [ ] Compression stats shown (e.g., "847 articles → 43 items")
- [ ] Meta-stats show total emotional language removed, speculation stripped, etc.

**Priority:** Critical
**Phase:** 2

---

### US-007: Configure Digest Time Period

**As a** user with varying schedules
**I want to** generate digests for different time periods
**So that** I can catch up on news whether I check daily or weekly

**Acceptance Criteria:**
- [ ] The `--period` flag accepts: 1h, 6h, 12h, 24h, 48h, 7d
- [ ] Only articles published within the period are included
- [ ] Older articles are excluded even if in the feed
- [ ] Period is clearly shown in digest header

**Priority:** High
**Phase:** 2

---

### US-008: Email Digest Delivery

**As a** user who prefers email
**I want to** receive my digest via email
**So that** I can read it in my inbox without running commands

**Acceptance Criteria:**
- [ ] Given SMTP configuration, when I run `newsdigest digest --email me@example.com`, then the digest is emailed
- [ ] Email is properly formatted HTML
- [ ] Subject line includes date
- [ ] Email works with common providers (Gmail, Outlook, etc.)
- [ ] Scheduled delivery supported via cron config
- [ ] Failed delivery attempts are logged with clear error messages

**Priority:** Medium
**Phase:** 3

---

### US-009: Topic Clustering in Digest

**As a** reader with specific interests
**I want to** see digest content organized by topic
**So that** I can quickly navigate to sections I care about

**Acceptance Criteria:**
- [ ] Digest groups articles into topics: World, Politics, Markets, Technology, Science, Sports, Entertainment
- [ ] Each topic has an emoji indicator
- [ ] Topics with no content are omitted
- [ ] Related stories within a topic are merged
- [ ] Topic classification is reasonably accurate (>80% correct)
- [ ] Clustering can be disabled with `--no-cluster`

**Priority:** High
**Phase:** 2

---

### US-010: Cross-Source Deduplication

**As a** user subscribed to multiple sources
**I want to** see each story only once even if multiple sources covered it
**So that** I don't waste time on duplicate content

**Acceptance Criteria:**
- [ ] Stories with >85% similarity are considered duplicates
- [ ] The most complete version is kept
- [ ] All sources are listed for deduplicated stories
- [ ] Deduplication count shown in meta-stats
- [ ] Deduplication can be disabled with `--no-dedup`

**Priority:** High
**Phase:** 2

---

## Epic: Source Management

### US-011: Add RSS Feed Source

**As a** user
**I want to** add RSS feeds to my news sources
**So that** my digest includes content from those publications

**Acceptance Criteria:**
- [ ] Running `newsdigest sources add --rss <url>` adds the feed
- [ ] Feed URL is validated (must be valid RSS/Atom)
- [ ] Optional `--name` flag sets display name
- [ ] Optional `--category` flag sets topic category
- [ ] Source is persisted to config file
- [ ] Confirmation message shows source was added

**Priority:** High
**Phase:** 2

---

### US-012: List Configured Sources

**As a** user
**I want to** see all my configured news sources
**So that** I can review and manage my information diet

**Acceptance Criteria:**
- [ ] Running `newsdigest sources list` shows all sources
- [ ] Output includes: name, type, URL, category, enabled status
- [ ] Sources grouped by type
- [ ] JSON output available with `--format json`

**Priority:** Medium
**Phase:** 2

---

### US-013: Remove Source

**As a** user
**I want to** remove sources I no longer want
**So that** I can curate my news intake

**Acceptance Criteria:**
- [ ] Running `newsdigest sources remove <name>` removes the source
- [ ] Confirmation prompt before removal (unless `--force`)
- [ ] Source is removed from config file
- [ ] Error if source name doesn't exist

**Priority:** Medium
**Phase:** 2

---

### US-014: Test Source Connectivity

**As a** user adding a new source
**I want to** verify the source is accessible and valid
**So that** I know it will work before relying on it

**Acceptance Criteria:**
- [ ] Running `newsdigest sources test --rss <url>` tests the feed
- [ ] Shows feed title and item count if successful
- [ ] Shows sample of recent items
- [ ] Clear error message if feed is invalid or inaccessible
- [ ] Timeout after 30 seconds with appropriate message

**Priority:** Medium
**Phase:** 2

---

### US-015: NewsAPI Integration

**As a** user wanting broader coverage
**I want to** add NewsAPI as a source
**So that** I can access news beyond my RSS subscriptions

**Acceptance Criteria:**
- [ ] Running `newsdigest sources add --newsapi "<query>"` adds NewsAPI source
- [ ] Requires `NEWSAPI_KEY` environment variable
- [ ] Query supports NewsAPI syntax
- [ ] Language filter supported
- [ ] Clear error if API key invalid

**Priority:** Medium
**Phase:** 3

---

## Epic: Output & Formatting

### US-016: Markdown Output

**As a** user who works with Markdown
**I want to** receive output in Markdown format
**So that** I can use it in my notes, blogs, or documentation

**Acceptance Criteria:**
- [ ] Markdown is the default output format
- [ ] Output is valid CommonMark
- [ ] Includes headers, lists, and code blocks where appropriate
- [ ] Statistics rendered as tables
- [ ] Links are properly formatted

**Priority:** High
**Phase:** 1

---

### US-017: JSON Output

**As a** developer
**I want to** receive output in JSON format
**So that** I can programmatically process the results

**Acceptance Criteria:**
- [ ] JSON output available with `--format json`
- [ ] Schema matches API response format
- [ ] All fields properly typed
- [ ] Valid JSON (parseable by standard tools)
- [ ] Pretty-printed by default, compact with `--compact`

**Priority:** High
**Phase:** 1

---

### US-018: HTML Output

**As a** user who wants visual presentation
**I want to** receive output in HTML format
**So that** I can view it in a browser or include in web pages

**Acceptance Criteria:**
- [ ] HTML output available with `--format html`
- [ ] Includes inline CSS for styling
- [ ] Responsive layout
- [ ] Comparison mode renders as two-column table
- [ ] Statistics rendered attractively

**Priority:** Medium
**Phase:** 2

---

### US-019: Save Output to File

**As a** user
**I want to** save extraction results to a file
**So that** I can reference them later

**Acceptance Criteria:**
- [ ] Output file path specified with `--output <path>`
- [ ] Appropriate extension added based on format if not specified
- [ ] Overwrites existing file (or prompts with `--no-clobber`)
- [ ] Creates parent directories if needed
- [ ] Confirmation message shows file path

**Priority:** Medium
**Phase:** 1

---

## Epic: Real-time Monitoring

### US-020: Watch Mode for Continuous Monitoring

**As a** news junkie
**I want to** continuously monitor my sources for new content
**So that** I can be alerted to important news as it happens

**Acceptance Criteria:**
- [ ] Running `newsdigest watch` starts continuous monitoring
- [ ] Polls sources at configured interval (default: 30m)
- [ ] Only processes new items since last check
- [ ] Extracts and displays new items as they're found
- [ ] Graceful shutdown on Ctrl+C
- [ ] Can run as daemon with `--daemon`

**Priority:** Medium
**Phase:** 4

---

### US-021: Breaking News Alerts

**As a** user who cares about timely information
**I want to** receive alerts for high-novelty breaking news
**So that** I can react quickly to important developments

**Acceptance Criteria:**
- [ ] Alerts triggered when novelty score > 0.9 and 3+ sources report
- [ ] Alert methods configurable: webhook, pushover, email
- [ ] Alert includes summary and source links
- [ ] Keyword alerts for specific terms
- [ ] Alert rate limiting to prevent spam

**Priority:** Low
**Phase:** 4

---

### US-022: Output to Directory

**As a** user archiving news
**I want to** save watch mode results to files
**So that** I can build a searchable archive

**Acceptance Criteria:**
- [ ] `--output <dir>` saves each extraction to a file
- [ ] Filename includes timestamp and source
- [ ] Configurable filename format
- [ ] Old files not overwritten

**Priority:** Low
**Phase:** 4

---

## Epic: Analytics & Insights

### US-023: View Consumption Analytics

**As a** user optimizing my information diet
**I want to** see analytics about my news consumption
**So that** I can make informed decisions about my sources

**Acceptance Criteria:**
- [ ] Running `newsdigest analytics` shows consumption stats
- [ ] Shows: articles analyzed, words processed/delivered, compression ratio
- [ ] Shows: time saved estimate
- [ ] Shows: source quality breakdown (density per source)
- [ ] Shows: topic distribution
- [ ] Configurable period: 7d, 30d, 90d, all
- [ ] JSON export available

**Priority:** Low
**Phase:** 4

---

### US-024: Source Quality Comparison

**As a** user evaluating sources
**I want to** see which sources have the highest information density
**So that** I can prioritize high-quality sources

**Acceptance Criteria:**
- [ ] Analytics includes per-source breakdown
- [ ] Shows: articles count, average density, filler percentage
- [ ] Sources sorted by density (highest first)
- [ ] Insight suggests replacing low-density sources

**Priority:** Low
**Phase:** 4

---

## Epic: REST API

### US-025: Extract via API

**As a** developer building integrations
**I want to** call an extraction API endpoint
**So that** I can integrate NewsDigest into my applications

**Acceptance Criteria:**
- [ ] POST `/v1/extract` accepts URL and options
- [ ] Returns JSON with extracted content and statistics
- [ ] Requires API key authentication
- [ ] Rate limited per tier
- [ ] Returns appropriate HTTP status codes
- [ ] Error responses include descriptive messages

**Priority:** Medium
**Phase:** 3

---

### US-026: Generate Digest via API

**As a** developer
**I want to** generate digests via API
**So that** I can automate digest creation for my users

**Acceptance Criteria:**
- [ ] POST `/v1/digest` accepts sources and options
- [ ] Returns JSON or rendered format based on request
- [ ] Supports same options as CLI (period, cluster, dedupe)
- [ ] Long-running requests handled appropriately

**Priority:** Medium
**Phase:** 3

---

### US-027: Register Webhooks

**As a** developer
**I want to** register webhooks for news alerts
**So that** my application receives notifications for relevant news

**Acceptance Criteria:**
- [ ] POST `/v1/webhooks` registers a webhook
- [ ] Configurable triggers: novelty threshold, topics, keywords
- [ ] Webhook receives POST with news data
- [ ] Webhook management: list, delete, test
- [ ] Retry logic for failed deliveries

**Priority:** Low
**Phase:** 4

---

### US-028: Health Check Endpoint

**As a** DevOps engineer
**I want to** check API health status
**So that** I can monitor service availability

**Acceptance Criteria:**
- [ ] GET `/v1/health` returns health status
- [ ] Includes: status, version, uptime
- [ ] Returns 200 when healthy, 503 when degraded
- [ ] No authentication required

**Priority:** Medium
**Phase:** 3

---

## Epic: Configuration & Setup

### US-029: Initial Setup Wizard

**As a** new user
**I want to** easily set up NewsDigest
**So that** I can start using it quickly

**Acceptance Criteria:**
- [ ] Running `newsdigest setup --all` performs full setup
- [ ] Downloads required language models
- [ ] Creates default config file
- [ ] Prompts for optional settings (email, API keys)
- [ ] Validates setup was successful
- [ ] Provides next steps guidance

**Priority:** High
**Phase:** 1

---

### US-030: Configure Extraction Aggressiveness

**As a** user with specific preferences
**I want to** adjust how aggressively content is compressed
**So that** I can balance brevity vs. completeness

**Acceptance Criteria:**
- [ ] Three modes available: conservative, standard, aggressive
- [ ] Conservative: keeps more context and nuance
- [ ] Standard: balanced approach (default)
- [ ] Aggressive: maximum compression
- [ ] Configurable in config file or via `--mode` flag

**Priority:** Medium
**Phase:** 1

---

### US-031: Environment Variable Configuration

**As a** user deploying in different environments
**I want to** configure settings via environment variables
**So that** I can manage configuration without editing files

**Acceptance Criteria:**
- [ ] API keys read from environment: `NEWSAPI_KEY`, `NEWSDIGEST_API_KEY`
- [ ] SMTP credentials from environment: `SMTP_USER`, `SMTP_PASS`
- [ ] Config file path from `NEWSDIGEST_CONFIG`
- [ ] Environment variables override config file values

**Priority:** Medium
**Phase:** 1

---

### US-032: Start Local API Server

**As a** self-hosting user
**I want to** run the API server locally
**So that** I can use API features without external dependencies

**Acceptance Criteria:**
- [ ] Running `newsdigest serve` starts the API server
- [ ] Configurable port and host
- [ ] Configurable number of workers
- [ ] Auto-reload available for development
- [ ] Serves on http://localhost:8080 by default

**Priority:** Medium
**Phase:** 3

---

## Summary by Phase

### Phase 1 (v0.1) - Core Engine
- US-001: Extract Content from URL
- US-002: Extract Content from Stdin
- US-004: View Extraction Statistics Only
- US-016: Markdown Output
- US-017: JSON Output
- US-019: Save Output to File
- US-029: Initial Setup Wizard
- US-030: Configure Extraction Aggressiveness
- US-031: Environment Variable Configuration

### Phase 2 (v0.1.x) - Enhanced Analysis
- US-003: Compare Original vs Extracted
- US-005: Batch Extract Multiple URLs
- US-006: Generate Digest from RSS Feeds
- US-007: Configure Digest Time Period
- US-009: Topic Clustering in Digest
- US-010: Cross-Source Deduplication
- US-011: Add RSS Feed Source
- US-012: List Configured Sources
- US-013: Remove Source
- US-014: Test Source Connectivity
- US-018: HTML Output

### Phase 3 (v0.2) - API & Integrations
- US-008: Email Digest Delivery
- US-015: NewsAPI Integration
- US-025: Extract via API
- US-026: Generate Digest via API
- US-028: Health Check Endpoint
- US-032: Start Local API Server

### Phase 4 (v0.3) - Advanced Features
- US-020: Watch Mode for Continuous Monitoring
- US-021: Breaking News Alerts
- US-022: Output to Directory
- US-023: View Consumption Analytics
- US-024: Source Quality Comparison
- US-027: Register Webhooks

---

## Definition of Done

A user story is considered **Done** when:

1. **Code Complete**: All acceptance criteria implemented
2. **Tests Written**: Unit tests with >80% coverage for new code
3. **Tests Passing**: All existing and new tests pass
4. **Documentation Updated**: README, help text, and API docs reflect changes
5. **Code Reviewed**: Peer review completed (if applicable)
6. **No Regressions**: Existing functionality unaffected
7. **Performance Acceptable**: Meets performance requirements (e.g., <10s for extraction)

---

*End of User Stories*
