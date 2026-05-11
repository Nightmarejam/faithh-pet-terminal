#!/bin/bash
# Helper script to update parity files
# Usage: ./update_parity.sh [backend|frontend|config] [filename]

PARITY_DIR="parity"
TYPE=$1
FILENAME=$2
DATE=$(date +%Y-%m-%d)

if [ -z "$TYPE" ] || [ -z "$FILENAME" ]; then
    echo "Usage: ./update_parity.sh [backend|frontend|config] [filename]"
    echo ""
    echo "Examples:"
    echo "  ./update_parity.sh backend faithh_professional_backend.py"
    echo "  ./update_parity.sh frontend faithh_pet_v3.html"
    echo "  ./update_parity.sh config config.yaml"
    exit 1
fi

PARITY_FILE="$PARITY_DIR/$TYPE/PARITY_${FILENAME%.*}.md"

if [ ! -f "$PARITY_FILE" ]; then
    echo "⚠️  Parity file doesn't exist: $PARITY_FILE"
    echo "Creating from template..."
    
    # Copy appropriate template
    case $TYPE in
        backend)
            cp parity/templates/PARITY_backend_template.md "$PARITY_FILE"
            ;;
        frontend)
            cp parity/templates/PARITY_frontend_template.md "$PARITY_FILE"
            ;;
        config)
            cp parity/templates/PARITY_config_template.md "$PARITY_FILE"
            ;;
    esac
    
    # Update filename in template
    sed -i "s/\[filename\]/$FILENAME/g" "$PARITY_FILE"
    sed -i "s/\[YYYY-MM-DD\]/$DATE/g" "$PARITY_FILE"
    
    echo "✅ Created new parity file: $PARITY_FILE"
fi

echo "📝 Opening parity file for editing..."
nano "$PARITY_FILE"

echo "✅ Parity file updated!"
