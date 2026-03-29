"""CLI principal para Git Commit Auditor."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from gitorit.analyzer import GitAnalyzer
from gitorit.detector import AIDetector
from gitorit.timeline import TimelineGenerator
from gitorit.rewriter import CommitRewriter
from gitorit.models import AnalysisReport, CommitAnalysis


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Git Commit Auditor - CLI tool para auditar historial de git."""
    pass


@main.command()
@click.argument("repo_path", type=click.Path(exists=True))
@click.option("--output", type=click.Choice(["terminal", "json", "markdown"]), default="terminal", help="Formato de salida")
@click.option("--export", type=click.Path(), help="Exportar a archivo")
@click.option("--verbose", is_flag=True, help="Modo detallado")
@click.option("--branch", default="HEAD", help="Branch a analizar")
def analyze(repo_path: str, output: str, export: Optional[str], verbose: bool, branch: str) -> None:
    """Análisis completo del repositorio."""
    try:
        analyzer = GitAnalyzer(repo_path)
        
        with console.status("[bold green]Analizando repositorio..."):
            report = analyzer.analyze(branch)
        
        if output == "terminal":
            _display_terminal_report(report, verbose)
        elif output == "json":
            json_output = report.model_dump_json(indent=2)
            if export:
                Path(export).write_text(json_output)
                console.print(f"[green]✓[/green] Reporte exportado a: {export}")
            else:
                console.print(json_output)
        elif output == "markdown":
            md_output = _generate_markdown_report(report)
            if export:
                Path(export).write_text(md_output)
                console.print(f"[green]✓[/green] Reporte exportado a: {export}")
            else:
                console.print(md_output)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        sys.exit(1)


@main.command()
@click.argument("repo_path", type=click.Path(exists=True))
@click.option("--threshold", type=float, default=0.5, help="Score mínimo para considerar AI (0.0-1.0)")
@click.option("--show-patterns", is_flag=True, help="Mostrar patrones detectados")
@click.option("--list-all", is_flag=True, help="Listar todos los commits analizados")
@click.option("--branch", default="HEAD", help="Branch a analizar")
def detect_ai(repo_path: str, threshold: float, show_patterns: bool, list_all: bool, branch: str) -> None:
    """Detecta commits con evidencia de IA."""
    try:
        analyzer = GitAnalyzer(repo_path)
        
        with console.status("[bold green]Detectando patrones de IA..."):
            commits = analyzer.extract_commits(branch)
        
        ai_commits = [c for c in commits if c.ai_score / 100.0 >= threshold]
        ai_commits.sort(key=lambda c: c.ai_score, reverse=True)
        
        console.print(Panel.fit(
            f"[bold]Commits analizados:[/bold] {len(commits)}\n"
            f"[bold]Con evidencia de IA:[/bold] {len(ai_commits)} ({len(ai_commits)/len(commits)*100:.1f}%)",
            title="Detección de IA",
            border_style="cyan"
        ))
        
        if list_all or ai_commits:
            table = Table(title=f"Commits con IA (threshold: {threshold})")
            table.add_column("Hash", style="cyan", width=8)
            table.add_column("Fecha", style="dim", width=10)
            table.add_column("Score", justify="right", style="yellow", width=6)
            table.add_column("Risk", width=6)
            table.add_column("Mensaje", style="white", width=60)
            
            display_commits = ai_commits if not list_all else commits
            
            for commit in display_commits[:50]:
                risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[commit.risk_level]
                
                msg_preview = commit.message[:57] + "..." if len(commit.message) > 60 else commit.message
                
                table.add_row(
                    commit.short_hash,
                    str(commit.date),
                    f"{commit.ai_score:.0f}",
                    risk_emoji,
                    msg_preview,
                )
            
            console.print(table)
        
        if show_patterns and ai_commits:
            console.print("\n[bold]Top AI Patterns Detectados:[/bold]")
            pattern_counts = {}
            for commit in ai_commits:
                for pattern in commit.ai_patterns:
                    pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
            for pattern, count in sorted_patterns[:10]:
                console.print(f"  {pattern}: {count}")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        sys.exit(1)


