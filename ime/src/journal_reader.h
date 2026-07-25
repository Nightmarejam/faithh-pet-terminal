#pragma once
#include <string>
#include <vector>
#include "resonance_gate.h"

class JournalReader {
public:
    explicit JournalReader(const std::string& journal_dir);
    std::vector<JournalEntry> load_entries();
    
private:
    std::string journal_dir_;
    JournalEntry parse_entry(const std::string& filepath);
    int count_words(const std::string& text);
};
