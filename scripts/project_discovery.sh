#!/bin/bash
# FAITHH Project Discovery Script
# Run this in your /home/jonat/ai-stack directory
# It will create organized reports of all your files

echo "🔍 FAITHH Project Discovery Starting..."
echo "================================================"

# Set output directory
OUTPUT_DIR="./discovery_reports"
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "📁 Output directory: $OUTPUT_DIR"
echo ""

# Function to count files
count_files() {
    find "$1" -type f 2>/dev/null | wc -l
}

# 1. DIRECTORY STRUCTURE
echo "1️⃣  Scanning directory structure..."
tree -L 3 -I '__pycache__|*.pyc|node_modules' > "$OUTPUT_DIR/structure_${TIMESTAMP}.txt" 2>/dev/null || \
    find . -maxdepth 3 -type d | sort > "$OUTPUT_DIR/structure_${TIMESTAMP}.txt"
echo "   ✅ Structure saved to: structure_${TIMESTAMP}.txt"

# 2. PYTHON FILES
echo "2️⃣  Finding Python files..."
find . -name "*.py" -type f -not -path "*/__pycache__/*" -not -path "*/venv/*" -not -path "*/env/*" | \
    while read file; do
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        echo "$size|$file"
    done | sort -t'|' -k2 > "$OUTPUT_DIR/python_files_${TIMESTAMP}.txt"
python_count=$(wc -l < "$OUTPUT_DIR/python_files_${TIMESTAMP}.txt")
echo "   ✅ Found $python_count Python files"

# 3. HTML/WEB FILES
echo "3️⃣  Finding HTML/web files..."
find . \( -name "*.html" -o -name "*.css" -o -name "*.js" \) -type f | \
    while read file; do
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        echo "$size|$file"
    done | sort -t'|' -k2 > "$OUTPUT_DIR/web_files_${TIMESTAMP}.txt"
web_count=$(wc -l < "$OUTPUT_DIR/web_files_${TIMESTAMP}.txt")
echo "   ✅ Found $web_count web files"

# 4. CONFIG FILES
echo "4️⃣  Finding configuration files..."
find . \( -name "*.yaml" -o -name "*.yml" -o -name ".env*" -o -name "*.json" -o -name "*.toml" -o -name "*.ini" -o -name "*.conf" \) -type f -not -path "*/node_modules/*" | \
    sort > "$OUTPUT_DIR/config_files_${TIMESTAMP}.txt"
config_count=$(wc -l < "$OUTPUT_DIR/config_files_${TIMESTAMP}.txt")
echo "   ✅ Found $config_count config files"

# 5. DOCUMENTATION
echo "5️⃣  Finding documentation files..."
find . \( -name "*.md" -o -name "*.txt" -o -name "README*" \) -type f | \
    sort > "$OUTPUT_DIR/docs_${TIMESTAMP}.txt"
doc_count=$(wc -l < "$OUTPUT_DIR/docs_${TIMESTAMP}.txt")
echo "   ✅ Found $doc_count documentation files"

# 6. DOCKER FILES
echo "6️⃣  Finding Docker files..."
find . \( -name "Dockerfile*" -o -name "docker-compose*.yml" -o -name "*.dockerfile" \) -type f | \
    sort > "$OUTPUT_DIR/docker_files_${TIMESTAMP}.txt"
docker_count=$(wc -l < "$OUTPUT_DIR/docker_files_${TIMESTAMP}.txt")
echo "   ✅ Found $docker_count Docker files"

# 7. SHELL SCRIPTS
echo "7️⃣  Finding shell scripts..."
find . \( -name "*.sh" -o -name "*.bash" \) -type f | \
    sort > "$OUTPUT_DIR/shell_scripts_${TIMESTAMP}.txt"
script_count=$(wc -l < "$OUTPUT_DIR/shell_scripts_${TIMESTAMP}.txt")
echo "   ✅ Found $script_count shell scripts"

