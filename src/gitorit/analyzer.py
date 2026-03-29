"""Analizador principal del historial de git."""

from datetime import date, datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Optional, Tuple

import git
from git import Repo

from gitorit.models import CommitAnalysis, Epoch, AnalysisReport
from gitorit.detector import AIDetector
from gitorit.rewriter import CommitRewriter


class GitAnalyzer:
    """Analiza el historial de un repositorio git."""
    
    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        try:
            self.repo = Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            raise ValueError(f"Not a valid git repository: {repo_path}")
        
        self.detector = AIDetector()
        self.rewriter = CommitRewriter()
    
    def extract_commits(self, branch: str = "HEAD") -> list[CommitAnalysis]:
        """
        Extrae todos los commits del repositorio.
        
        Args:
            branch: Branch o ref a analizar (default: HEAD)
            
        Returns:
            Lista de CommitAnalysis ordenada por fecha (más reciente primero)
        """
        commits = []
        
        for commit in self.repo.iter_commits(branch, max_count=None):
            stats = commit.stats.total
            
            commit_date = datetime.fromtimestamp(commit.committed_date).date()
            
            analysis = CommitAnalysis(
                hash=commit.hexsha,
                short_hash=commit.hexsha[:7],
                date=commit_date,
                author=commit.author.name,
                message=commit.message.strip(),
                files_changed=len(commit.stats.files),
                insertions=stats.get("insertions", 0),
                deletions=stats.get("deletions", 0),
            )
            
            analysis.ai_score = self.detector.calculate_ai_score(analysis.message)
            analysis.ai_patterns = self.detector.detect_patterns(analysis.message)
            
            if analysis.ai_score >= 50:
                analysis.suggested_rewrite = self.rewriter.suggest_rewrite(analysis.message)
            
            commit_type, scope, _ = self.rewriter.parse_conventional_commit(analysis.message)
            analysis.commit_type = commit_type
            analysis.scope = scope
            
            commits.append(analysis)
        
        return commits
    
    def group_by_epochs(self, commits: list[CommitAnalysis], gap_days: int = 7) -> list[Epoch]:
        """
        Agrupa commits en épocas basándose en gaps temporales.
        
        Args:
            commits: Lista de commits ordenada por fecha
            gap_days: Días de inactividad para definir nueva época (default: 7)
            
        Returns:
            Lista de Epoch
        """
        if not commits:
            return []
        
        sorted_commits = sorted(commits, key=lambda c: c.date)
        
        epochs = []
        current_group = [sorted_commits[0]]
        
        for i in range(1, len(sorted_commits)):
            current = sorted_commits[i]
            previous = sorted_commits[i - 1]
            
            days_diff = (current.date - previous.date).days
            
            if days_diff > gap_days:
                epoch = self._create_epoch(current_group)
                epochs.append(epoch)
                current_group = [current]
            else:
                current_group.append(current)
        
        if current_group:
            epoch = self._create_epoch(current_group)
            epochs.append(epoch)
        
        for epoch in epochs:
            for commit in epoch.commits:
                commit.epoch = epoch.name
        
        return epochs
    
    def _create_epoch(self, commits: list[CommitAnalysis]) -> Epoch:
        """Crea un objeto Epoch a partir de un grupo de commits."""
        dates = [c.date for c in commits]
        start_date = min(dates)
        end_date = max(dates)
        
        name = f"{start_date.strftime('%b %Y')}"
        
        if len(commits) >= 20:
            name += " [High Activity]"
        
        epoch = Epoch(
            name=name,
            date_start=start_date,
            date_end=end_date,
            commits=commits,
        )
        
        return epoch
    
    def analyze(self, branch: str = "HEAD") -> AnalysisReport:
        """
        Realiza análisis completo del repositorio.
        
        Args:
            branch: Branch a analizar (default: HEAD)
            
        Returns:
            AnalysisReport con todas las métricas
        """
        commits = self.extract_commits(branch)
        epochs = self.group_by_epochs(commits)
        
        if not commits:
            raise ValueError("No commits found in repository")
        
        dates = [c.date for c in commits]
        date_start = min(dates)
        date_end = max(dates)
        
        authors = defaultdict(int)
        for commit in commits:
            authors[commit.author] += 1
        
        ai_commits = [c for c in commits if c.ai_score > 30]
        high_risk = [c for c in commits if c.risk_level == "high"]
        medium_risk = [c for c in commits if c.risk_level == "medium"]
        clean_commits = [c for c in commits if c.risk_level == "low"]
        
        ai_pattern_counts = defaultdict(int)
        for commit in commits:
            for pattern in commit.ai_patterns:
                ai_pattern_counts[pattern] += 1
        
        top_patterns = dict(sorted(ai_pattern_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        commits_by_date = defaultdict(int)
        for commit in commits:
            commits_by_date[commit.date] += 1
        
        peak_dates = sorted(commits_by_date.items(), key=lambda x: x[1], reverse=True)[:10]
        peak_activity = [
            {
                "date": str(d),
                "commits": count,
                "is_suspicious": count >= 10
            }
            for d, count in peak_dates
        ]
        
        total_days = (date_end - date_start).days + 1
        velocity_avg = len(commits) / total_days if total_days > 0 else 0.0
        
        report = AnalysisReport(
            repo_name=self.repo_path.name,
            repo_path=str(self.repo_path),
            total_commits=len(commits),
            date_start=date_start,
            date_end=date_end,
            authors=dict(authors),
            ai_detection={
                "total": len(ai_commits),
                "percentage": (len(ai_commits) / len(commits)) * 100,
                "high_risk": len(high_risk),
                "medium_risk": len(medium_risk),
                "clean": len(clean_commits),
            },
            epochs=[
                {
                    "name": epoch.name,
                    "date_start": str(epoch.date_start),
                    "date_end": str(epoch.date_end),
                    "total_commits": epoch.total_commits,
                    "velocity": round(epoch.velocity, 2),
                    "risk_percentage": round(epoch.risk_percentage, 2),
                    "ai_detection_rate": round(epoch.ai_detection_rate, 2),
                }
                for epoch in epochs
            ],
            problematic_commits=[
                {
                    "hash": c.short_hash,
                    "date": str(c.date),
                    "author": c.author,
                    "message": c.message,
                    "ai_score": round(c.ai_score, 2),
                    "risk_level": c.risk_level,
                    "patterns": c.ai_patterns,
                    "suggested_rewrite": c.suggested_rewrite,
                }
                for c in sorted(commits, key=lambda x: x.ai_score, reverse=True)
                if c.risk_level in ["high", "medium"]
            ][:50],
            clean_commits=[
                {
                    "hash": c.short_hash,
                    "date": str(c.date),
                    "message": c.message,
                }
                for c in clean_commits[:20]
            ],
            peak_activity=peak_activity,
            velocity_avg=round(velocity_avg, 2),
            top_ai_patterns=top_patterns,
        )
        
        return report
    
    def get_commits_by_risk(
        self, 
        commits: list[CommitAnalysis], 
        risk_level: str = "high"
    ) -> list[CommitAnalysis]:
        """
        Filtra commits por nivel de riesgo.
        
        Args:
            commits: Lista de commits
            risk_level: "high", "medium", "low", o "all"
            
        Returns:
            Lista filtrada de commits
        """
        if risk_level == "all":
            return commits
        return [c for c in commits if c.risk_level == risk_level]
    
    def get_activity_peaks(
        self, 
        commits: list[CommitAnalysis], 
        threshold: int = 10
    ) -> list[Tuple[date, int]]:
        """
        Identifica días con actividad sospechosa (>threshold commits/día).
        
        Args:
            commits: Lista de commits
            threshold: Número mínimo de commits para considerar peak
            
        Returns:
            Lista de tuplas (fecha, count) ordenada por count
        """
        commits_by_date = defaultdict(int)
        for commit in commits:
            commits_by_date[commit.date] += 1
        
        peaks = [(d, count) for d, count in commits_by_date.items() if count >= threshold]
        return sorted(peaks, key=lambda x: x[1], reverse=True)
