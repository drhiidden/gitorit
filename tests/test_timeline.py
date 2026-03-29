"""Tests para el módulo timeline."""

import pytest
from datetime import date
from gitorit.timeline import TimelineGenerator
from gitorit.models import CommitAnalysis, Epoch


class TestTimelineGenerator:
    """Tests para la clase TimelineGenerator."""
    
    def setup_method(self):
        self.generator = TimelineGenerator(commits_per_block=2)
    
    def create_sample_commit(
        self,
        hash_val: str = "abc1234",
        commit_date: date = None,
        message: str = "test commit",
        ai_score: float = 0.0,
    ) -> CommitAnalysis:
        """Helper para crear commits de prueba."""
        return CommitAnalysis(
            hash=hash_val * 5,
            short_hash=hash_val,
            date=commit_date or date(2026, 3, 29),
            author="test_author",
            message=message,
            files_changed=1,
            insertions=10,
            deletions=5,
            ai_score=ai_score,
        )
    
    def test_ascii_timeline_empty(self):
        """Test timeline con lista vacía."""
        result = self.generator.generate_ascii_timeline([])
        assert "No commits found" in result
    
    def test_ascii_timeline_single_commit(self):
        """Test timeline con un solo commit."""
        commit = self.create_sample_commit()
        result = self.generator.generate_ascii_timeline([commit])
        assert "2026-03-29" in result
        assert "▌" in result or "█" in result or "(1)" in result
    
    def test_ascii_timeline_multiple_commits(self):
        """Test timeline con múltiples commits."""
        commits = [
            self.create_sample_commit("abc1", date(2026, 3, 20)),
            self.create_sample_commit("abc2", date(2026, 3, 20)),
            self.create_sample_commit("abc3", date(2026, 3, 21)),
        ]
        result = self.generator.generate_ascii_timeline(commits, group_by="day")
        assert "2026-03-20" in result
        assert "2026-03-21" in result
    
    def test_timeline_suspicious_flag(self):
        """Test que se marca actividad sospechosa."""
        commits = [self.create_sample_commit(f"abc{i}", date(2026, 3, 20)) for i in range(15)]
        result = self.generator.generate_ascii_timeline(commits)
        assert "🔴" in result
        assert "2026-03-20" in result
    
    def test_risk_heatmap_empty(self):
        """Test heatmap con lista vacía."""
        result = self.generator.generate_risk_heatmap([])
        assert "No epochs found" in result
    
    def test_risk_heatmap_with_epochs(self):
        """Test heatmap con épocas."""
        commits_low = [self.create_sample_commit(f"a{i}", date(2026, 3, i+1), ai_score=20) for i in range(5)]
        commits_high = [self.create_sample_commit(f"b{i}", date(2026, 2, i+1), ai_score=80) for i in range(5)]
        
        epoch1 = Epoch(name="Mar 2026", date_start=date(2026, 3, 1), date_end=date(2026, 3, 5), commits=commits_low)
        epoch2 = Epoch(name="Feb 2026", date_start=date(2026, 2, 1), date_end=date(2026, 2, 5), commits=commits_high)
        
        result = self.generator.generate_risk_heatmap([epoch1, epoch2])
        assert "Mar 2026" in result
        assert "Feb 2026" in result
        assert "🟢" in result or "🔴" in result
    
    def test_velocity_chart_empty(self):
        """Test velocity chart con lista vacía."""
        result = self.generator.generate_velocity_chart([])
        assert "No epochs found" in result
    
    def test_velocity_chart_with_epochs(self):
        """Test velocity chart con épocas."""
        commits = [self.create_sample_commit(f"a{i}", date(2026, 3, i+1)) for i in range(10)]
        epoch = Epoch(name="Mar 2026", date_start=date(2026, 3, 1), date_end=date(2026, 3, 10), commits=commits)
        
        result = self.generator.generate_velocity_chart([epoch])
        assert "Mar 2026" in result
        assert "1.00/day" in result
    
    def test_activity_summary(self):
        """Test resumen de actividad."""
        commits = [
            self.create_sample_commit("a1", date(2026, 3, 20), ai_score=80),
            self.create_sample_commit("a2", date(2026, 3, 21), ai_score=40),
            self.create_sample_commit("a3", date(2026, 3, 22), ai_score=10),
        ]
        
        result = self.generator.generate_activity_summary(commits)
        assert "Total Commits: 3" in result
        assert "AI Detection:" in result
        assert "High risk:" in result or "high risk:" in result.lower()
    
    def test_period_key_day(self):
        """Test generación de clave por día."""
        test_date = date(2026, 3, 29)
        key = self.generator._get_period_key(test_date, "day")
        assert key == "2026-03-29"
    
    def test_period_key_month(self):
        """Test generación de clave por mes."""
        test_date = date(2026, 3, 29)
        key = self.generator._get_period_key(test_date, "month")
        assert key == "2026-03"
