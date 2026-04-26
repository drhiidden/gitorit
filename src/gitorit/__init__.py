"""Git Commit Auditor - CLI tool para auditar historial de git."""

__version__ = "0.1.0"

from gitorit.diff_simplifier import simplify_diff

__all__ = ["simplify_diff"]
