"""Topic clustering for NewsDigest."""

import re

from newsdigest.core.result import ExtractionResult


class TopicClusterer:
    """Clusters articles by topic.

    Uses keyword-based classification and entity analysis
    to group related articles together.
    """

    # Topic definitions with keywords and emoji
    TOPICS: list[tuple[str, str, set[str]]] = [
        (
            "World",
            "🌍",
            {
                "international",
                "global",
                "foreign",
                "diplomatic",
                "embassy",
                "treaty",
                "united nations",
                "un",
                "nato",
                "eu",
                "european union",
                "summit",
                "war",
                "conflict",
                "refugee",
                "humanitarian",
            },
        ),
        (
            "Politics",
            "🏛️",
            {
                "congress",
                "senate",
                "house",
                "representative",
                "president",
                "administration",
                "white house",
                "democrat",
                "republican",
                "election",
                "vote",
                "ballot",
                "campaign",
                "legislation",
                "bill",
                "law",
                "policy",
                "governor",
                "mayor",
                "political",
            },
        ),
        (
            "Markets",
            "💰",
            {
                "stock",
                "market",
                "dow",
                "nasdaq",
                "s&p",
                "investor",
                "trading",
                "shares",
                "bond",
                "yield",
                "fed",
                "federal reserve",
                "interest rate",
                "inflation",
                "gdp",
                "economy",
                "economic",
                "recession",
                "growth",
                "earnings",
                "revenue",
                "profit",
                "quarterly",
            },
        ),
        (
            "Technology",
            "🔬",
            {
                "tech",
                "technology",
                "ai",
                "artificial intelligence",
                "machine learning",
                "software",
                "app",
                "startup",
                "silicon valley",
                "google",
                "apple",
                "microsoft",
                "amazon",
                "meta",
                "facebook",
                "twitter",
                "social media",
                "cybersecurity",
                "hack",
                "data",
                "privacy",
                "cloud",
                "chip",
                "semiconductor",
            },
        ),
        (
            "Science",
            "🧪",
            {
                "science",
                "scientific",
                "research",
                "study",
                "researchers",
                "scientists",
                "discovery",
                "experiment",
                "lab",
                "laboratory",
                "nasa",
                "space",
                "climate",
                "environment",
                "nature",
                "biology",
                "physics",
                "chemistry",
                "medicine",
                "health",
                "disease",
                "vaccine",
                "treatment",
                "drug",
            },
        ),
        (
            "Sports",
            "⚽",
            {
                "sport",
                "game",
                "match",
                "team",
                "player",
                "coach",
                "championship",
                "league",
                "nfl",
                "nba",
                "mlb",
                "nhl",
                "soccer",
                "football",
                "basketball",
                "baseball",
                "hockey",
                "tennis",
                "golf",
                "olympics",
                "score",
                "win",
                "loss",
                "season",
            },
        ),
        (
            "Entertainment",
            "🎬",
            {
                "movie",
                "film",
                "tv",
                "television",
                "show",
                "series",
                "actor",
                "actress",
                "director",
                "celebrity",
                "star",
                "music",
                "album",
                "song",
                "artist",
                "concert",
                "tour",
                "award",
                "oscar",
                "emmy",
                "grammy",
                "netflix",
                "streaming",
                "box office",
            },
        ),
        (
            "Business",
            "📊",
            {
                "business",
                "company",
                "corporate",
                "ceo",
                "executive",
                "merger",
                "acquisition",
                "deal",
                "ipo",
                "startup",
                "venture",
                "investment",
                "industry",
                "manufacturing",
                "retail",
                "consumer",
                "brand",
                "marketing",
            },
        ),
    ]

    def __init__(self, config: dict | None = None) -> None:
        """Initialize topic clusterer.

        Args:
            config: Configuration dictionary.
        """
        self.config = config or {}
        self.min_cluster_size = self.config.get("min_cluster_size", 1)

    def cluster(
        self, articles: list[ExtractionResult]
    ) -> dict[str, list[ExtractionResult]]:
        """Cluster articles into topics.

        Args:
            articles: List of extraction results.

        Returns:
            Dictionary mapping topic names to articles.
        """
        clusters: dict[str, list[ExtractionResult]] = {}

        for article in articles:
            topic = self._classify_topic(article)
            if topic not in clusters:
                clusters[topic] = []
            clusters[topic].append(article)

        # Filter by minimum cluster size
        return {
            topic: arts
            for topic, arts in clusters.items()
            if len(arts) >= self.min_cluster_size
        }

    def _classify_topic(self, article: ExtractionResult) -> str:
        """Classify article into a topic.

        Args:
            article: Extraction result.

        Returns:
            Topic name.
        """
        # Combine title and text for analysis
        content = f"{article.title or ''} {article.text}".lower()
        words = set(re.findall(r'\b\w+\b', content))

        # Score each topic
        scores: dict[str, int] = {}
        for topic_name, _, keywords in self.TOPICS:
            score = len(words & keywords)
            if score > 0:
                scores[topic_name] = score

        # Return highest scoring topic or "Other"
        if scores:
            return max(scores.keys(), key=lambda k: scores[k])
        return "Other"

    def get_topic_info(self, topic_name: str) -> tuple[str, str]:
        """Get topic name and emoji.

        Args:
            topic_name: Topic name.

        Returns:
            Tuple of (name, emoji).
        """
        for name, emoji, _ in self.TOPICS:
            if name == topic_name:
                return name, emoji
        return topic_name, "📌"

    def get_all_topics(self) -> list[tuple[str, str]]:
        """Get all topic names and emojis.

        Returns:
            List of (name, emoji) tuples.
        """
        return [(name, emoji) for name, emoji, _ in self.TOPICS]
