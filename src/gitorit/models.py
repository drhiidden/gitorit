"""Modelos de datos para el análisis de commits."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


RiskLevel = Literal["high", "medium", "low"]
CommitType = Literal["feat", "docs", "fix", "refactor", "chore", "test", "style", "build", "ci"]


@dataclass
class CommitAnalysis:
    """Representa un commit analizado con métricas de IA."""
    
    hash: str
    short_hash: str
    date: date
    author: str
    message: str
    files_changed: int
    insertions: int
    deletions: int
    
    ai_score: float = 0.0
    ai_patterns: list[str] = field(default_factory=list)
    suggested_rewrite: Optional[str] = None
    
    commit_type: Optional[str] = None
    scope: Optional[str] = None
    epoch: Optional[str] = None
    
    @property
    def message_length(self) -> int:
        return len(self.message)
    
    @property
    def risk_level(self) -> RiskLevel:
        """Calcula el nivel de riesgo basado en ai_score."""
        if self.ai_score >= 61:
            return "high"
        elif self.ai_score >= 31:
            return "medium"
        else:
            return "low"


@dataclass
class Epoch:
    """Representa una época/período en el historial del repositorio."""
    
    name: str
    date_start: date
    date_end: date
    commits: list[CommitAnalysis] = field(default_factory=list)
    
    @property
    def total_commits(self) -> int:
        return len(self.commits)
    
    @property
    def duration_days(self) -> int:
        return (self.date_end - self.date_start).days + 1
    
    @property
    def velocity(self) -> float:
        """Commits por día."""
        if self.duration_days == 0:
            return 0.0
        return self.total_commits / self.duration_days
    
    @property
    def risk_percentage(self) -> float:
        """Porcentaje de commits de alto riesgo."""
        if not self.commits:
            return 0.0
        high_risk = sum(1 for c in self.commits if c.risk_level == "high")
        return (high_risk / len(self.commits)) * 100
    
    @property
    def ai_detection_rate(self) -> float:
        """Porcentaje de commits con evidencia de IA (score > 30)."""
        if not self.commits:
            return 0.0
        ai_commits = sum(1 for c in self.commits if c.ai_score > 30)
        return (ai_commits / len(self.commits)) * 100
    
    @property
    def main_features(self) -> list[str]:
        """Extrae features principales de los mensajes de commits."""
        features = []
        for commit in self.commits:
            if commit.commit_type == "feat":
                features.append(commit.message[:50])
        return features[:5]


class AnalysisReport(BaseModel):
    """Reporte completo del análisis del repositorio."""
    
    repo_name: str
    repo_path: str
    analyzed_at: datetime = Field(default_factory=datetime.now)
    
    total_commits: int
    date_start: date
    date_end: date
    authors: dict[str, int]
    
    ai_detection: dict[str, int | float] = Field(default_factory=dict)
    
    epochs: list[dict] = Field(default_factory=list)
    problematic_commits: list[dict] = Field(default_factory=list)
    clean_commits: list[dict] = Field(default_factory=list)
    
    peak_activity: list[dict] = Field(default_factory=list)
    velocity_avg: float = 0.0
    
    top_ai_patterns: dict[str, int] = Field(default_factory=dict)
    
    model_config = {"arbitrary_types_allowed": True}


@dataclass
class ComparisonResult:
    """Resultado de comparación entre dos branches o commits."""
    
    base_ref: str
    target_ref: str
    commits_added: list[CommitAnalysis]
    commits_removed: list[CommitAnalysis]
    files_added: list[str]
    files_removed: list[str]
    files_modified: list[str]