@main.command()
@click.argument("repo_path", type=click.Path(exists=True))
@click.option("--format", type=click.Choice(["ascii", "markdown"]), default="ascii", help="Formato de visualización")
@click.option("--group-by", type=click.Choice(["day", "week", "month"]), default="day", help="Agrupación temporal")
@click.option("--show-velocity", is_flag=True, help="Mostrar velocidad por época")
@click.option("--show-heatmap", is_flag=True, help="Mostrar heatmap de riesgo")
@click.option("--branch", default="HEAD", help="Branch a analizar")
def timeline(repo_path: str, format: str, group_by: str, show_velocity: bool, show_heatmap: bool, branch: str) -> None:
    """Genera timeline visual del historial."""
    try:
        analyzer = GitAnalyzer(repo_path)
        timeline_gen = TimelineGenerator()
        
        with console.status("[bold green]Generando timeline..."):
            commits = analyzer.extract_commits(branch)
            epochs = analyzer.group_by_epochs(commits)
        
        if format == "ascii":
            timeline_output = timeline_gen.generate_ascii_timeline(commits, group_by)
            console.print(timeline_output)
            
            if show_velocity:
                console.print("\n")
                velocity_chart = timeline_gen.generate_velocity_chart(epochs)
                console.print(velocity_chart)
            
            if show_heatmap:
                console.print("\n")
                heatmap = timeline_gen.generate_risk_heatmap(epochs)
                console.print(heatmap)
        
        elif format == "markdown":
            md_output = _generate_markdown_timeline(commits, epochs, timeline_gen)
            console.print(md_output)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        sys.exit(1)


@main.command()
@click.argument("repo_path", type=click.Path(exists=True))
@click.option("--risk-level", type=click.Choice(["high", "medium", "all"]), default="high", help="Nivel de riesgo a incluir")
@click.option("--output", type=click.Choice(["terminal", "script"]), default="terminal", help="Formato de salida")
@click.option("--preview", is_flag=True, help="Mostrar before/after")
@click.option("--export", type=click.Path(), help="Exportar a archivo")
@click.option("--branch", default="HEAD", help="Branch a analizar")
def suggest_rewrites(repo_path: str, risk_level: str, output: str, preview: bool, export: Optional[str], branch: str) -> None:
    """Sugiere reescrituras para commits problemáticos."""
    try:
        analyzer = GitAnalyzer(repo_path)
        
        with console.status("[bold green]Analizando commits..."):
            commits = analyzer.extract_commits(branch)
        
        if risk_level == "all":
            target_commits = [c for c in commits if c.ai_score > 30]
        elif risk_level == "high":
            target_commits = [c for c in commits if c.risk_level == "high"]
        elif risk_level == "medium":
            target_commits = [c for c in commits if c.risk_level == "medium"]
        
        target_commits.sort(key=lambda c: c.ai_score, reverse=True)
        
        if not target_commits:
            console.print("[green]✓[/green] No se encontraron commits problemáticos!")
            return
        
        console.print(f"\n[bold]Commits a reescribir:[/bold] {len(target_commits)}\n")
        
        if output == "terminal":
            for i, commit in enumerate(target_commits[:30], 1):
                risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[commit.risk_level]
                
                console.print(f"{risk_emoji} [cyan]{commit.short_hash}[/cyan] ({commit.date}) [yellow]Score: {commit.ai_score:.0f}[/yellow]")
                
                if preview:
                    console.print(f"❌ {commit.message[:100]}")
                    console.print(f"✅ {commit.suggested_rewrite}")
                else:
                    console.print(f"   {commit.message[:80]}...")
                    console.print(f"   → {commit.suggested_rewrite}")
                
                console.print()
        
        elif output == "script":
            script_lines = [
                "#!/bin/bash",
                "# Git rebase script - Generado por git-auditor",
                "# WARNING: Review antes de ejecutar",
                "",
                "set -e",
                "",
            ]
            
            for commit in reversed(target_commits):
                script_lines.append(f"# Original: {commit.message[:60]}")
                script_lines.append(f"git commit --amend -m '{commit.suggested_rewrite}' {commit.hash}")
                script_lines.append("")
            
            script_content = "\n".join(script_lines)
            
            if export:
                Path(export).write_text(script_content)
                console.print(f"[green]✓[/green] Script exportado a: {export}")
            else:
                console.print(script_content)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        sys.exit(1)


