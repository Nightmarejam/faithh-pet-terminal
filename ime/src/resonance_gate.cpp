#include "resonance_gate.h"
#include <algorithm>

ResonanceGate::ResonanceGate() {}

ResonanceLevel ResonanceGate::evaluate(const JournalEntry& entry) {
    float score = calculate_score(entry);
    
    ResonanceLevel level;
    level.score = score;
    
    if (score >= 0.75f) {
        level.label = "high";
        level.permitted_output = "synthesis";
        level.redirect_behavior = "none";
    } else if (score >= 0.5f) {
        level.label = "medium";
        level.permitted_output = "structured analysis with uncertainty flags";
        level.redirect_behavior = "flag gaps";
    } else if (score >= 0.25f) {
        level.label = "low";
        level.permitted_output = "gap identification";
        level.redirect_behavior = "refuse premature synthesis";
    } else {
        level.label = "insufficient";
        level.permitted_output = "mode report only";
        level.redirect_behavior = "state what is needed";
    }
    
    return level;
}

bool ResonanceGate::permits_synthesis(const std::vector<JournalEntry>& entries) {
    if ((int)entries.size() < minimum_entries_for_synthesis) return false;
    
    float total_score = 0.0f;
    for (const auto& e : entries) {
        total_score += calculate_score(e);
    }
    float avg = total_score / entries.size();
    return avg >= synthesis_threshold;
}

float ResonanceGate::calculate_score(const JournalEntry& entry) {
    // Stub: score based on content depth
    // Real implementation will use embedding similarity across entries
    float word_score = std::min(1.0f, entry.word_count / 500.0f);
    return word_score;
}
