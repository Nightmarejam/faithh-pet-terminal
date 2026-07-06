// Agent + population seeding — ported to match Python's agent.py / initialize_population.
// The determinism-critical part is again the RNG consumption order per spawn attempt.

use crate::rng::PyRandom;
use crate::world::World;

pub const GENOME_LENGTH: usize = 8;
pub const INITIAL_ENERGY: i32 = 200;
pub const INITIAL_POPULATION: usize = 50;

pub struct Agent {
    pub id: u64,
    pub generation: i32,
    pub x: i32,
    pub y: i32,
    pub genome: [u8; GENOME_LENGTH],
    pub energy: i32,
    pub alive: bool,
}

/// EXACT port of Simulation.initialize_population. RNG order per attempt:
/// randbelow(width), randbelow(height), then 8× randbelow(8) for the genome —
/// consumed even when add_agent fails on a collision (Python creates the Agent,
/// which generates the genome, BEFORE checking the cell).
pub fn initialize_population(
    world: &mut World, rng: &mut PyRandom, count: usize, seed_reproduce: bool,
) -> Vec<Agent> {
    let mut agents: Vec<Agent> = Vec::new();
    let mut next_id: u64 = 0;
    let mut spawned = 0usize;
    let mut attempts = 0usize;
    let max_attempts = count * 10;
    while spawned < count && attempts < max_attempts {
        let x = rng.randbelow(world.width as u32) as i32;
        let y = rng.randbelow(world.height as u32) as i32;
        next_id += 1; // Agent.__init__ increments the id counter here
        let mut genome = [0u8; GENOME_LENGTH];
        for g in genome.iter_mut() {
            *g = rng.randbelow(8) as u8; // randint(0,7)
        }
        if seed_reproduce {
            genome[5] = 0x04; // ACT_REPRODUCE
            genome[6] = 0x02; // ACT_CONSUME
        }
        // add_agent: succeeds only if the cell is empty
        let cell = &mut world.grid[y as usize][x as usize];
        if cell.occupant.is_none() {
            cell.occupant = Some(next_id);
            agents.push(Agent {
                id: next_id, generation: 0, x, y, genome,
                energy: INITIAL_ENERGY, alive: true,
            });
            spawned += 1;
        }
        attempts += 1;
    }
    agents
}

/// FNV-1a over agent physical state (x,y,genome,energy,generation) in insertion order.
pub fn population_hash(agents: &[Agent]) -> u64 {
    let mut h: u64 = 0xcbf29ce484222325;
    let mut feed = |v: i32, h: &mut u64| {
        for b in v.to_le_bytes() {
            *h ^= b as u64;
            *h = h.wrapping_mul(0x100000001b3);
        }
    };
    for a in agents {
        feed(a.x, &mut h);
        feed(a.y, &mut h);
        for &g in &a.genome {
            feed(g as i32, &mut h);
        }
        feed(a.energy, &mut h);
        feed(a.generation, &mut h);
    }
    h
}
