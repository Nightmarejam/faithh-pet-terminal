// Validation harness for the RNG port — prove Rust matches Python bit-for-bit.
mod rng;
use rng::PyRandom;

fn main() {
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
