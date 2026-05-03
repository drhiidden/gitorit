# Contribuir a Git Commit Auditor

## Setup de Desarrollo

```bash
# Clonar y setup
git clone <repo-url>
cd git-commit-auditor

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar con dependencias de desarrollo
pip install -e ".[dev]"
```

## Tests

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=src/gitorit --cov-report=html

# Test específico
pytest tests/test_detector.py -v
```

## Linting y Formato

```bash
# Black (formatter)
black src/ tests/

# Ruff (linter)
ruff check src/ tests/

# MyPy (type checking)
mypy src/
```

## Estructura del Código

```
src/gitorit/
├── models.py       # Dataclasses (CommitAnalysis, Epoch, Report)
├── detector.py     # Algoritmo detección AI
├── rewriter.py     # Sugerencias de reescritura
├── analyzer.py     # Core analysis engine
├── timeline.py     # Visualizaciones ASCII
└── cli.py          # CLI interface
```

## Añadir Nuevas Features

### 1. Añadir Nuevo Patrón de IA

Edita `src/gitorit/detector.py`:

```python
AI_PATTERNS = {
    "words": [
        "enhancing",
        "tu_nueva_palabra",  # Añadir aquí
    ],
    # ...
}
```

### 2. Añadir Nuevo Comando CLI

Edita `src/gitorit/cli.py`:

```python
@main.command()
@click.argument("repo_path")
def tu_comando(repo_path: str) -> None:
    """Descripción del comando."""
    # Implementación
    pass
```

### 3. Añadir Nuevo Export Format

1. Crea template en `templates/tu_formato.j2`
2. Añade función `_generate_tu_formato_report()` en `cli.py`
3. Añade opción en `--output` choice

## Roadmap

Ver `CHANGELOG.md` para features planeadas.

## Estilo de Código

- Seguir PEP 8
- Type hints en todas las funciones
- Docstrings en formato Google Style
- Nombres descriptivos (no abreviaciones)
- Máximo 100 caracteres por línea

## Pull Requests

1. Fork el repo
2. Crea branch: `git checkout -b feature/mi-feature`
3. Commit cambios: `git commit -m "feat: add X"`
4. Push: `git push origin feature/mi-feature`
5. Abre PR con descripción clara

## Licencia

MIT License - ver `LICENSE`
