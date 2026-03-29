"""Tests para el módulo detector."""

import pytest
from gitorit.detector import AIDetector, detect_ai_in_message


class TestAIDetector:
    """Tests para la clase AIDetector."""
    
    def setup_method(self):
        self.detector = AIDetector()
    
    def test_clean_commit(self):
        """Test con commit limpio sin IA."""
        message = "feat(skills): add java security patterns"
        score = self.detector.calculate_ai_score(message)
        assert score < 30, f"Expected low score, got {score}"
        assert self.detector.classify_risk(score)[0] == "low"
    
    def test_ai_commit_with_enhancing(self):
        """Test con commit que usa 'enhancing'."""
        message = "feat: enhancing user experience with new features"
        score = self.detector.calculate_ai_score(message)
        assert score >= 10, "Should detect 'enhancing' keyword"
        patterns = self.detector.detect_patterns(message)
        assert "enhancing" in patterns
    
    def test_ai_commit_comprehensive(self):
        """Test con commit que usa 'comprehensive'."""
        message = "docs: add comprehensive documentation for API"
        score = self.detector.calculate_ai_score(message)
        assert score >= 10
        patterns = self.detector.detect_patterns(message)
        assert "comprehensive" in patterns
    
    def test_long_message(self):
        """Test con mensaje largo."""
        message = "a" * 250
        score = self.detector.calculate_ai_score(message)
        assert score >= 70, "Long messages should score high"
    
    def test_high_risk_commit(self):
        """Test con commit de alto riesgo."""
        message = (
            "feat(tools): introduce comprehensive HCP Tools suite, including modules "
            "for annotations, metrics, code analysis, skill generation, and CLI; "
            "implement custom exceptions and auto-fix scripts for code quality issues; "
            "enhance documentation and installation guides for improved user onboarding "
            "and functionality."
        )
        score = self.detector.calculate_ai_score(message)
        assert score >= 61, f"Expected high risk score, got {score}"
        risk, emoji = self.detector.classify_risk(score)
        assert risk == "high"
        assert emoji == "🔴"
    
    def test_structural_patterns(self):
        """Test detección de patrones estructurales."""
        message = "feat: add support for X, including A, B, C, and D"
        score = self.detector.calculate_ai_score(message)
        patterns = self.detector.detect_patterns(message)
        assert any("structural" in p for p in patterns)
    
    def test_is_ai_generated(self):
        """Test método is_ai_generated."""
        clean_message = "fix: correct auth bug"
        ai_message = "feat: enhancing comprehensive user experience"
        
        assert not self.detector.is_ai_generated(clean_message, threshold=0.3)
        assert self.detector.is_ai_generated(ai_message, threshold=0.1)
    
    def test_analyze_commit_message(self):
        """Test análisis completo de mensaje."""
        message = "feat: showcasing new comprehensive features"
        result = self.detector.analyze_commit_message(message)
        
        assert "ai_score" in result
        assert "risk_level" in result
        assert "ai_patterns" in result
        assert result["has_ai_language"] is True
        assert len(result["ai_patterns"]) > 0
    
    def test_detect_ai_helper_function(self):
        """Test función helper detect_ai_in_message."""
        message = "docs: enhancing documentation"
        score, patterns = detect_ai_in_message(message, threshold=0.1)
        assert score > 0
        assert len(patterns) > 0
