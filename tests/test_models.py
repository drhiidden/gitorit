"""Tests básicos para los modelos de datos."""

import pytest
from datetime import date
from gitorit.models import CommitAnalysis, Epoch, AnalysisReport


class TestCommitAnalysis:
    """Tests para CommitAnalysis."""
    
    def test_commit_creation(self):
        """Test creación básica de commit."""
        commit = CommitAnalysis(
            hash="abc123def456",
            short_hash="abc123d",
            date=date(2026, 3, 29),
            author="test_user",
            message="feat: add feature",
            files_changed=3,
            insertions=50,
            deletions=10,
        )
        assert commit.hash == "abc123def456"
        assert commit.message_length == len("feat: add feature")
        assert commit.risk_level == "low"
    
    def test_risk_level_classification(self):
        """Test clasificación automática de riesgo."""
        high_commit = CommitAnalysis(
            hash="a", short_hash="a", date=date.today(),
            author="test", message="test", files_changed=1,
            insertions=1, deletions=1, ai_score=70
        )
        assert high_commit.risk_level == "high"
        
        medium_commit = CommitAnalysis(
            hash="b", short_hash="b", date=date.today(),
            author="test", message="test", files_changed=1,
            insertions=1, deletions=1, ai_score=45
        )
        assert medium_commit.risk_level == "medium"
        
        low_commit = CommitAnalysis(
            hash="c", short_hash="c", date=date.today(),
            author="test", message="test", files_changed=1,
            insertions=1, deletions=1, ai_score=15
        )
        assert low_commit.risk_level == "low"


class TestEpoch:
    """Tests para Epoch."""
    
    def test_epoch_properties(self):
        """Test propiedades calculadas de época."""
        commits = [
            CommitAnalysis(
                hash=f"hash{i}", short_hash=f"h{i}",
                date=date(2026, 3, i+1), author="test",
                message="test", files_changed=1,
                insertions=1, deletions=1, ai_score=50 if i < 2 else 10
            )
            for i in range(5)
        ]
        
        epoch = Epoch(
            name="Test Epoch",
            date_start=date(2026, 3, 1),
            date_end=date(2026, 3, 5),
            commits=commits,
        )
        
        assert epoch.total_commits == 5
        assert epoch.duration_days == 5
        assert epoch.velocity == 1.0
        assert 0 <= epoch.risk_percentage <= 100
        assert 0 <= epoch.ai_detection_rate <= 100
    
    def test_epoch_empty(self):
        """Test época sin commits."""
        epoch = Epoch(
            name="Empty",
            date_start=date(2026, 3, 1),
            date_end=date(2026, 3, 1),
            commits=[],
        )
        assert epoch.total_commits == 0
        assert epoch.risk_percentage == 0.0
        assert epoch.ai_detection_rate == 0.0


class TestAnalysisReport:
    """Tests para AnalysisReport."""
    
    def test_report_creation(self):
        """Test creación de reporte."""
        report = AnalysisReport(
            repo_name="test-repo",
            repo_path="/tmp/test",
            total_commits=100,
            date_start=date(2026, 1, 1),
            date_end=date(2026, 3, 29),
            authors={"user1": 60, "user2": 40},
            velocity_avg=1.5,
        )
        assert report.repo_name == "test-repo"
        assert report.total_commits == 100
        assert report.velocity_avg == 1.5
    
    def test_report_with_ai_detection(self):
        """Test reporte con detección de IA."""
        report = AnalysisReport(
            repo_name="test",
            repo_path="/tmp/test",
            total_commits=100,
            date_start=date(2026, 1, 1),
            date_end=date(2026, 3, 29),
            authors={},
            ai_detection={
                "total": 37,
                "percentage": 37.0,
                "high_risk": 15,
                "medium_risk": 22,
                "clean": 63,
            },
        )
        assert report.ai_detection["total"] == 37
        assert report.ai_detection["percentage"] == 37.0
