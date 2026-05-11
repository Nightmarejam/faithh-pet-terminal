#include <iostream>
#include <string>
#include "resonance_gate.h"
#include "journal_reader.h"

int main(int argc, char* argv[]) {
    std::cout << "Inner Monologue Engine v0.1.0" << std::endl;
    std::cout << "Architecture: Resonance Transformer (specced)" << std::endl;
    std::cout << "Status: Scaffold — not yet functional" << std::endl;
    
    // Phase 1: Read journal entries
    std::string journal_dir = "../ml/output/journal/";
    if (argc > 1) journal_dir = argv[1];
    
    JournalReader reader(journal_dir);
    auto entries = reader.load_entries();
    
    std::cout << "Journal entries found: " << entries.size() << std::endl;
    
    // Phase 2: Evaluate resonance level
    ResonanceGate gate;
    for (const auto& entry : entries) {
        auto level = gate.evaluate(entry);
        std::cout << "  " << entry.date << ": resonance=" << level.label 
                  << " (" << level.score << ")" << std::endl;
    }
    
    return 0;
}
