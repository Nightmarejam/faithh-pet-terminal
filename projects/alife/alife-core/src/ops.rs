// The 40 ops — verbatim port of ops.py, exp0 (no-wave) paths. All deterministic.
use crate::agent::{Agent, CONSUME_AMOUNT, CRITICAL_LOW_ENERGY, BURST_THRESHOLD,
                   REPRODUCTION_THRESHOLD};
use crate::world::World;

const SIGNAL_ACTIVE: bool = false; // base sim (exp0); set true only in exp5
const TOXIN_ACTIVE: bool = false;

// ---- SENSE (agent, world) -> i32 ----
pub fn sense_op(code: u8, a: &Agent, w: &World) -> i32 {
    match code & 0x07 {
        0 => w.energy_at(a.x, a.y),
        1 => w.threat_at(a.x, a.y), // exp0: no waves -> cell threat (0)
        2 => w.light_at(a.x, a.y),
        3 => { // neighbor: avg of 8-adjacent cell energy (// count)
            let (mut total, mut count) = (0, 0);
            for dx in -1..=1 { for dy in -1..=1 {
                if dx == 0 && dy == 0 { continue; }
                let (nx, ny) = (a.x + dx, a.y + dy);
                if w.in_bounds(nx, ny) { total += w.energy_at(nx, ny); count += 1; }
            }}
            if count > 0 { total / count } else { 0 }
        }
        4 => { // density: 3x3 (INCLUDING center) occupied count * 28, cap 255
            let mut count = 0;
            for dx in -1..=1 { for dy in -1..=1 {
                let (nx, ny) = (a.x + dx, a.y + dy);
                if w.in_bounds(nx, ny) && w.occupied(nx, ny) { count += 1; }
            }}
            (count * 28).min(255)
        }
        5 => a.energy.min(255),
        6 => { // gradient: dir*32 of best adjacent energy, 255 if flat
            let mut best_dir = 255;
            let mut best_e = w.energy_at(a.x, a.y);
            let dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)];
            for (i, &(dx, dy)) in dirs.iter().enumerate() {
                let (nx, ny) = (a.x + dx, a.y + dy);
                if w.in_bounds(nx, ny) {
                    let e = w.energy_at(nx, ny);
                    if e > best_e { best_e = e; best_dir = (i as i32) * 32; }
                }
            }
            best_dir
        }
        _ => a.age.min(255), // 7
    }
}

// ---- PROCESS (sense_value, agent, world) -> bool ----
pub fn process_op(code: u8, sv: i32, a: &Agent, _w: &World) -> bool {
    match code & 0x07 {
        0 => sv > 128,
        1 => sv > a.energy,
        2 => a.memory.last().map_or(false, |&m| sv > m),
        3 => a.memory.len() >= 2 && a.memory[a.memory.len()-1] > a.memory[a.memory.len()-2],
        4 => false, // predict: wave_arrival_times empty in exp0
        5 => sv > 128, // beat: exp0 fallback (no waves) -> sense>128
        6 => { // average
            if a.memory.is_empty() { sv > 128 }
            else { (a.memory.iter().sum::<i32>() as f64 / a.memory.len() as f64) > 128.0 }
        }
        _ => sv < 64, // invert
    }
}

// ---- MEMORY (agent, sense_value) mutates ----
pub fn memory_op(code: u8, a: &mut Agent, sv: i32) {
    match code & 0x07 {
        0 => a.memory.clear(),
        1 => a.memory = vec![sv],
        2 => { a.memory.push(sv); if a.memory.len() > 4 { a.memory.remove(0); } }
        3 => { a.memory.push(sv); if a.memory.len() > 8 { a.memory.remove(0); } }
        4 => if a.memory.is_empty() || sv > a.memory[0] { a.memory = vec![sv]; },
        5 => if a.memory.is_empty() || sv < a.memory[0] { a.memory = vec![sv]; },
        6 | 7 => if sv > 128 { // pattern / dual (same for exp0)
            a.pattern_memory.push((a.age, sv));
            if a.pattern_memory.len() > 4 { a.pattern_memory.remove(0); }
        },
        _ => {}
    }
}

// ---- ACT (agent, world) -> requested_reproduction:bool ----
pub fn act_op(code: u8, a: &mut Agent, w: &mut World) -> bool {
    match code & 0x07 {
        0 => {} // idle
        1 => { // move toward best adjacent energy if empty
            let (mut bx, mut by, mut be) = (a.x, a.y, w.energy_at(a.x, a.y));
            for dx in -1..=1 { for dy in -1..=1 {
                if dx == 0 && dy == 0 { continue; }
                let (nx, ny) = (a.x + dx, a.y + dy);
                if w.in_bounds(nx, ny) && !w.occupied(nx, ny) {
                    let e = w.energy_at(nx, ny);
                    if e > be { be = e; bx = nx; by = ny; }
                }
            }}
            if (bx, by) != (a.x, a.y) {
                if w.move_occupant(a.id, a.x, a.y, bx, by) { a.x = bx; a.y = by; }
            }
        }
        2 => { // consume
            let avail = w.energy_at(a.x, a.y);
            let amt = avail.min(CONSUME_AMOUNT);
            a.add_energy(amt);
            w.reduce_energy(a.x, a.y, amt);
        }
        3 => a.shield_active = true,
        4 => { // reproduce: request if eligible
            return a.reproduction_cooldown == 0 && a.energy >= REPRODUCTION_THRESHOLD;
        }
        5 => if SIGNAL_ACTIVE { a.signaling = true; },
        6 => if TOXIN_ACTIVE { a.toxin_active = true; },
        7 => { // flee: move opposite threat direction
            if let Some((tx, ty)) = w.threat_direction(a.x, a.y) {
                let fx = (a.x - (tx - a.x)).max(0).min(w.width - 1);
                let fy = (a.y - (ty - a.y)).max(0).min(w.height - 1);
                if !w.occupied(fx, fy) {
                    if w.move_occupant(a.id, a.x, a.y, fx, fy) { a.x = fx; a.y = fy; }
                }
            }
        }
        _ => {}
    }
    false
}

// ---- REGULATE (agent) -> (nonempty, cost_modifier) ----
pub fn regulate_op(code: u8, a: &Agent) -> (bool, i32) {
    match code & 0x07 {
        0 => (false, 0),
        1 => if a.energy < CRITICAL_LOW_ENERGY { (true, -1) } else { (false, 0) },
        2 => if a.energy > BURST_THRESHOLD { (true, 0) } else { (false, 0) },
        3 => (true, 0),                 // cycle: always has behavior_mode key
        4 => (true, 0),                 // learn: always has op_discounts key
        5 => if a.energy < CRITICAL_LOW_ENERGY / 2 { (true, 0) } else { (false, 0) },
        6 => (true, 0),                 // prioritize: always nonempty
        _ => (true, if a.energy < CRITICAL_LOW_ENERGY { -1 } else { 0 }), // adaptive
    }
}
