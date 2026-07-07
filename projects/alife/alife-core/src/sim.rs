// Simulation — the tick loop, execute_genome, reproduction, mutation.
// Base sim (experiment 0, no predator waves). Ported to match Python Simulation.tick().
use crate::rng::PyRandom;
use crate::world::World;
use crate::agent::*;
use crate::ops;

const BYTE_SWAP_RATE: f64 = 0.001;
const SLOT_MUTATION_RATES: [f64; 8] = [0.001, 0.001, 0.010, 0.010, 0.005, 0.001, 0.001, 0.005];

pub struct Simulation {
    pub world: World,
    pub agents: Vec<Agent>,
    pub rng: PyRandom,
    pub next_id: u64,
    pub total_ticks: u64,
    pub total_reproductions: u64,
    pub total_deaths: u64,
    // UCF experiment knobs (None = base sim, keeps the validated tick unchanged)
    pub floor_energy: Option<i32>,   // guaranteed minimum energy (UCF); rescues from death
    pub shock_interval: Option<u64>, // relocate energy sources every N ticks (fitness shift)
    pub floor_rescues: u64,          // how many times the floor prevented a death
}

impl Simulation {
    pub fn new(seed: u32) -> Self {
        let mut rng = PyRandom::seed(seed);
        let world = World::new(&mut rng);
        Simulation { world, agents: Vec::new(), rng, next_id: 0,
                     total_ticks: 0, total_reproductions: 0, total_deaths: 0,
                     floor_energy: None, shock_interval: None, floor_rescues: 0 }
    }

    /// Distinct-genome count — the diversity metric (the "reserve" the floor preserves).
    pub fn genome_diversity(&self) -> usize {
        use std::collections::HashSet;
        self.agents.iter().map(|a| a.genome).collect::<HashSet<_>>().len()
    }

    pub fn initialize_population(&mut self, count: usize, seed_reproduce: bool) {
        let (mut spawned, mut attempts) = (0usize, 0usize);
        let max_attempts = count * 10;
        while spawned < count && attempts < max_attempts {
            let x = self.rng.randbelow(self.world.width as u32) as i32;
            let y = self.rng.randbelow(self.world.height as u32) as i32;
            self.next_id += 1;
            let mut genome = [0u8; GENOME_LENGTH];
            for g in genome.iter_mut() { *g = self.rng.randbelow(8) as u8; }
            if seed_reproduce { genome[5] = 0x04; genome[6] = 0x02; }
            let cell = &mut self.world.grid[y as usize][x as usize];
            if cell.occupant.is_none() {
                cell.occupant = Some(self.next_id);
                self.agents.push(Agent::new(self.next_id, x, y, genome));
                spawned += 1;
            }
            attempts += 1;
        }
    }

    pub fn tick(&mut self) {
        self.world.tick += 1;
        self.total_ticks += 1;
        self.world.regenerate_energy();
        // SHOCK: relocate energy sources + famine every shock_interval (fitness landscape shift)
        if let Some(iv) = self.shock_interval {
            if self.world.tick % iv == 0 { self.world.apply_shock(&mut self.rng); }
        }

        let floor = self.floor_energy;
        let n = self.agents.len();
        let mut order: Vec<usize> = (0..n).collect();
        self.rng.shuffle(&mut order);

        let mut repro_requests: Vec<usize> = Vec::new();
        let mut deaths = 0u64;
        let mut rescues = 0u64;
        {
            let world = &mut self.world;
            let agents = &mut self.agents;
            for &idx in &order {
                if !agents[idx].alive { continue; }
                if agents[idx].reproduction_cooldown > 0 { agents[idx].reproduction_cooldown -= 1; }
                agents[idx].reset_tick_state();
                agents[idx].apply_energy_cost(BASELINE_DRAIN);
                // FLOOR: rescue from death to guaranteed minimum (UCF)
                if !agents[idx].alive {
                    if let Some(f) = floor { agents[idx].alive = true; agents[idx].energy = f; rescues += 1; }
                    else { deaths += 1; continue; }
                }
                let passive = world.energy_at(agents[idx].x, agents[idx].y).min(5);
                agents[idx].add_energy(passive);
                world.reduce_energy(agents[idx].x, agents[idx].y, passive);
                let requested = execute_genome(&mut agents[idx], world);
                if !agents[idx].alive {
                    if let Some(f) = floor { agents[idx].alive = true; agents[idx].energy = f; rescues += 1; }
                    else { deaths += 1; continue; }
                }
                if requested { repro_requests.push(idx); }
                agents[idx].tick_age();
            }
        }
        self.total_deaths += deaths;
        self.floor_rescues += rescues;

        self.process_reproductions(&repro_requests);
        self.cleanup_dead();
    }

    fn process_reproductions(&mut self, queue: &[usize]) {
        let current_pop = self.agents.len() as i32;
        let density_penalty = (current_pop - 150).max(0) / 5;
        let effective = REPRODUCTION_THRESHOLD + density_penalty;
        for &pidx in queue {
            if !self.agents[pidx].alive { continue; }
            if self.agents[pidx].energy < effective { continue; }
            let (px, py) = (self.agents[pidx].x, self.agents[pidx].y);
            let spawn = find_empty_nearby(&self.world, px, py, 3, &mut self.rng);
            let (cx, cy) = match spawn { Some(p) => p, None => continue };
            let child_genome = mutate_genome(&self.agents[pidx].genome, &mut self.rng);
            // create_child: child energy = REPRODUCTION_COST, parent loses it, gen+1
            self.next_id += 1;
            let cid = self.next_id;
            let cgen = self.agents[pidx].generation + 1;
            self.agents[pidx].energy -= REPRODUCTION_COST;
            let mut child = Agent::new(cid, cx, cy, child_genome);
            child.energy = REPRODUCTION_COST;
            child.generation = cgen;
            // add_agent: place if empty (find_empty already ensured)
            if self.world.grid[cy as usize][cx as usize].occupant.is_none() {
                self.world.grid[cy as usize][cx as usize].occupant = Some(cid);
                self.agents.push(child);
                self.total_reproductions += 1;
                self.agents[pidx].reproduction_cooldown = 20;
            }
        }
    }

