#include "journal_reader.h"
#include <filesystem>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <iostream>
#include <iterator>

namespace fs = std::filesystem;

JournalReader::JournalReader(const std::string& journal_dir) 
    : journal_dir_(journal_dir) {}

std::vector<JournalEntry> JournalReader::load_entries() {
    std::vector<JournalEntry> entries;
    
    if (!fs::exists(journal_dir_)) {
        std::cerr << "Journal directory not found: " << journal_dir_ << std::endl;
        return entries;
    }
    
    for (const auto& file : fs::directory_iterator(journal_dir_)) {
        if (file.path().extension() == ".md" && 
            file.path().filename().string().find("synthesis") == std::string::npos) {
            entries.push_back(parse_entry(file.path().string()));
        }
    }
    
    std::sort(entries.begin(), entries.end(), 
              [](const JournalEntry& a, const JournalEntry& b) {
                  return a.date < b.date;
              });
    
    return entries;
}

JournalEntry JournalReader::parse_entry(const std::string& filepath) {
    JournalEntry entry;
    
    // Extract date from filename (YYYY-MM-DD.md)
    fs::path p(filepath);
    entry.date = p.stem().string();
    
    std::ifstream file(filepath);
    std::stringstream buffer;
    buffer << file.rdbuf();
    entry.content = buffer.str();
    entry.word_count = count_words(entry.content);
    
    return entry;
}

int JournalReader::count_words(const std::string& text) {
    std::istringstream iss(text);
    return std::distance(std::istream_iterator<std::string>(iss),
                         std::istream_iterator<std::string>());
}
