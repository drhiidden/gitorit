#!/bin/bash
# Quick Install Script para Git Commit Auditor

set -e

echo "=================================================="
echo "Git Commit Auditor - Instalación Rápida"
echo "=================================================="
echo ""

if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

echo "Activando entorno virtual..."
source venv/bin/activate

echo "Instalando dependencias..."
pip install -e . > /dev/null 2>&1

echo ""
echo "✓ Instalación completada!"
echo ""
echo "Para usar git-auditor:"
echo "  1. Activa el entorno: source venv/bin/activate"
echo "  2. Ejecuta: git-auditor --help"
echo ""
echo "Ejemplo rápido:"
echo "  git-auditor analyze /path/to/repo --verbose"
echo ""
echo "Para más información, lee USAGE.md"
