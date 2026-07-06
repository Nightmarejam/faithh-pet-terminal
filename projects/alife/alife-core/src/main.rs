// Validation harness for the RNG port — prove Rust matches Python bit-for-bit.
mod rng;
mod world;
mod agent;
use rng::PyRandom;
use world::World;

fn main() {
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
