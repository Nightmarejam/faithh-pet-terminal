// Agent — full port including per-tick state used by the tick loop.
use crate::rng::PyRandom;
use crate::world::World;

pub const GENOME_LENGTH: usize = 8;
pub const INITIAL_ENERGY: i32 = 200;
pub const INITIAL_POPULATION: usize = 50;
pub const ENERGY_MAX: i32 = 255;
pub const REPRODUCTION_THRESHOLD: i32 = 120;
pub const REPRODUCTION_COST: i32 = 80;
pub const CRITICAL_LOW_ENERGY: i32 = 50;
pub const BURST_THRESHOLD: i32 = 150;
pub const CONSUME_AMOUNT: i32 = 25;
pub const BASELINE_DRAIN: i32 = 1;
// costs from config.py
pub const SENSE_COSTS: [i32; 8] = [0, 0, 0, 0, 0, 0, 0, 0];
pub const PROCESS_COSTS: [i32; 8] = [0, 0, 1, 1, 2, 1, 1, 0];
pub const MEMORY_COSTS: [i32; 8] = [0, 0, 1, 1, 0, 0, 1, 2];
pub const ACT_COSTS: [i32; 8] = [0, 1, 0, 1, 2, 1, 2, 1];
pub const REGULATE_COSTS: [i32; 8] = [0, 0, 1, 1, 1, 0, 1, 2];

pub struct Agent {
    pub id: u64,
    pub generation: i32,
    pub x: i32,
    pub y: i32,
    pub genome: [u8; GENOME_LENGTH],
    pub energy: i32,
    pub alive: bool,
    pub age: i32,
    pub memory: Vec<i32>,
    pub pattern_memory: Vec<(i32, i32)>,
    pub shield_active: bool,
    pub signaling: bool,
    pub toxin_active: bool,
    pub op_usage: Vec<(u8, i32)>, // insertion-ordered (reg_learn iterates it)
    pub reproduction_cooldown: i32,
    pub wave_arrival_times: Vec<i32>, // empty in exp0
}

impl Agent {
    pub fn new(id: u64, x: i32, y: i32, genome: [u8; GENOME_LENGTH]) -> Self {
        Agent {
            id, generation: 0, x, y, genome, energy: INITIAL_ENERGY, alive: true,
            age: 0, memory: Vec::new(), pattern_memory: Vec::new(),
            shield_active: false, signaling: false, toxin_active: false,
            op_usage: Vec::new(), reproduction_cooldown: 0, wave_arrival_times: Vec::new(),
        }
    }
    // genome slot accessors
    pub fn sense_ops(&self) -> (u8, u8) { (self.genome[0], self.genome[1]) }
    pub fn process_ops(&self) -> (u8, u8) { (self.genome[2], self.genome[3]) }
    pub fn memory_op(&self) -> u8 { 0 } // MEMORY_ENABLED=false in config -> MEM_NONE forced
    pub fn act_ops(&self) -> (u8, u8) { (self.genome[5], self.genome[6]) }
    pub fn regulate_op(&self) -> u8 { self.genome[7] }

    pub fn apply_energy_cost(&mut self, cost: i32) {
        self.energy -= cost;
        if self.energy <= 0 { self.energy = 0; self.alive = false; }
    }
    pub fn add_energy(&mut self, amount: i32) {
        self.energy = (self.energy + amount).min(ENERGY_MAX);
    }
    pub fn tick_age(&mut self) { self.age += 1; }
    pub fn reset_tick_state(&mut self) {
        self.shield_active = false; self.signaling = false; self.toxin_active = false;
    }
    pub fn record_op_usage(&mut self, op: u8) {
        for e in self.op_usage.iter_mut() { if e.0 == op { e.1 += 1; return; } }
        self.op_usage.push((op, 1));
    }
}

/// initialize_population — validated bit-for-bit (hash 2c9aa438ca75cf3f).
pub fn initialize_population(
    world: &mut World, rng: &mut PyRandom, count: usize, seed_reproduce: bool,
) -> Vec<Agent> {
    let mut agents: Vec<Agent> = Vec::new();
    let mut next_id: u64 = 0;
    let (mut spawned, mut attempts) = (0usize, 0usize);
    let max_attempts = count * 10;
    while spawned < count && attempts < max_attempts {
        let x = rng.randbelow(world.width as u32) as i32;
        let y = rng.randbelow(world.height as u32) as i32;
        next_id += 1;
        let mut genome = [0u8; GENOME_LENGTH];
        for g in genome.iter_mut() { *g = rng.randbelow(8) as u8; }
        if seed_reproduce { genome[5] = 0x04; genome[6] = 0x02; }
        let cell = &mut world.grid[y as usize][x as usize];
        if cell.occupant.is_none() {
            cell.occupant = Some(next_id);
            agents.push(Agent::new(next_id, x, y, genome));
            spawned += 1;
        }
        attempts += 1;
    }
    agents
}

pub fn population_hash(agents: &[Agent]) -> u64 {
    let mut h: u64 = 0xcbf29ce484222325;
    let mut feed = |v: i32, h: &mut u64| {
        for b in v.to_le_bytes() { *h ^= b as u64; *h = h.wrapping_mul(0x100000001b3); }
    };
    for a in agents {
        feed(a.x, &mut h); feed(a.y, &mut h);
        for &g in &a.genome { feed(g as i32, &mut h); }
        feed(a.energy, &mut h); feed(a.generation, &mut h); feed(a.age, &mut h);
    }
    h
}
