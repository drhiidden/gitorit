#!/bin/bash
# Demo script para Git Commit Auditor

set -e

REPO_PATH="${1:-.}"
OUTPUT_DIR="./demo-output"

echo "════════════════════════════════════════════════════════════════"
echo "Git Commit Auditor - Demo"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Repo: $REPO_PATH"
echo ""

mkdir -p "$OUTPUT_DIR"

echo "1️⃣  Análisis Completo"
echo "────────────────────────────────────────────────────────────────"
git-auditor analyze "$REPO_PATH" --verbose
echo ""

echo "2️⃣  Timeline Visual"
echo "────────────────────────────────────────────────────────────────"
git-auditor timeline "$REPO_PATH" --show-velocity --show-heatmap
echo ""

echo "3️⃣  Detección de IA"
echo "────────────────────────────────────────────────────────────────"
git-auditor detect-ai "$REPO_PATH" --threshold=0.5 --show-patterns | head -40
echo ""

echo "4️⃣  Sugerencias de Reescritura (Top 5)"
echo "────────────────────────────────────────────────────────────────"
git-auditor suggest-rewrites "$REPO_PATH" --risk-level=high --preview | head -40
echo ""

echo "5️⃣  Exportando Reportes"
echo "────────────────────────────────────────────────────────────────"
git-auditor analyze "$REPO_PATH" --output=markdown --export="$OUTPUT_DIR/audit-report.md"
git-auditor analyze "$REPO_PATH" --output=json --export="$OUTPUT_DIR/audit-report.json"

echo ""
echo "✅ Demo completado!"
echo ""
echo "Reportes generados en $OUTPUT_DIR/"
echo "  • audit-report.md"
echo "  • audit-report.json"
echo ""
echo "Para más info: cat README.md"
