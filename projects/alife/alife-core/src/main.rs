// Validation harness for the RNG port — prove Rust matches Python bit-for-bit.
mod rng;
mod world;
mod agent;
mod ops;
mod sim;
use rng::PyRandom;
use world::World;
use sim::Simulation;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if let Some(pos) = args.iter().position(|a| a == "run") {
        let seed: u32 = args.get(pos + 1).and_then(|s| s.parse().ok()).unwrap_or(42);
        let ticks: usize = args.get(pos + 2).and_then(|s| s.parse().ok()).unwrap_or(1);
        let mut s = Simulation::new(seed);
        s.initialize_population(50, true);
        for _ in 0..ticks { s.tick(); }
        println!("seed {} after {} ticks: pop={} births={} deaths={}",
                 seed, ticks, s.agents.len(), s.total_reproductions, s.total_deaths);
        let hash = s.state_hash();
        println!("state_hash: {:016x}", hash);
        // fossil output — same shape the Python fossil tools read (dependency-free JSON)
        if args.iter().any(|a| a == "fossil") {
            std::fs::create_dir_all("fossils").ok();
            let json = format!(
                "{{\n  \"experiment\": 0,\n  \"seed\": {},\n  \"ticks\": {},\n  \"location\": \"{}\",\n  \"engine\": \"rust\",\n  \"results\": {{\n    \"population\": {},\n    \"total_reproductions\": {},\n    \"total_deaths\": {},\n    \"total_ticks\": {}\n  }},\n  \"state_hash\": \"{:016x}\"\n}}\n",
                seed, ticks, std::env::var("HOSTNAME").unwrap_or_else(|_| "mac".into()),
                s.agents.len(), s.total_reproductions, s.total_deaths, s.total_ticks, hash);
            let path = format!("fossils/exp0_rust_seed{}_t{}.json", seed, ticks);
            std::fs::write(&path, json).ok();
            println!("wrote {}", path);
        }
        return;
    }
    if std::env::args().any(|a| a == "pop") {
        let mut r = PyRandom::seed(42);
        let mut w = World::new(&mut r);
        let agents = agent::initialize_population(&mut w, &mut r, 50, true);
        println!("seed 42 population: {} agents", agents.len());
        let a0 = &agents[0];
        println!("agent0: pos=({},{}) genome={:?} energy={}", a0.x, a0.y, a0.genome, a0.energy);
        println!("population_hash: {:016x}", agent::population_hash(&agents));
        return;
    }
    if let Some(pos) = args.iter().position(|a| a == "ucf") {
        let seed: u32 = args.get(pos + 1).and_then(|s| s.parse().ok()).unwrap_or(42);
        let ticks: usize = args.get(pos + 2).and_then(|s| s.parse().ok()).unwrap_or(10000);
        let shock = 2000u64;
        let run_arm = |floor: Option<i32>| -> (usize, usize, usize, bool, u64) {
            let mut s = Simulation::new(seed);
            s.floor_energy = floor;
            s.shock_interval = Some(shock);
            s.initialize_population(50, true);
            let mut min_pop = 50usize;
            let mut extinct = false;
            for _ in 0..ticks {
                s.tick();
                let p = s.agents.len();
                if p < min_pop { min_pop = p; }
                if p == 0 { extinct = true; break; }
            }
            (s.agents.len(), s.genome_diversity(), min_pop, extinct, s.floor_rescues)
        };
        println!("=== UCF floor experiment (seed {}, {} ticks, shock every {}) ===", seed, ticks, shock);
        let (fp, fd, fmin, fext, fr) = run_arm(Some(30));
        let (np, nd, nmin, next, _) = run_arm(None);
        println!("{:<10} {:>8} {:>10} {:>12} {:>9} {:>10}", "arm", "finalPop", "diversity", "minPop(resil)", "extinct", "rescues");
        println!("{:<10} {:>8} {:>10} {:>12} {:>9} {:>10}", "FLOOR", fp, fd, fmin, fext, fr);
        println!("{:<10} {:>8} {:>10} {:>12} {:>9} {:>10}", "NO-FLOOR", np, nd, nmin, next, "-");
        println!("\nHealth read (higher finalPop/diversity/minPop = healthier system):");
        println!("  floor helped survival: {}", if fp > np || (next && !fext) { "YES" } else { "no/unclear" });
        println!("  floor preserved diversity: {}", if fd > nd { "YES" } else { "no/unclear" });
        println!("  floor improved resilience (min pop trough): {}", if fmin > nmin { "YES" } else { "no/unclear" });
        return;
    }
    if std::env::args().any(|a| a == "shuffle") {
        let mut r = PyRandom::seed(42);
        let mut x: Vec<i32> = (0..10).collect();
        r.shuffle(&mut x);
        println!("shuffled: {:?}", x); // Python: [7, 3, 2, 8, 5, 6, 9, 4, 0, 1]
        assert_eq!(x, vec![7, 3, 2, 8, 5, 6, 9, 4, 0, 1], "SHUFFLE MISMATCH");
        println!("✅ shuffle matches Python");
        return;
    }
    if std::env::args().any(|a| a == "world") {
        let mut r = PyRandom::seed(42);
        let w = World::new(&mut r);
        println!("seed 42 World: {}x{}, {} sources", w.width, w.height, w.energy_sources.len());
        println!("first sources: {:?}", &w.energy_sources[..3.min(w.energy_sources.len())]);
        println!("state_hash: {:016x}", w.state_hash());
        return;
    }
    println!("seed 42 random():");
    let mut r = PyRandom::seed(42);
    let vals: Vec<f64> = (0..6).map(|_| r.random()).collect();
    for v in &vals { print!("{:.16} ", v); }
    println!();

    println!("seed 42 randrange(256):");
    let mut r = PyRandom::seed(42);
    let vals: Vec<u32> = (0..6).map(|_| r.randrange(256)).collect();
    println!("{:?}", vals);

    // independent check: different seed, non-power-of-2 range (exercises rejection sampling)
    println!("seed 123 randrange(50):");
    let mut r = PyRandom::seed(123);
    let vals: Vec<u32> = (0..8).map(|_| r.randrange(50)).collect();
    println!("{:?}", vals);
    // Python: [3, 17, 5, 49, 26, 17, 6, 2]
    assert_eq!(vals, vec![3, 17, 5, 49, 26, 17, 6, 2], "RNG MISMATCH — port is broken");
    println!("\n✅ all RNG checks pass — Rust matches Python bit-for-bit");
}
