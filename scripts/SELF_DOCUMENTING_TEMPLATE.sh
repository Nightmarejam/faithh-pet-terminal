#!/bin/bash
# SELF-DOCUMENTING SCRIPT TEMPLATE
# Copy this template for any automation that should update MASTER_ACTION

# ============================================================
# CONFIGURATION
# ============================================================

# Session info (UPDATE THESE!)
SESSION_NUM=X              # Increment for each session
SESSION_DATE=$(date +%Y-%m-%d)
SESSION_DAY="DayName"      # Monday, Tuesday, etc.
WEEK_INFO="1, Day X"       # e.g., "1, Day 2"
FOCUS="What this script does"

# Files
WORK_LOG=".work_log_temp.md"
MASTER_ACTION="MASTER_ACTION_FAITHH.md"

# ============================================================
# SELF-DOCUMENTATION FUNCTIONS
# ============================================================

# Initialize work log
init_log() {
    cat > "$WORK_LOG" << EOF
## Session $SESSION_NUM - $SESSION_DATE - $SESSION_DAY
**Week:** $WEEK_INFO
**Focus:** $FOCUS

**Completed:**
EOF
}

# Log an action (automatically adds to work log)
log_action() {
    echo "- $1" >> "$WORK_LOG"
    echo "✅ $1"
}

# Log a decision
log_decision() {
    echo "$1" >> "$WORK_LOG.decisions"
}

# Log an issue
log_issue() {
    echo "$1" >> "$WORK_LOG.issues"
}

# Finalize and append to MASTER_ACTION
finalize_log() {
    local start_time=$1
    local end_time=$(date +%H:%M:%S)
    
    # Add decisions section
    if [ -f "$WORK_LOG.decisions" ]; then
        echo "" >> "$WORK_LOG"
        echo "**Decisions Made:**" >> "$WORK_LOG"
        cat "$WORK_LOG.decisions" >> "$WORK_LOG"
        rm "$WORK_LOG.decisions"
    fi
    
    # Add issues section
    if [ -f "$WORK_LOG.issues" ]; then
        echo "" >> "$WORK_LOG"
        echo "**Issues Encountered:**" >> "$WORK_LOG"
        cat "$WORK_LOG.issues" >> "$WORK_LOG"
        rm "$WORK_LOG.issues"
    fi
    
    # Add metadata
    cat >> "$WORK_LOG" << EOF

**Status:** ✅ Complete
**Next Session:** [What's next]
**Time Spent:** Started $start_time, Ended $end_time

---

EOF
    
    # Append to MASTER_ACTION
    echo "" >> "$MASTER_ACTION"
    cat "$WORK_LOG" >> "$MASTER_ACTION"
    
    # Clean up
    rm "$WORK_LOG"
    
    echo ""
    echo "✅ MASTER_ACTION automatically updated!"
    echo "   Check: tail -50 $MASTER_ACTION"
    echo ""
}

# ============================================================
# MAIN SCRIPT LOGIC
# ============================================================

main() {
    local start_time=$(date +%H:%M:%S)
    
    # Initialize
    init_log
    
    echo "Starting script..."
    echo ""
    
    # YOUR WORK HERE
    # Use log_action() for each thing you do
    # Use log_decision() for decisions made
    # Use log_issue() for problems encountered
    
    # Example:
    log_action "Did something important"
    log_decision "**Decision:** Chose option A over B because..."
    
    # More work...
    
    # Finalize
    finalize_log "$start_time"
    
    echo "✨ Script complete!"
}

# Run main
main

# ============================================================
# USAGE EXAMPLES
# ============================================================

# Example 1: Simple file move
# log_action "Moved 5 files to backend/"

# Example 2: With count
# files_moved=0
# for file in *.py; do
#     mv "$file" backend/
#     files_moved=$((files_moved + 1))
# done
# log_action "Moved $files_moved Python files to backend/"

# Example 3: Log decision
# log_decision "**Decision:** Keep config.yaml in root (standard location)"

# Example 4: Log issue
# if [ ! -f ".env" ]; then
#     log_issue ".env file missing - created template"
# fi

# ============================================================
# BENEFITS
# ============================================================

# ✅ Scripts document themselves automatically
# ✅ No manual MASTER_ACTION updates needed
# ✅ Perfect continuity across sessions
# ✅ Timestamped actions
# ✅ Decisions and issues tracked
# ✅ Easy to audit what happened

# ============================================================
# PATTERN
# ============================================================

# Every script:
# 1. Does work
# 2. Logs what it did (log_action)
# 3. Logs decisions (log_decision)
# 4. Automatically updates MASTER_ACTION
# 5. You = zero manual documentation!