# 8. IMPORTANT FILES DETAILED INFO
echo "8️⃣  Getting detailed info on key files..."
{
    echo "=== BACKEND FILES ==="
    find . -name "*backend*.py" -o -name "*api*.py" -o -name "*server*.py" 2>/dev/null | while read f; do
        echo ""
        echo "FILE: $f"
        ls -lh "$f"
        head -n 30 "$f" | grep -E "^(import|from|def|class|#|GEMINI|API_KEY)"
    done
    
    echo ""
    echo "=== CONFIGURATION FILES ==="
    for config in .env config.yaml docker-compose.yml; do
        if [ -f "$config" ]; then
            echo ""
            echo "FILE: $config"
            ls -lh "$config"
            head -n 50 "$config" | grep -v "^#" | grep -v "^$"
        fi
    done
    
    echo ""
    echo "=== HTML UI FILES ==="
    find . -name "*.html" 2>/dev/null | while read f; do
        echo ""
        echo "FILE: $f"
        ls -lh "$f"
        head -n 20 "$f"
    done
} > "$OUTPUT_DIR/key_files_detail_${TIMESTAMP}.txt"
echo "   ✅ Detailed info saved"

# 9. HOME DIRECTORY SCAN (outside ai-stack)
echo "9️⃣  Scanning home directory for orphaned folders..."
cd /home/jonat || cd ~
{
    echo "=== HOME DIRECTORY CONTENTS ==="
    ls -lah | grep "^d"
    echo ""
    echo "=== LARGE DIRECTORIES OUTSIDE AI-STACK ==="
    du -sh */ 2>/dev/null | sort -rh | head -20
} > "$OUTPUT_DIR/../discovery_reports/home_directory_${TIMESTAMP}.txt" 2>/dev/null || \
    echo "Could not scan home directory" > "$OUTPUT_DIR/home_directory_${TIMESTAMP}.txt"
echo "   ✅ Home directory scanned"

# 10. GEMINI/API KEY SEARCH
echo "🔑 Searching for Gemini API configuration..."
{
    echo "=== SEARCHING FOR GEMINI API REFERENCES ==="
    echo ""
    echo "In .env files:"
    find . -name ".env*" -type f -exec grep -l -i "gemini\|api_key" {} \; 2>/dev/null
    echo ""
    echo "In config files:"
    find . -name "*.yaml" -o -name "*.yml" -type f -exec grep -l -i "gemini\|api_key" {} \; 2>/dev/null
    echo ""
    echo "In Python files:"
    find . -name "*.py" -type f -exec grep -l -i "gemini" {} \; 2>/dev/null | head -10
} > "$OUTPUT_DIR/gemini_search_${TIMESTAMP}.txt"
echo "   ✅ Gemini search completed"

# 11. CREATE SUMMARY REPORT
echo ""
echo "📊 Creating summary report..."
{
    echo "FAITHH PROJECT DISCOVERY SUMMARY"
    echo "================================="
    echo "Scan Date: $(date)"
    echo "Project Path: $(pwd)"
    echo ""
    echo "FILE COUNTS:"
    echo "------------"
    echo "Python files:      $python_count"
    echo "Web files:         $web_count"
    echo "Config files:      $config_count"
    echo "Documentation:     $doc_count"
    echo "Docker files:      $docker_count"
    echo "Shell scripts:     $script_count"
    echo ""
    echo "DISK USAGE:"
    echo "----------"
    du -sh . 2>/dev/null
    echo ""
    echo "TOP 10 LARGEST FILES:"
    echo "--------------------"
    find . -type f -not -path "*/__pycache__/*" -exec ls -lh {} \; 2>/dev/null | \
        sort -k5 -rh | head -10 | awk '{print $5, $9}'
    echo ""
    echo "ALL REPORTS SAVED TO: $OUTPUT_DIR/"
    echo ""
    echo "FILES GENERATED:"
    ls -1 "$OUTPUT_DIR/" | grep "$TIMESTAMP"
} > "$OUTPUT_DIR/SUMMARY_${TIMESTAMP}.txt"

cat "$OUTPUT_DIR/SUMMARY_${TIMESTAMP}.txt"

echo ""
echo "✅ Discovery complete! All reports saved to: $OUTPUT_DIR/"
echo ""
echo "📤 NEXT STEPS:"
echo "1. Review the SUMMARY_${TIMESTAMP}.txt file"
echo "2. Upload the key_files_detail_${TIMESTAMP}.txt to Claude"
echo "3. Upload the SUMMARY_${TIMESTAMP}.txt to Claude"
echo "4. Check gemini_search_${TIMESTAMP}.txt for API key location"
echo ""
