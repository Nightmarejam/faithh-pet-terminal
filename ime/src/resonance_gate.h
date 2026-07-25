#pragma once
#include <string>
#include <vector>

struct ResonanceLevel {
    std::string label;  // "high", "medium", "low", "insufficient"
    float score;        // 0.0 - 1.0
    std::string permitted_output;
    std::string redirect_behavior;
};

struct JournalEntry {
    std::string date;
    std::string content;
    int word_count;
};

class ResonanceGate {
public:
    ResonanceGate();
    ResonanceLevel evaluate(const JournalEntry& entry);
    bool permits_synthesis(const std::vector<JournalEntry>& entries);
    
private:
    float calculate_score(const JournalEntry& entry);
    int minimum_entries_for_synthesis = 10;
    float synthesis_threshold = 0.65f;
};
