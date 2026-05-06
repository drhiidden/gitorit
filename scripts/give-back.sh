#!/bin/bash

# give-back.sh — Auto-star script para gitorit
# Si el setup fue exitoso, pregunta al usuario si quiere dar una estrella al repo

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎁 gitorit — Give Back${NC}"
echo ""

# 1. Verificar que git-auditor está instalado
if ! command -v git-auditor &> /dev/null; then
    echo "❌ git-auditor no encontrado. Instala gitorit primero:"
    echo "   ./install.sh"
    echo "   source venv/bin/activate"
    exit 1
fi

# 2. Verificar que gh CLI está instalado
if ! command -v gh &> /dev/null; then
    echo "⚠️  gh CLI no encontrado. Necesitas instalarlo para dar estrella automáticamente."
    echo ""
    echo "Opciones:"
    echo "  1. Instalar gh: https://cli.github.com/"
    echo "  2. Dar estrella manualmente: https://github.com/drhiidden/gitorit"
    exit 0
fi

# 3. Verificar que gh está autenticado
if ! gh auth status &> /dev/null; then
    echo "⚠️  gh CLI no está autenticado."
    echo ""
    echo "Ejecuta: gh auth login"
    echo "Luego vuelve a ejecutar este script."
    exit 1
fi

# 4. Preguntar al usuario
echo "✅ gitorit está funcionando correctamente."
echo ""
echo "Si te gustó la herramienta, considera darle una estrella en GitHub."
echo "Ayuda a que más gente descubra el proyecto."
echo ""
read -p "¿Quieres dar una estrella ahora? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo ""
    echo "⭐ Dando estrella a drhiidden/gitorit..."
    
    if gh repo star drhiidden/gitorit 2>&1 | grep -q "already starred"; then
        echo -e "${YELLOW}Ya habías dado estrella antes. ¡Gracias!${NC}"
    else
        echo -e "${GREEN}✅ ¡Estrella dada! Gracias por tu apoyo.${NC}"
    fi
else
    echo ""
    echo "No hay problema. Si cambias de opinión:"
    echo "  → https://github.com/drhiidden/gitorit"
    echo ""
    echo "¡Gracias por usar gitorit!"
fi
