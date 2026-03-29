"""Generador de timelines visuales y heatmaps."""

from datetime import date, timedelta
from collections import defaultdict
from typing import Literal

from gitorit.models import CommitAnalysis, Epoch


class TimelineGenerator:
    """Genera visualizaciones ASCII del historial."""
    
    def __init__(self, commits_per_block: int = 2):
        self.commits_per_block = commits_per_block
    
    def generate_ascii_timeline(
        self,
        commits: list[CommitAnalysis],
        group_by: Literal["day", "week", "month"] = "day",
    ) -> str:
        """
        Genera timeline ASCII del historial.
        
        Args:
            commits: Lista de commits ordenada
            group_by: Agrupación temporal
            
        Returns:
            String con timeline ASCII
        """
        if not commits:
            return "No commits found."
        
        sorted_commits = sorted(commits, key=lambda c: c.date)
        
        commits_by_period = defaultdict(list)
        for commit in sorted_commits:
            period_key = self._get_period_key(commit.date, group_by)
            commits_by_period[period_key].append(commit)
        
        lines = []
        lines.append("Timeline")
        lines.append("=" * 80)
        lines.append("")
        
        for period in sorted(commits_by_period.keys()):
            period_commits = commits_by_period[period]
            count = len(period_commits)
            
            blocks = "█" * (count // self.commits_per_block)
            if count % self.commits_per_block > 0:
                blocks += "▌"
            
            is_suspicious = count >= 10
            flag = " 🔴" if is_suspicious else ""
            
            high_ai = sum(1 for c in period_commits if c.risk_level == "high")
            ai_flag = f" [AI: {high_ai}]" if high_ai > 0 else ""
            
            line = f"{period} {blocks} ({count}){ai_flag}{flag}"
            lines.append(line)
            
            if is_suspicious or high_ai > 5:
                features = self._extract_features(period_commits[:3])
                if features:
                    lines.append(f"           {features}")
        
        lines.append("")
        lines.append(f"Legend: █ = {self.commits_per_block} commits | 🔴 = Suspicious (≥10/period)")
        
        return "\n".join(lines)
    
    def generate_risk_heatmap(self, epochs: list[Epoch]) -> str:
        """
        Genera heatmap de riesgo por época.
        
        Args:
            epochs: Lista de épocas
            
        Returns:
            String con heatmap ASCII
        """
        if not epochs:
            return "No epochs found."
        
        lines = []
        lines.append("Risk Heatmap by Epoch")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"{'Period':<15} {'LOW':>6} {'MEDIUM':>8} {'HIGH':>6}  Visual")
        lines.append("-" * 80)
        
        for epoch in epochs:
            low_count = sum(1 for c in epoch.commits if c.risk_level == "low")
            medium_count = sum(1 for c in epoch.commits if c.risk_level == "medium")
            high_count = sum(1 for c in epoch.commits if c.risk_level == "high")
            
            total = len(epoch.commits)
            low_pct = (low_count / total * 100) if total > 0 else 0
            medium_pct = (medium_count / total * 100) if total > 0 else 0
            high_pct = (high_count / total * 100) if total > 0 else 0
            
            bars = "█" * int(high_pct / 5)
            emoji = "🔴" if high_pct > 50 else "🟡" if high_pct > 30 else "🟢"
            
            period_label = epoch.name[:14]
            line = f"{period_label:<15} {low_pct:>5.0f}% {medium_pct:>7.0f}% {high_pct:>5.0f}%  {bars} {emoji}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def generate_velocity_chart(self, epochs: list[Epoch]) -> str:
        """
        Genera gráfico de velocity por época.
        
        Args:
            epochs: Lista de épocas
            
        Returns:
            String con gráfico ASCII
        """
        if not epochs:
            return "No epochs found."
        
        lines = []
        lines.append("Velocity (Commits/Day) by Epoch")
        lines.append("=" * 80)
        lines.append("")
        
        max_velocity = max(epoch.velocity for epoch in epochs) if epochs else 0
        
        for epoch in epochs:
            velocity = epoch.velocity
            bar_length = int((velocity / max_velocity) * 40) if max_velocity > 0 else 0
            bar = "█" * bar_length
            
            flag = " 🔴" if velocity > 5 else ""
            
            line = f"{epoch.name:<20} {bar} {velocity:.2f}/day{flag}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _get_period_key(self, commit_date: date, group_by: str) -> str:
        """Convierte una fecha en clave de período."""
        if group_by == "day":
            return commit_date.strftime("%Y-%m-%d")
        elif group_by == "week":
            return f"{commit_date.year}-W{commit_date.isocalendar()[1]:02d}"
        elif group_by == "month":
            return commit_date.strftime("%Y-%m")
        return str(commit_date)
    
    def _extract_features(self, commits: list[CommitAnalysis]) -> str:
        """Extrae features principales de un grupo de commits."""
        features = []
        for commit in commits:
            if commit.scope:
                features.append(commit.scope)
        
        if features:
            unique_features = list(set(features))[:3]
            return f"Features: {', '.join(unique_features)}"
        return ""
    
    def generate_activity_summary(self, commits: list[CommitAnalysis]) -> str:
        """
        Genera resumen de actividad con métricas clave.
        
        Args:
            commits: Lista de commits
            
        Returns:
            String con resumen formateado
        """
        if not commits:
            return "No commits found."
        
        total = len(commits)
        ai_commits = [c for c in commits if c.ai_score > 30]
        high_risk = [c for c in commits if c.risk_level == "high"]
        medium_risk = [c for c in commits if c.risk_level == "medium"]
        
        dates = [c.date for c in commits]
        date_start = min(dates)
        date_end = max(dates)
        duration = (date_end - date_start).days + 1
        
        lines = []
        lines.append("Activity Summary")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Total Commits: {total}")
        lines.append(f"Period: {date_start} → {date_end} ({duration} days)")
        lines.append(f"Average Velocity: {total / duration:.2f} commits/day")
        lines.append("")
        lines.append("AI Detection:")
        lines.append(f"  Total: {len(ai_commits)}/{total} ({len(ai_commits)/total*100:.1f}%)")
        lines.append(f"  🔴 High risk: {len(high_risk)} ({len(high_risk)/total*100:.1f}%)")
        lines.append(f"  🟡 Medium risk: {len(medium_risk)} ({len(medium_risk)/total*100:.1f}%)")
        lines.append(f"  🟢 Clean: {total - len(ai_commits)} ({(total - len(ai_commits))/total*100:.1f}%)")
        
        return "\n".join(lines)
