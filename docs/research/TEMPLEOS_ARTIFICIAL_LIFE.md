# TempleOS as Artificial Life Sandbox

## Concept Overview

TempleOS could serve as an isolated, deterministic environment for running artificial life simulations. Its extreme minimalism and lack of networking make it paradoxically ideal for this purpose.

## Why TempleOS for Artificial Life

### Advantages

1. **Complete Isolation**
   - No networking = no external interference
   - Single-address-space = deterministic execution
   - Ring-0 only = full hardware access, no OS overhead

2. **Minimalist Foundation**
   - ~120K lines of code for entire OS
   - JIT-compiled HolyC = fast iteration
   - No bloat, no background processes

3. **Self-Documenting System**
   - DolDoc hypertext format mixes code + graphics + text
   - Changes to code automatically update documentation
   - Perfect for tracking evolutionary lineages

4. **Graphics Built-In**
   - 640x480 16-color = simple but sufficient for visualization
   - Direct framebuffer access
   - No GPU driver complexity

5. **Reflection & Metadata**
   - Attach arbitrary metadata to any class member
   - Full runtime introspection
   - Ideal for tracking organism properties

### Limitations

- **No networking** — Can't communicate with FAITHH directly
- **16-color graphics** — Limited visualization
- **Single-user** — One simulation at a time
- **x86-64 only** — Can't run on ARM/embedded

## Implementation Strategy

### Phase 1: VM Sandbox
Run TempleOS in QEMU/VirtualBox on Gen8:
```bash
qemu-system-x86_64 -m 512 -cdrom TempleOS.ISO -hda templeos.qcow2
```

### Phase 2: Artificial Life Framework in HolyC

```c
// Organism structure with metadata
class Organism {
  I64 id;
  I64 x, y;           // Position
  I64 energy;
  I64 age;
  U8 genome[256];     // Genetic code
  I64 generation;
  
  // Metadata for tracking
  @min=0 @max=1000 I64 fitness;
  @format="%d mutations" I64 mutation_count;
};

// World grid
#define WORLD_W 160
#define WORLD_H 120
Organism *world[WORLD_W][WORLD_H];

// Main loop
U0 Simulate() {
  while (TRUE) {
    // Update all organisms
    for (I64 x=0; x<WORLD_W; x++)
      for (I64 y=0; y<WORLD_H; y++)
        if (world[x][y])
          UpdateOrganism(world[x][y]);
    
    // Render
    DrawWorld();
    Sleep(16); // ~60fps
  }
}
```

### Phase 3: Data Export
Since TempleOS has no networking, export via:
1. **Shared disk image** — Mount QCOW2 from host
2. **Serial port** — QEMU can redirect to file
3. **Screenshot analysis** — OCR the display (hacky but works)

### Phase 4: FAITHH Integration
- Gen8 runs TempleOS VM
- Host script monitors shared disk for state dumps
- State dumps indexed to ChromaDB
- FAITHH can query evolutionary history

## Cellular Automata in TempleOS

TempleOS is well-suited for cellular automata:

```c
// Conway's Game of Life in HolyC
U8 grid[WORLD_W][WORLD_H];
U8 next[WORLD_W][WORLD_H];

U0 GameOfLife() {
  for (I64 x=0; x<WORLD_W; x++) {
    for (I64 y=0; y<WORLD_H; y++) {
      I64 neighbors = CountNeighbors(x, y);
      if (grid[x][y]) {
        next[x][y] = (neighbors == 2 || neighbors == 3);
      } else {
        next[x][y] = (neighbors == 3);
      }
    }
  }
  MemCpy(grid, next, sizeof(grid));
}
```

## Alternative: Hybrid Approach

Run the simulation engine on Gen8 Linux, but use TempleOS concepts:
- **HolyC-inspired DSL** for defining organisms
- **DolDoc-style** self-documenting genomes
- **Deterministic execution** via fixed random seeds
- **Full FAITHH integration** without VM overhead

## Resources

- TempleOS ISO: https://templeos.org/
- Source code: https://github.com/cia-foundation/TempleOS
- HolyC documentation: Built into TempleOS (F1 for help)
- Terry Davis videos: YouTube archives

## Decision Point

**Recommended path**: Start with hybrid approach on Gen8, prototype the artificial life framework in Python, then port core simulation to HolyC if isolation benefits prove valuable.

The TempleOS VM can run alongside as a "sacred sandbox" — a place where evolved organisms can be "released" into a truly isolated environment to see how they behave without any external influence.