def _display_terminal_report(report: AnalysisReport, verbose: bool) -> None:
    """Muestra reporte formateado en terminal."""
    console.print("\n")
    console.print(Panel.fit(
        f"[bold cyan]{report.repo_name}[/bold cyan]\n"
        f"[dim]{report.repo_path}[/dim]\n"
        f"Commits: {report.total_commits} | Period: {report.date_start} → {report.date_end}",
        title="Git Commit Audit Report",
        border_style="cyan"
    ))
    
    ai_data = report.ai_detection
    console.print("\n[bold]AI Detection:[/bold]")
    console.print(f"  Total: {ai_data['total']}/{report.total_commits} ({ai_data['percentage']:.1f}%)")
    console.print(f"  🔴 High risk: {ai_data['high_risk']} ({ai_data['high_risk']/report.total_commits*100:.1f}%)")
    console.print(f"  🟡 Medium risk: {ai_data['medium_risk']} ({ai_data['medium_risk']/report.total_commits*100:.1f}%)")
    console.print(f"  🟢 Clean: {ai_data['clean']} ({ai_data['clean']/report.total_commits*100:.1f}%)")
    
    if report.peak_activity:
        console.print("\n[bold]Peak Activity:[/bold]")
        for peak in report.peak_activity[:5]:
            flag = "🔴 " if peak["is_suspicious"] else "  "
            console.print(f"  {flag}{peak['date']}: {peak['commits']} commits")
    
    if report.top_ai_patterns:
        console.print("\n[bold]Top AI Patterns:[/bold]")
        for pattern, count in list(report.top_ai_patterns.items())[:10]:
            console.print(f"  {pattern}: {count}")
    
    if verbose and report.problematic_commits:
        console.print("\n[bold]Commits Problemáticos (Top 10):[/bold]")
        table = Table()
        table.add_column("Hash", style="cyan", width=8)
        table.add_column("Score", justify="right", style="yellow", width=6)
        table.add_column("Mensaje", width=70)
        
        for commit in report.problematic_commits[:10]:
            msg_preview = commit["message"][:67] + "..." if len(commit["message"]) > 70 else commit["message"]
            table.add_row(
                commit["hash"],
                f"{commit['ai_score']:.0f}",
                msg_preview,
            )
        
        console.print(table)
    
    console.print(f"\n[dim]Velocity promedio: {report.velocity_avg:.2f} commits/día[/dim]")
    console.print(f"[dim]Analyzed at: {report.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n")


def _generate_markdown_report(report: AnalysisReport) -> str:
    """Genera reporte en formato Markdown."""
    lines = [
        f"# Git Commit Audit Report",
        f"",
        f"**Repository**: {report.repo_name}",
        f"**Path**: {report.repo_path}",
        f"**Analyzed**: {report.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"## Summary",
        f"",
        f"- **Total Commits**: {report.total_commits}",
        f"- **Period**: {report.date_start} → {report.date_end}",
        f"- **Velocity**: {report.velocity_avg:.2f} commits/day",
        f"",
        f"## AI Detection",
        f"",
        f"- **Total**: {report.ai_detection['total']}/{report.total_commits} ({report.ai_detection['percentage']:.1f}%)",
        f"- 🔴 **High Risk**: {report.ai_detection['high_risk']} ({report.ai_detection['high_risk']/report.total_commits*100:.1f}%)",
        f"- 🟡 **Medium Risk**: {report.ai_detection['medium_risk']} ({report.ai_detection['medium_risk']/report.total_commits*100:.1f}%)",
        f"- 🟢 **Clean**: {report.ai_detection['clean']} ({report.ai_detection['clean']/report.total_commits*100:.1f}%)",
        f"",
        f"## Peak Activity",
        f"",
    ]
    
    for peak in report.peak_activity[:10]:
        flag = "🔴" if peak["is_suspicious"] else "  "
        lines.append(f"- {flag} **{peak['date']}**: {peak['commits']} commits")
    
    if report.top_ai_patterns:
        lines.append("")
        lines.append("## Top AI Patterns")
        lines.append("")
        for pattern, count in list(report.top_ai_patterns.items())[:15]:
            lines.append(f"- `{pattern}`: {count}")
    
    if report.problematic_commits:
        lines.append("")
        lines.append("## Commits Problemáticos")
        lines.append("")
        lines.append("| Hash | Score | Risk | Mensaje |")
        lines.append("|------|-------|------|---------|")
        
        for commit in report.problematic_commits[:30]:
            risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[commit["risk_level"]]
            msg = commit["message"][:60].replace("|", "\\|")
            lines.append(f"| `{commit['hash']}` | {commit['ai_score']:.0f} | {risk_emoji} | {msg} |")
    
    if report.epochs:
        lines.append("")
        lines.append("## Épocas Identificadas")
        lines.append("")
        lines.append("| Época | Commits | Velocity | AI Detection |")
        lines.append("|-------|---------|----------|--------------|")
        
        for epoch in report.epochs:
            lines.append(
                f"| {epoch['name']} | {epoch['total_commits']} | "
                f"{epoch['velocity']:.2f}/day | {epoch['ai_detection_rate']:.0f}% |"
            )
    
    return "\n".join(lines)


def _generate_markdown_timeline(commits: list, epochs: list, timeline_gen: TimelineGenerator) -> str:
    """Genera timeline en formato Markdown."""
    lines = [
        "# Git Timeline",
        "",
        "```",
        timeline_gen.generate_ascii_timeline(commits, "day"),
        "```",
        "",
        "## Velocity by Epoch",
        "",
        "```",
        timeline_gen.generate_velocity_chart(epochs),
        "```",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
