"""NLP pipeline orchestration for NewsDigest."""

from typing import Any

from newsdigest.analyzers import (
    BaseAnalyzer,
    ClaimExtractor,
    EmotionalDetector,
    FillerDetector,
    NoveltyScorer,
    QuoteIsolator,
    RepetitionCollapser,
    SourceValidator,
    SpeculationStripper,
)
from newsdigest.core.result import Claim, Sentence


class AnalysisPipeline:
    """Orchestrates the NLP and semantic analysis pipeline.

    The pipeline:
    1. Processes raw text through spaCy for NLP annotations
    2. Converts to Sentence objects
    3. Runs sentences through analyzer chain
    4. Returns analyzed sentences with scores and flags
    """

    def __init__(self, config: dict | None = None) -> None:
        """Initialize the analysis pipeline.

        Args:
            config: Configuration dictionary for pipeline settings.
        """
        self.config = config or {}
        self._nlp: Any = None  # Lazy-loaded spaCy model
        self._analyzers: list[BaseAnalyzer] = []
        self._claim_extractor: ClaimExtractor | None = None

        # Initialize analyzers
        self._init_analyzers()

    @property
    def nlp(self) -> Any:
        """Lazy-load spaCy model."""
        if self._nlp is None:
            try:
                import spacy

                model_name = self.config.get("spacy_model", "en_core_web_sm")
                self._nlp = spacy.load(model_name)
            except ImportError:
                raise ImportError(
                    "spaCy is required. Install with: pip install spacy && "
                    "python -m spacy download en_core_web_sm"
                )
            except OSError:
                raise OSError(
                    f"spaCy model not found. Download with: "
                    f"python -m spacy download {self.config.get('spacy_model', 'en_core_web_sm')}"
                )
        return self._nlp

    def _init_analyzers(self) -> None:
        """Initialize the analyzer chain."""
        extraction_config = self.config.get("extraction", {})

        # Build analyzer configurations
        filler_config = {"enabled": True}
        spec_config = {
            "enabled": True,
            "mode": extraction_config.get("speculation", "remove"),
            "max_hedges_per_sentence": extraction_config.get(
                "max_hedges_per_sentence", 2
            ),
        }
        emotional_config = {
            "enabled": True,
            "mode": extraction_config.get("emotional_language", "remove"),
        }
        source_config = {
            "enabled": True,
            "unnamed_sources": extraction_config.get("unnamed_sources", "flag"),
        }
        repetition_config = {
            "enabled": True,
            "similarity_threshold": self.config.get("similarity_threshold", 0.7),
        }
        novelty_config = {
            "enabled": True,
            "min_novelty_score": self.config.get("min_novelty_score", 0.3),
        }
        quotes_config = extraction_config.get("quotes", {})
        quote_config = {
            "enabled": True,
            "keep_attributed": quotes_config.get("keep_attributed", True),
            "keep_unattributed": quotes_config.get("keep_unattributed", False),
            "flag_circular": quotes_config.get("flag_circular", True),
        }
        claims_config = {"enabled": True, "min_confidence": 0.3}

        # Initialize analyzers in order of processing
        # Order matters: some analyzers depend on scores from others
        self._analyzers = [
            # First pass: source and quote detection (enriches sentences)
            SourceValidator(source_config),
            QuoteIsolator(quote_config),
            # Second pass: content scoring
            SpeculationStripper(spec_config),
            EmotionalDetector(emotional_config),
            FillerDetector(filler_config),
            # Third pass: cross-sentence analysis
            RepetitionCollapser(repetition_config),
            NoveltyScorer(novelty_config),
        ]

        # Claim extractor runs separately after analysis
        self._claim_extractor = ClaimExtractor(claims_config)

    def process(self, text: str) -> list[Sentence]:
        """Process text through NLP pipeline.

        Args:
            text: Raw text content to process.

        Returns:
            List of Sentence objects with NLP annotations.
        """
        if not text or not text.strip():
            return []

        # Process with spaCy
        doc = self.nlp(text)

        sentences = []
        for i, sent in enumerate(doc.sents):
            # Extract tokens
            tokens = [token.text for token in sent]

            # Extract POS tags
            pos_tags = [token.pos_ for token in sent]

            # Extract entities
            entities = [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char - sent.start_char,
                    "end": ent.end_char - sent.start_char,
                }
                for ent in sent.ents
            ]

            # Calculate initial density score based on entity/content ratio
            content_tokens = [t for t in sent if not t.is_stop and not t.is_punct]
            density = len(content_tokens) / len(sent) if len(sent) > 0 else 0

            sentence = Sentence(
                text=sent.text.strip(),
                index=i,
                tokens=tokens,
                pos_tags=pos_tags,
                entities=entities,
                density_score=round(density, 2),
            )
            sentences.append(sentence)

        return sentences

    def analyze(self, sentences: list[Sentence]) -> list[Sentence]:
        """Run sentences through analyzer chain.

        Args:
            sentences: List of Sentence objects from NLP processing.

        Returns:
            Analyzed sentences with scores and flags.
        """
        if not sentences:
            return sentences

        # Run through each analyzer
        for analyzer in self._analyzers:
            if analyzer.enabled:
                sentences = analyzer.analyze(sentences)

        # Extract claims
        if self._claim_extractor and self._claim_extractor.enabled:
            self._claim_extractor.analyze(sentences)

        return sentences

    def process_and_analyze(self, text: str) -> list[Sentence]:
        """Process text and run analysis in one step.

        Args:
            text: Raw text content.

        Returns:
            Fully analyzed sentences.
        """
        sentences = self.process(text)
        return self.analyze(sentences)

    def get_claims(self) -> list[Claim]:
        """Get extracted claims from last analysis.

        Returns:
            List of Claim objects.
        """
        if self._claim_extractor:
            return self._claim_extractor.get_claims()
        return []

    def get_statistics(self, sentences: list[Sentence]) -> dict:
        """Get analysis statistics from sentences.

        Args:
            sentences: Analyzed sentences.

        Returns:
            Dictionary of statistics.
        """
        kept = [s for s in sentences if s.keep]
        removed = [s for s in sentences if not s.keep]

        # Count by removal reason
        removal_counts: dict = {}
        for s in removed:
            reason = s.removal_reason or "unknown"
            removal_counts[reason] = removal_counts.get(reason, 0) + 1

        # Get source validator stats
        source_validator = next(
            (a for a in self._analyzers if isinstance(a, SourceValidator)), None
        )
        named_sources = (
            source_validator.get_unique_named_sources() if source_validator else []
        )
        unnamed_count = (
            source_validator.get_unnamed_source_count() if source_validator else 0
        )

        # Get emotional word count
        emotional_detector = next(
            (a for a in self._analyzers if isinstance(a, EmotionalDetector)), None
        )
        emotional_words = (
            emotional_detector.get_emotional_word_count() if emotional_detector else 0
        )

        # Get repetition stats
        repetition_collapser = next(
            (a for a in self._analyzers if isinstance(a, RepetitionCollapser)), None
        )
        collapsed = (
            repetition_collapser.get_collapsed_count() if repetition_collapser else 0
        )

        return {
            "total_sentences": len(sentences),
            "kept_sentences": len(kept),
            "removed_sentences": len(removed),
            "removal_breakdown": removal_counts,
            "named_sources": named_sources,
            "unnamed_source_references": unnamed_count,
            "emotional_words_removed": emotional_words,
            "repetitions_collapsed": collapsed,
            "claims_extracted": len(self.get_claims()),
        }