    fn cleanup_dead(&mut self) {
        for a in self.agents.iter() {
            if !a.alive {
                let c = &mut self.world.grid[a.y as usize][a.x as usize];
                if c.occupant == Some(a.id) { c.occupant = None; }
            }
        }
        self.agents.retain(|a| a.alive);
    }

    pub fn state_hash(&self) -> u64 {
        let mut h = population_hash(&self.agents);
        // fold in world energy grid so movement/consume divergence is caught
        let mut feed = |v: i32, h: &mut u64| {
            for b in v.to_le_bytes() { *h ^= b as u64; *h = h.wrapping_mul(0x100000001b3); }
        };
        for row in &self.world.grid { for c in row { feed(c.energy, &mut h); } }
        h
    }
}

/// _execute_genome — returns whether the agent requested reproduction.
fn execute_genome(a: &mut Agent, w: &mut World) -> bool {
    // 1. regulate
    let (reg_nonempty, cost_modifier) = ops::regulate_op(a.regulate_op(), a);
    if reg_nonempty {
        let reg_cost = (REGULATE_COSTS[(a.regulate_op() & 7) as usize] + cost_modifier).max(0);
        a.apply_energy_cost(reg_cost);
        if !a.alive { return false; }
    }
    // 2. sense
    let (s0, s1) = a.sense_ops();
    let sv = [ops::sense_op(s0, a, w), ops::sense_op(s1, a, w)];
    // 3. memory
    let mop = a.memory_op();
    let old_len = a.memory.len();
    let sv0 = sv[0];
    ops::memory_op(mop, a, sv0);
    if a.memory.len() != old_len || a.memory.last().map_or(false, |&m| m == sv0) {
        let mem_cost = (MEMORY_COSTS[(mop & 7) as usize] + cost_modifier).max(0);
        a.apply_energy_cost(mem_cost);
        if !a.alive { return false; }
    }
    // 4. process
    let (p0, p1) = a.process_ops();
    let pcodes = [p0, p1];
    let mut fired = [false, false];
    for i in 0..2 {
        let sval = if i < sv.len() { sv[i] } else { 0 };
        if ops::process_op(pcodes[i], sval, a, w) {
            fired[i] = true;
            let pcost = (PROCESS_COSTS[(pcodes[i] & 7) as usize] + cost_modifier).max(0);
            a.apply_energy_cost(pcost);
            if !a.alive { return false; }
        }
    }
    // 5. act
    let (a0, a1) = a.act_ops();
    let acodes = [a0, a1];
    let mut requested_repro = false;
    for i in 0..2 {
        if !fired[i] { continue; }
        let code = acodes[i];
        let (ox, oy, oshield, oenergy) = (a.x, a.y, a.shield_active, a.energy);
        let req = ops::act_op(code, a, w);
        a.record_op_usage(code);
        if req { requested_repro = true; }
        let action_fired = match code & 7 {
            0 => false,
            1 => a.x != ox || a.y != oy,
            2 => a.energy > oenergy,
            3 => a.shield_active && !oshield,
            4 => false, // reproduce: cost handled in reproduction
            5 => a.signaling,
            6 => a.toxin_active,
            _ => a.x != ox || a.y != oy, // flee
        };
        if action_fired {
            let acost = (ACT_COSTS[(code & 7) as usize] + cost_modifier).max(0);
            a.apply_energy_cost(acost);
            if !a.alive { return requested_repro; }
        }
    }
    requested_repro
}

fn mutate_genome(genome: &[u8; 8], rng: &mut PyRandom) -> [u8; 8] {
    let mut g = *genome;
    for i in 0..8 {
        if rng.random() < SLOT_MUTATION_RATES[i] {
            g[i] = rng.randbelow(8) as u8;
        }
    }
    if rng.random() < BYTE_SWAP_RATE {
        let pairs = [(0usize, 1usize), (2, 3), (5, 6)];
        let pair = pairs[rng.randbelow(pairs.len() as u32) as usize];
        g.swap(pair.0, pair.1);
    }
    g
}

fn find_empty_nearby(w: &World, x: i32, y: i32, max_r: i32, rng: &mut PyRandom) -> Option<(i32, i32)> {
    for radius in 1..=max_r {
        let mut candidates: Vec<(i32, i32)> = Vec::new();
        for dx in -radius..=radius {
            for dy in -radius..=radius {
                if dx == 0 && dy == 0 { continue; }
                if dx.abs() == radius || dy.abs() == radius {
                    let (nx, ny) = (x + dx, y + dy);
                    if w.in_bounds(nx, ny) && !w.occupied(nx, ny) {
                        candidates.push((nx, ny));
                    }
                }
            }
        }
        if !candidates.is_empty() {
            return Some(candidates[rng.randbelow(candidates.len() as u32) as usize]);
        }
    }
    None
}
