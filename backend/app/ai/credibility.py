from typing import List, Dict
import numpy as np

class CredibilityScore:
    def __init__(self, score: float, breakdown: Dict[str, float], confidence: float):
        self.score = score
        self.breakdown = breakdown
        self.confidence = confidence

class CredibilityScorer:
    def __init__(self):
        self.weights = {
            'credibility': 0.25,
            'variance': 0.15,
            'occurrence': 0.15,
            'coverage': 0.10,
            'reach': 0.10,
            'proof_type': 0.15,
            'source_diversity': 0.10
        }

    def score_event(self, content: str, metadata: dict) -> CredibilityScore:
        """
        Calculates a credibility score based on the 7-parameter system.
        """
        scores = {
            'credibility': self._calculate_source_credibility(metadata),
            'variance': self._calculate_perspective_variance(metadata),
            'occurrence': self._calculate_cross_platform_occurrence(metadata),
            'coverage': self._calculate_geographic_coverage(metadata),
            'reach': self._calculate_engagement_velocity(metadata),
            'proof_type': self._validate_proof_types(metadata),
            'source_diversity': self._analyze_source_independence(metadata)
        }
        
        final_score = sum(scores[k] * self.weights[k] for k in scores)
        confidence = self._calculate_confidence_interval(scores)
        
        return CredibilityScore(
            score=final_score,
            breakdown=scores,
            confidence=confidence
        )

    def _calculate_source_credibility(self, metadata: dict) -> float:
        # Base score on verification and domain authority
        score = 0.5
        if metadata.get("verified", False): score += 0.3
        if metadata.get("official_source", False): score += 0.2
        return min(score, 1.0)

    def _calculate_perspective_variance(self, metadata: dict) -> float:
        return metadata.get("perspective_variance", 0.5)

    def _calculate_cross_platform_occurrence(self, metadata: dict) -> float:
        platforms = metadata.get("platforms", ["unknown"])
        return min(len(platforms) / 5.0, 1.0)

    def _calculate_geographic_coverage(self, metadata: dict) -> float:
        countries = metadata.get("geographic_coverage", ["unknown"])
        return min(len(countries) / 10.0, 1.0)

    def _calculate_engagement_velocity(self, metadata: dict) -> float:
        velocity = metadata.get("engagement_velocity", 0.1)
        return min(velocity, 1.0)

    def _validate_proof_types(self, metadata: dict) -> float:
        proof_scores = {
            'text_only': 0.2,
            'image': 0.6,
            'video': 0.8,
            'official_document': 0.9,
            'multiple_corroborating': 1.0
        }
        proof_type = metadata.get("proof_type", "text_only")
        return proof_scores.get(proof_type, 0.2)

    def _analyze_source_independence(self, metadata: dict) -> float:
        return metadata.get("source_independence", 0.5)

    def _calculate_confidence_interval(self, scores: dict) -> float:
        # High variance in sub-scores might indicate lower confidence
        vals = list(scores.values())
        return 1.0 - float(np.std(vals))

credibility_scorer = CredibilityScorer()
