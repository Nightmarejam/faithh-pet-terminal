// World — the minimal ecology grid. Ported to match Python's world.py bit-for-bit.
// The determinism-critical part is the RNG consumption order at init (see README spec).

use crate::rng::PyRandom;

// From config.py (verified 2026-07 — the world.py docstring's "160x120" is stale).
pub const GRID_WIDTH: i32 = 480;
pub const GRID_HEIGHT: i32 = 360;
pub const NUM_ENERGY_SOURCES: usize = 20;
pub const ENERGY_SOURCE_RADIUS: i32 = 15;
pub const ENERGY_SOURCE_STRENGTH: i32 = 10;
pub const ENERGY_REGEN_RATE: i32 = 1;
pub const REGEN_INTERVAL: u64 = 5;
pub const ENERGY_MAX: i32 = 255;

pub struct Cell {
    pub energy: i32,
    pub threat: i32,
    pub light: i32,
    pub occupant: Option<u64>,
}

pub struct World {
    pub width: i32,
    pub height: i32,
    pub tick: u64,
    pub grid: Vec<Vec<Cell>>, // grid[y][x]
    pub energy_sources: Vec<(i32, i32)>,
    pub regime: u8, // directional shock: which trait-group the environment currently favors (0/1)
}

impl World {
    /// EXACT port of Python World.__init__. The RNG must already be seeded.
    /// Consumption order (this is the whole point): row-major cells (energy then light),
    /// then energy-source coordinates. One draw out of order = total divergence.
    pub fn new(rng: &mut PyRandom) -> Self {
        let mut grid: Vec<Vec<Cell>> = Vec::with_capacity(GRID_HEIGHT as usize);
        for _y in 0..GRID_HEIGHT {
            let mut row: Vec<Cell> = Vec::with_capacity(GRID_WIDTH as usize);
            for _x in 0..GRID_WIDTH {
                // Python: randint(50,150) then randint(100,200). randint(a,b)=a+randbelow(b-a+1).
                let energy = 50 + rng.randbelow(101) as i32;
                let light = 100 + rng.randbelow(101) as i32;
                row.push(Cell { energy, threat: 0, light, occupant: None });
            }
            grid.push(row);
        }
        let mut energy_sources = Vec::with_capacity(NUM_ENERGY_SOURCES);
        for _ in 0..NUM_ENERGY_SOURCES {
            // Python: randint(0,width-1), randint(0,height-1) = randbelow(width), randbelow(height)
            let x = rng.randbelow(GRID_WIDTH as u32) as i32;
            let y = rng.randbelow(GRID_HEIGHT as u32) as i32;
            energy_sources.push((x, y));
        }
        World { width: GRID_WIDTH, height: GRID_HEIGHT, tick: 0, grid, energy_sources, regime: 0 }
    }

    pub fn in_bounds(&self, x: i32, y: i32) -> bool {
        x >= 0 && x < self.width && y >= 0 && y < self.height
    }
    pub fn energy_at(&self, x: i32, y: i32) -> i32 { self.grid[y as usize][x as usize].energy }
    pub fn light_at(&self, x: i32, y: i32) -> i32 { self.grid[y as usize][x as usize].light }
    pub fn threat_at(&self, x: i32, y: i32) -> i32 { self.grid[y as usize][x as usize].threat }
    pub fn occupied(&self, x: i32, y: i32) -> bool { self.grid[y as usize][x as usize].occupant.is_some() }
    pub fn reduce_energy(&mut self, x: i32, y: i32, amt: i32) {
        let c = &mut self.grid[y as usize][x as usize];
        c.energy = (c.energy - amt).max(0);
    }
    /// Move an agent's occupant marker (agent.x/y updated by caller). Returns true if moved.
    pub fn move_occupant(&mut self, id: u64, ox: i32, oy: i32, nx: i32, ny: i32) -> bool {
        if !self.in_bounds(nx, ny) || self.grid[ny as usize][nx as usize].occupant.is_some() {
            return false;
        }
        self.grid[oy as usize][ox as usize].occupant = None;
        self.grid[ny as usize][nx as usize].occupant = Some(id);
        true
    }
    /// get_threat_direction: cell with max threat in 5x5, returns (tx,ty) or None.
    pub fn threat_direction(&self, x: i32, y: i32) -> Option<(i32, i32)> {
        let mut max_threat = 0;
        let mut pos = None;
        for dx in -2..=2 {
            for dy in -2..=2 {
                let (nx, ny) = (x + dx, y + dy);
                if self.in_bounds(nx, ny) {
                    let t = self.threat_at(nx, ny);
                    if t > max_threat { max_threat = t; pos = Some((nx, ny)); }
                }
            }
        }
        pos
    }

