"""Simplificación semántica de diffs para agentes de IA."""

import re
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Hunk:
    header: str
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    
    def is_empty(self) -> bool:
        return not self.added and not self.removed

@dataclass
class FileDiff:
    old_path: Optional[str] = None
    new_path: Optional[str] = None
    hunks: List[Hunk] = field(default_factory=list)

def simplify_diff(raw_diff: str) -> str:
    """
    Toma un diff unificado y lo simplifica para consumo de IA.
    Elimina el ruido de contexto y metadatos innecesarios,
    dejando solo los archivos modificados y las líneas exactas que cambiaron.
    """
    if not raw_diff:
        return ""
        
    files: List[FileDiff] = []
    current_file: Optional[FileDiff] = None
    current_hunk: Optional[Hunk] = None
    
    lines = raw_diff.splitlines()
    
    for line in lines:
        if line.startswith("diff --git"):
            if current_file and (current_file.hunks or current_file.old_path or current_file.new_path):
                files.append(current_file)
            current_file = FileDiff()
            current_hunk = None
            continue
            
        if not current_file:
            continue
            
        if line.startswith("--- "):
            path = line[4:].strip()
            current_file.old_path = path if path != "/dev/null" else None
            continue
            
        if line.startswith("+++ "):
            path = line[4:].strip()
            current_file.new_path = path if path != "/dev/null" else None
            continue
            
        if line.startswith("@@ "):
            if current_hunk and not current_hunk.is_empty():
                current_file.hunks.append(current_hunk)
            
            # Extraer solo la parte de los números de línea, ignorando el contexto de la función
            match = re.match(r"(@@ -[0-9,]+ \+[0-9,]+ @@)", line)
            header = match.group(1) if match else line
            current_hunk = Hunk(header=header)
            continue
            
        if not current_hunk:
            continue
            
        if line.startswith("+") and not line.startswith("+++"):
            current_hunk.added.append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            current_hunk.removed.append(line[1:])
            
    if current_hunk and not current_hunk.is_empty():
        current_file.hunks.append(current_hunk)
    if current_file and (current_file.hunks or current_file.old_path or current_file.new_path):
        files.append(current_file)
        
    # Construir la representación simplificada
    output = []
    for f in files:
        # Determinar el nombre del archivo
        name = f.new_path or f.old_path or "unknown"
        # Limpiar prefijos a/ y b/ de git
        if name.startswith("a/") or name.startswith("b/"):
            name = name[2:]
            
        output.append(f"File: {name}")
        
        for h in f.hunks:
            output.append(f"  {h.header}")
            for r in h.removed:
                output.append(f"    - {r}")
            for a in h.added:
                output.append(f"    + {a}")
        output.append("")
        
    return "\n".join(output).strip()

