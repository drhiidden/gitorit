"""Detector de patrones de IA en mensajes de commit."""

import re
from typing import Tuple


AI_PATTERNS = {
    "words": [
        "enhancing",
        "comprehensive",
        "showcasing",
        "engagement",
        "detailing",
        "facilitating",
        "usability",
        "clarity",
        "functionality",
        "streamlining",
        "optimizing",
    ],
    "phrases": [
        "improving the",
        "detailing the",
        "highlighting the",
        "enhancing user",
        "showcasing best",
        "facilitating better",
        "ensuring better",
        "providing comprehensive",
    ],
    "structural": [
        r", including \w+(?:,\s*\w+)+,?\s+and \w+",
        r"\w+ing [^;]+;\s*\w+ing [^;]+;\s*\w+ing",
        r"(?:\w+ing\s+){3,}",
    ],
}


class AIDetector:
    """Detecta evidencia de IA en mensajes de commit."""
    
    def __init__(self, ai_patterns: dict[str, list[str]] | None = None):
        self.patterns = ai_patterns or AI_PATTERNS
    
    def calculate_ai_score(self, message: str) -> float:
        """
        Calcula un score de 0-100 indicando probabilidad de IA.
        
        Args:
            message: Mensaje del commit a analizar
            
        Returns:
            Score entre 0 y 100
        """
        score = 0.0
        message_lower = message.lower()
        
        if len(message) > 100:
            score += 20
        if len(message) > 150:
            score += 20
        if len(message) > 200:
            score += 30
        
        for word in self.patterns["words"]:
            count = message_lower.count(word.lower())
            score += count * 10
        
        for phrase in self.patterns["phrases"]:
            if phrase.lower() in message_lower:
                score += 15
        
        for pattern in self.patterns["structural"]:
            if re.search(pattern, message, re.IGNORECASE):
                score += 25
        
        return min(score, 100.0)
    
    def detect_patterns(self, message: str) -> list[str]:
        """
        Detecta qué patrones específicos están presentes en el mensaje.
        
        Args:
            message: Mensaje del commit
            
        Returns:
            Lista de patrones detectados
        """
        detected = []
        message_lower = message.lower()
        
        for word in self.patterns["words"]:
            if word.lower() in message_lower:
                detected.append(word)
        
        for phrase in self.patterns["phrases"]:
            if phrase.lower() in message_lower:
                detected.append(f'"{phrase}"')
        
        for i, pattern in enumerate(self.patterns["structural"]):
            if re.search(pattern, message, re.IGNORECASE):
                detected.append(f"structural_pattern_{i+1}")
        
        return detected
    
    def classify_risk(self, score: float) -> Tuple[str, str]:
        """
        Clasifica el nivel de riesgo basado en el score.
        
        Args:
            score: Score de IA (0-100)
            
        Returns:
            Tupla (nivel, emoji)
        """
        if score >= 61:
            return ("high", "🔴")
        elif score >= 31:
            return ("medium", "🟡")
        else:
            return ("low", "🟢")
    
    def is_ai_generated(self, message: str, threshold: float = 0.5) -> bool:
        """
        Determina si un mensaje fue probablemente generado por IA.
        
        Args:
            message: Mensaje del commit
            threshold: Umbral de detección (0.0-1.0), default 0.5
            
        Returns:
            True si score/100 >= threshold
        """
        score = self.calculate_ai_score(message)
        return (score / 100.0) >= threshold
    
    def analyze_commit_message(self, message: str) -> dict[str, any]:
        """
        Análisis completo de un mensaje de commit.
        
        Args:
            message: Mensaje del commit
            
        Returns:
            Dict con score, riesgo, patrones, y metadata
        """
        score = self.calculate_ai_score(message)
        patterns = self.detect_patterns(message)
        risk_level, emoji = self.classify_risk(score)
        
        return {
            "ai_score": score,
            "risk_level": risk_level,
            "risk_emoji": emoji,
            "ai_patterns": patterns,
            "message_length": len(message),
            "is_too_long": len(message) > 100,
            "has_ai_language": len(patterns) > 0,
        }


def detect_ai_in_message(message: str, threshold: float = 0.5) -> Tuple[float, list[str]]:
    """
    Función helper para detectar IA en un mensaje.
    
    Args:
        message: Mensaje del commit
        threshold: Umbral de detección (default 0.5)
        
    Returns:
        Tupla (score, patrones detectados)
    """
    detector = AIDetector()
    score = detector.calculate_ai_score(message)
    patterns = detector.detect_patterns(message) if score / 100.0 >= threshold else []
    return score, patterns