    /// SHOCK: relocate all energy sources to new random cells + famine the grid.
    /// This shifts the spatial fitness landscape — old-optimal genomes must adapt,
    /// so a diverse population (with movement/gradient variants) recovers and a
    /// monoculture may not. The core of the diversity-reserve test.
    pub fn apply_shock(&mut self, rng: &mut PyRandom) {
        self.energy_sources.clear();
        for _ in 0..NUM_ENERGY_SOURCES {
            let x = rng.randbelow(GRID_WIDTH as u32) as i32;
            let y = rng.randbelow(GRID_HEIGHT as u32) as i32;
            self.energy_sources.push((x, y));
        }
        // famine: drop every cell to a low value; agents must migrate to the new sources
        for row in self.grid.iter_mut() {
            for c in row.iter_mut() { c.energy = 20; }
        }
    }

    /// DIRECTIONAL shock: flip which trait-group the environment favors + relocate sources.
    /// Unlike apply_shock (uniform famine → a generalist wins every time), this changes WHICH
    /// trait is optimal, so a previously-disfavored variant can become the winner. This is the
    /// only shock that can actually invoke the diversity reserve. No blanket famine — the point
    /// is the *directional* selection flip, not mass death.
    pub fn apply_directional_shock(&mut self, rng: &mut PyRandom) {
        self.regime ^= 1;
        self.energy_sources.clear();
        for _ in 0..NUM_ENERGY_SOURCES {
            let x = rng.randbelow(GRID_WIDTH as u32) as i32;
            let y = rng.randbelow(GRID_HEIGHT as u32) as i32;
            self.energy_sources.push((x, y));
        }
    }

    fn regen_rate(&self, x: i32, y: i32) -> i32 {
        for &(sx, sy) in &self.energy_sources {
            if (x - sx).abs() + (y - sy).abs() <= ENERGY_SOURCE_RADIUS {
                return ENERGY_SOURCE_STRENGTH;
            }
        }
        ENERGY_REGEN_RATE
    }

    /// Deterministic (no RNG). Regenerates every REGEN_INTERVAL ticks.
    pub fn regenerate_energy(&mut self) {
        if self.tick % REGEN_INTERVAL != 0 {
            return;
        }
        for y in 0..self.height {
            for x in 0..self.width {
                let rate = self.regen_rate(x, y);
                let c = &mut self.grid[y as usize][x as usize];
                c.energy = (c.energy + rate).min(ENERGY_MAX);
            }
        }
    }

    /// FNV-1a 64-bit over the canonical state (energy,light row-major, then sources).
    /// Dependency-free and computed identically in Python — the cross-language check.
    pub fn state_hash(&self) -> u64 {
        let mut h: u64 = 0xcbf29ce484222325;
        let mut feed = |v: i32, h: &mut u64| {
            for b in v.to_le_bytes() {
                *h ^= b as u64;
                *h = h.wrapping_mul(0x100000001b3);
            }
        };
        for row in &self.grid {
            for c in row {
                feed(c.energy, &mut h);
                feed(c.light, &mut h);
            }
        }
        for &(sx, sy) in &self.energy_sources {
            feed(sx, &mut h);
            feed(sy, &mut h);
        }
        h
    }
}
