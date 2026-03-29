"""Generador de sugerencias de reescritura para commits problemáticos."""

import re
from typing import Optional, Tuple
from gitorit.detector import AI_PATTERNS


CONVENTIONAL_TYPES = {
    "feat": ["add", "implement", "introduce", "create", "new"],
    "docs": ["document", "update doc", "add doc", "readme", "comment"],
    "fix": ["fix", "correct", "resolve", "patch", "repair"],
    "refactor": ["refactor", "restructure", "reorganize", "simplify", "clean"],
    "chore": ["chore", "update", "upgrade", "bump", "maintain"],
    "test": ["test", "spec", "coverage"],
    "style": ["format", "style", "lint"],
    "build": ["build", "dependencies", "deps"],
    "ci": ["ci", "pipeline", "workflow", "github action"],
}


class CommitRewriter:
    """Sugiere reescrituras para commits problemáticos."""
    
    def __init__(self):
        self.ai_patterns = AI_PATTERNS
    
    def parse_conventional_commit(self, message: str) -> Tuple[Optional[str], Optional[str], str]:
        """
        Parsea un mensaje en formato Conventional Commits.
        
        Args:
            message: Mensaje del commit
            
        Returns:
            Tupla (type, scope, descripción)
        """
        match = re.match(r'^(feat|docs|fix|refactor|chore|test|style|build|ci)(\(([^)]+)\))?: (.+)', message)
        if match:
            commit_type = match.group(1)
            scope = match.group(3)
            description = match.group(4)
            return commit_type, scope, description
        return None, None, message
    
    def infer_type_and_scope(self, message: str) -> Tuple[str, Optional[str]]:
        """
        Infiere el tipo y scope de un commit basado en su mensaje.
        
        Args:
            message: Mensaje del commit
            
        Returns:
            Tupla (type, scope)
        """
        message_lower = message.lower()
        
        for commit_type, keywords in CONVENTIONAL_TYPES.items():
            for keyword in keywords:
                if keyword in message_lower:
                    scope = self._extract_scope(message)
                    return commit_type, scope
        
        return "chore", None
    
    def _extract_scope(self, message: str) -> Optional[str]:
        """Extrae el scope de un mensaje (ej: docs, tools, mcp, skills)."""
        scopes = ["docs", "tools", "mcp", "skills", "patterns", "guides", "templates", "tests", "cli"]
        message_lower = message.lower()
        
        for scope in scopes:
            if scope in message_lower:
                return scope
        
        return None
    
    def clean_ai_language(self, message: str) -> str:
        """
        Elimina palabras y frases características de IA.
        
        Args:
            message: Mensaje original
            
        Returns:
            Mensaje limpio
        """
        clean = message
        
        for word in self.ai_patterns["words"]:
            clean = re.sub(rf'\b{word}\b', '', clean, flags=re.IGNORECASE)
        
        for phrase in self.ai_patterns["phrases"]:
            clean = re.sub(re.escape(phrase), '', clean, flags=re.IGNORECASE)
        
        clean = re.sub(r', including .+$', '', clean)
        clean = re.sub(r'; \w+ing [^;]+', '', clean)
        
        clean = re.sub(r'\s+', ' ', clean)
        clean = clean.strip()
        
        return clean
    
    def simplify_message(self, message: str, max_length: int = 72) -> str:
        """
        Simplifica un mensaje largo a una versión concisa.
        
        Args:
            message: Mensaje original
            max_length: Longitud máxima (default 72)
            
        Returns:
            Mensaje simplificado
        """
        clean = self.clean_ai_language(message)
        
        clean = re.sub(r'\([^)]*\bincluding\b[^)]*\)', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\bfor (improved|better|enhanced)\b', '', clean, flags=re.IGNORECASE)
        
        parts = re.split(r'[;,]', clean)
        if parts:
            clean = parts[0].strip()
        
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        if len(clean) > max_length:
            clean = clean[:max_length - 3].strip() + "..."
        
        return clean
    
    def suggest_rewrite(self, message: str, max_length: int = 72) -> str:
        """
        Genera una sugerencia de reescritura para un commit.
        
        Args:
            message: Mensaje original del commit
            max_length: Longitud máxima del mensaje (default 72)
            
        Returns:
            Mensaje reescrito siguiendo Conventional Commits
        """
        commit_type, scope, description = self.parse_conventional_commit(message)
        
        if commit_type is None:
            commit_type, scope = self.infer_type_and_scope(message)
            description = message
        
        simplified = self.simplify_message(description, max_length)
        
        if not simplified:
            simplified = "update changes"
        
        if simplified[0].isupper():
            simplified = simplified[0].lower() + simplified[1:]
        
        if scope:
            rewrite = f"{commit_type}({scope}): {simplified}"
        else:
            rewrite = f"{commit_type}: {simplified}"
        
        if len(rewrite) > max_length:
            available = max_length - len(f"{commit_type}: ") - (len(f"({scope})") if scope else 0)
            simplified = simplified[:available - 3].strip() + "..."
            if scope:
                rewrite = f"{commit_type}({scope}): {simplified}"
            else:
                rewrite = f"{commit_type}: {simplified}"
        
        return rewrite
    
    def suggest_rewrites_batch(self, messages: list[str], max_length: int = 72) -> list[Tuple[str, str]]:
        """
        Genera rewrites para múltiples mensajes.
        
        Args:
            messages: Lista de mensajes de commit
            max_length: Longitud máxima
            
        Returns:
            Lista de tuplas (original, rewrite)
        """
        return [(msg, self.suggest_rewrite(msg, max_length)) for msg in messages]
