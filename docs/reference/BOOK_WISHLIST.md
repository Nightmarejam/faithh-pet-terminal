# Book Wishlist for Knowledge Curation

**Last Updated:** 2026-03-14  
**Purpose:** Curated list of books to acquire for the knowledge base, aligned with project needs

---

## Priority Legend
- 🔴 **Critical** - Directly supports active projects
- 🟡 **High** - Important for skill development
- 🟢 **Medium** - Nice to have, future reference

---

## Programming & System Design

### AI/ML Engineering 🔴
| Title | Author | Why |
|-------|--------|-----|
| Designing Data-Intensive Applications | Martin Kleppmann | FAITHH architecture, ChromaDB optimization |
| Building Machine Learning Pipelines | Hannes Hapke | ML chip synthesis, model deployment |
| Natural Language Processing with Transformers | Lewis Tunstall | LLM integration, embedding strategies |
| Hands-On Large Language Models | Jay Alammar | Practical LLM implementation |
| Machine Learning System Design | Chip Huyen | Production ML systems |

### Python & Backend 🔴
| Title | Author | Why |
|-------|--------|-----|
| Fluent Python (2nd Ed) | Luciano Ramalho | Backend code quality |
| Architecture Patterns with Python | Harry Percival | FAITHH refactoring |
| High Performance Python | Micha Gorelick | Optimization |
| Python Concurrency with asyncio | Matthew Fowler | Async patterns |

### Systems & Infrastructure 🟡
| Title | Author | Why |
|-------|--------|-----|
| The Linux Command Line | William Shotts | Server administration |
| Docker Deep Dive | Nigel Poulton | Container optimization |
| Kubernetes Up & Running | Kelsey Hightower | Future scaling |
| Site Reliability Engineering | Google | Production practices |

---

## Electronics & Audio Engineering

### Circuit Design 🔴
| Title | Author | Why |
|-------|--------|-----|
| The Art of Electronics (3rd Ed) | Horowitz & Hill | Foundational reference |
| Small Signal Audio Design | Douglas Self | Preamp/console design |
| Designing Audio Power Amplifiers | Bob Cordell | Power amp theory |
| Op Amps for Everyone | Ron Mancini (TI) | Practical op-amp circuits |
| Audio Engineering 101 | Tim Dittmar | Fundamentals |

### Acoustics 🟡
| Title | Author | Why |
|-------|--------|-----|
| Master Handbook of Acoustics | F. Alton Everest | Studio design, Floating Garden |
| Sound System Engineering | Don Davis | Live sound, system tuning |
| Recording Studio Design | Philip Newell | Studio construction |

### DIY Audio 🟡
| Title | Author | Why |
|-------|--------|-----|
| Build Your Own Audio Valve Amplifiers | Rainer zur Linde | Tube amp projects |
| The TAB Guide to Vacuum Tube Audio | Jerry Whitaker | Tube theory |
| Analog Synthesizers | Mark Jenkins | Synth DIY |

---

## Permaculture & Sustainable Living

### Core Permaculture 🔴
| Title | Author | Why |
|-------|--------|-----|
| Permaculture: A Designer's Manual | Bill Mollison | The bible, comprehensive |
| Gaia's Garden | Toby Hemenway | Home-scale permaculture |
| The Permaculture Handbook | Peter Bane | Practical implementation |
| Edible Forest Gardens (Vol 1 & 2) | Dave Jacke | Food forest design |

### Soil & Composting 🟡
| Title | Author | Why |
|-------|--------|-----|
| Teaming with Microbes | Jeff Lowenfels | Soil food web |
| The Rodale Book of Composting | Grace Gershuny | Composting systems |
| Building Soils Naturally | Phil Nauta | Organic soil building |

### Water & Earthworks 🟡
| Title | Author | Why |
|-------|--------|-----|
| Water for Every Farm | P.A. Yeomans | Keyline design |
| Rainwater Harvesting | Brad Lancaster | Water catchment |
| The Earth Manual | Malcolm Margolin | Earthwork techniques |

### Animals 🟢
| Title | Author | Why |
|-------|--------|-----|
| Storey's Guide to Raising Chickens | Gail Damerow | Poultry basics |
| The Backyard Goat | Sue Weaver | Goat husbandry |
| Holistic Management | Allan Savory | Grazing systems |
| The Merck Veterinary Manual | Merck | Reference |

---

## Business & Legal

### Small Business 🔴
| Title | Author | Why |
|-------|--------|-----|
| The E-Myth Revisited | Michael Gerber | Business systems |
| Profit First | Mike Michalowicz | Cash flow management |
| Company of One | Paul Jarvis | Sustainable solo business |

### Legal & Tax 🟡
| Title | Author | Why |
|-------|--------|-----|
| LLC Quick Start Guide | ClydeBank Business | LLC management |
| Small Business Taxes Made Easy | Eva Rosenberg | Tax strategy |
| Contracts for Creatives | Various | Contract templates |

---

## Philosophy & Psychology

### Philosophy 🟢
| Title | Author | Why |
|-------|--------|-----|
| Meditations | Marcus Aurelius | Stoic foundations |
| The Tao Te Ching | Lao Tzu | Eastern philosophy |
| Finite and Infinite Games | James Carse | Game theory, life philosophy |
| Gödel, Escher, Bach | Douglas Hofstadter | Consciousness, AI philosophy |

### Psychology & Productivity 🟢
| Title | Author | Why |
|-------|--------|-----|
| Deep Work | Cal Newport | Focus strategies |
| Thinking, Fast and Slow | Daniel Kahneman | Decision making |
| Flow | Mihaly Csikszentmihalyi | Optimal experience |

---

## Architecture & Construction

### Design 🟢
| Title | Author | Why |
|-------|--------|-----|
| A Pattern Language | Christopher Alexander | Design patterns |
| Building Construction Illustrated | Francis Ching | Construction fundamentals |
| The Not So Big House | Sarah Susanka | Efficient design |

### Natural Building 🟡
| Title | Author | Why |
|-------|--------|-----|
| The Hand-Sculpted House | Ianto Evans | Cob construction |
| Earthbag Building | Kaki Hunter | Earthbag techniques |
| The Natural Building Companion | Jacob Deva Racusin | Overview of methods |

---

## Acquisition Strategy

### LibGen Search
```bash
# Search format
https://libgen.is/search.php?req=<title>&column=title

# Download via Torbox
python3 scripts/torbox_downloader.py add "<magnet_link>"
```

### Priority Order
1. **Immediate (This Week):** AI/ML books for FAITHH development
2. **Short-term (This Month):** Electronics for audio projects
3. **Medium-term:** Permaculture for Mexico land planning
4. **Ongoing:** Add as projects evolve

### Storage Location
```
X:/knowledge/
├── programming/
├── electronics/
├── audio-engineering/
├── permaculture/
├── business/
├── philosophy/
└── research/
```

---

## Already Owned (In Learning Portal)

From `X:/learning_portal/Learning Portal/`:
- Java programming books
- Python fundamentals
- C++ (Bjarne Stroustrup)
- Network & Security certification
- Japanese language pack (38GB)
- French language collection
- Life skills collection
- Math references

**Action:** Migrate relevant items to new `X:/knowledge/` structure

---

## Notes

- Prioritize PDF/EPUB over scanned copies when available
- Index high-value books to ChromaDB for FAITHH access
- Keep wishlist updated as projects evolve
- Consider audiobook versions for commute/travel learning
