#include <iostream>
#include <cassert>
#include "../src/resonance_gate.h"

void test_resonance_levels() {
    ResonanceGate gate;
    
    // Test high resonance
    JournalEntry high_entry;
    high_entry.date = "2026-02-25";
    high_entry.content = std::string(600, 'x');  // 600 words
    high_entry.word_count = 600;
    
    auto high_level = gate.evaluate(high_entry);
    assert(high_level.label == "high");
    assert(high_level.permitted_output == "synthesis");
    std::cout << "✅ High resonance test passed" << std::endl;
    
    // Test low resonance
    JournalEntry low_entry;
    low_entry.date = "2026-02-26";
    low_entry.content = std::string(200, 'x');  // 200 words for low resonance
    low_entry.word_count = 200;
    
    auto low_level = gate.evaluate(low_entry);
    assert(low_level.label == "low");
    assert(low_level.permitted_output == "gap identification");
    std::cout << "✅ Low resonance test passed" << std::endl;
    
    // Test synthesis permission
    std::vector<JournalEntry> entries;
    for (int i = 0; i < 15; ++i) {
        entries.push_back(high_entry);  // All high resonance
    }
    
    assert(gate.permits_synthesis(entries) == true);
    std::cout << "✅ Synthesis permission test passed" << std::endl;
    
    // Test insufficient entries
    std::vector<JournalEntry> few_entries;
    for (int i = 0; i < 5; ++i) {
        few_entries.push_back(high_entry);
    }
    
    assert(gate.permits_synthesis(few_entries) == false);
    std::cout << "✅ Insufficient entries test passed" << std::endl;
}

int main() {
    std::cout << "Running Resonance Gate Tests..." << std::endl;
    test_resonance_levels();
    std::cout << "All tests passed! ✅" << std::endl;
    return 0;
}
