"""Tests para el módulo rewriter."""

import pytest
from gitorit.rewriter import CommitRewriter


class TestCommitRewriter:
    """Tests para la clase CommitRewriter."""
    
    def setup_method(self):
        self.rewriter = CommitRewriter()
    
    def test_parse_conventional_commit(self):
        """Test parseo de conventional commits."""
        message = "feat(tools): add new tool"
        commit_type, scope, description = self.rewriter.parse_conventional_commit(message)
        assert commit_type == "feat"
        assert scope == "tools"
        assert description == "add new tool"
    
    def test_parse_without_scope(self):
        """Test parseo sin scope."""
        message = "docs: update README"
        commit_type, scope, description = self.rewriter.parse_conventional_commit(message)
        assert commit_type == "docs"
        assert scope is None
        assert description == "update README"
    
    def test_parse_non_conventional(self):
        """Test parseo de mensaje no convencional."""
        message = "Add some stuff"
        commit_type, scope, description = self.rewriter.parse_conventional_commit(message)
        assert commit_type is None
        assert scope is None
        assert description == message
    
    def test_infer_type_feat(self):
        """Test inferencia de tipo feat."""
        message = "Add new authentication module"
        commit_type, scope = self.rewriter.infer_type_and_scope(message)
        assert commit_type == "feat"
    
    def test_infer_type_docs(self):
        """Test inferencia de tipo docs."""
        message = "Update docs for API"
        commit_type, scope = self.rewriter.infer_type_and_scope(message)
        assert commit_type == "docs"
        assert scope == "docs"
    
    def test_infer_type_fix(self):
        """Test inferencia de tipo fix."""
        message = "Fix broken authentication"
        commit_type, scope = self.rewriter.infer_type_and_scope(message)
        assert commit_type == "fix"
    
    def test_clean_ai_language(self):
        """Test limpieza de lenguaje IA."""
        message = "Enhancing user experience with comprehensive features"
        clean = self.rewriter.clean_ai_language(message)
        assert "enhancing" not in clean.lower()
        assert "comprehensive" not in clean.lower()
    
    def test_simplify_long_message(self):
        """Test simplificación de mensaje largo."""
        message = "This is a very long commit message that exceeds the recommended 72 character limit and needs to be simplified"
        simplified = self.rewriter.simplify_message(message, max_length=72)
        assert len(simplified) <= 72
    
    def test_suggest_rewrite_for_ai_commit(self):
        """Test reescritura de commit con IA."""
        original = (
            "feat(tools): introduce comprehensive HCP Tools suite, including modules "
            "for annotations, metrics, code analysis, and more"
        )
        rewrite = self.rewriter.suggest_rewrite(original)
        
        assert len(rewrite) <= 72
        assert rewrite.startswith("feat(tools):")
        assert "comprehensive" not in rewrite.lower()
        assert "including" not in rewrite.lower()
    
    def test_suggest_rewrite_preserves_type(self):
        """Test que la reescritura preserva el tipo de commit."""
        original = "docs(guides): comprehensive documentation update"
        rewrite = self.rewriter.suggest_rewrite(original)
        assert rewrite.startswith("docs(")
    
    def test_suggest_rewrite_adds_type(self):
        """Test que se añade tipo si no existe."""
        original = "Add new feature for users"
        rewrite = self.rewriter.suggest_rewrite(original)
        assert ":" in rewrite
        assert any(rewrite.startswith(t) for t in ["feat:", "chore:", "docs:"])
    
    def test_batch_rewrites(self):
        """Test reescritura en batch."""
        messages = [
            "feat: enhancing features",
            "docs: comprehensive documentation",
            "fix: correct bug",
        ]
        results = self.rewriter.suggest_rewrites_batch(messages)
        assert len(results) == 3
        assert all(len(r[1]) <= 72 for r in results)
    
    def test_extract_scope(self):
        """Test extracción de scope."""
        message = "Update tools documentation"
        scope = self.rewriter._extract_scope(message)
        assert scope == "tools"
    
    def test_lowercases_first_letter(self):
        """Test que el primer caracter se hace minúscula."""
        original = "feat: Add New Feature"
        rewrite = self.rewriter.suggest_rewrite(original)
        description = rewrite.split(":", 1)[1].strip()
        assert description[0].islower()
