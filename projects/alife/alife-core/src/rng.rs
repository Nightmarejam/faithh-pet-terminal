// MT19937 — a bit-exact port of CPython's `random` module.
//
// WHY this exists and why it's first: the ALife sim's determinism rests entirely on the
// random stream. If Rust's RNG differs from Python's by one draw, the two sims diverge
// completely from step 1 and no fossil can ever hash-match. So we don't use Rust's RNG —
// we reproduce Python's Mersenne Twister exactly: same seeding, same draws, same bits.
// Validated against `python3 -c "random.seed(42); random.random()"` etc.

const N: usize = 624;
const M: usize = 397;
const MATRIX_A: u32 = 0x9908b0df;
const UPPER_MASK: u32 = 0x80000000;
const LOWER_MASK: u32 = 0x7fffffff;

pub struct PyRandom {
    mt: [u32; N],
    mti: usize,
}

impl PyRandom {
    /// Matches Python's `random.seed(n)` for a non-negative int seed (n < 2^32).
    pub fn seed(n: u32) -> Self {
        let mut r = PyRandom { mt: [0; N], mti: N + 1 };
        r.init_by_array(&[n]);
        r
    }

    fn init_genrand(&mut self, s: u32) {
        self.mt[0] = s;
        for i in 1..N {
            let prev = self.mt[i - 1];
            self.mt[i] = (1812433253u32
                .wrapping_mul(prev ^ (prev >> 30)))
                .wrapping_add(i as u32);
        }
        self.mti = N;
    }

    fn init_by_array(&mut self, key: &[u32]) {
        self.init_genrand(19650218);
        let mut i = 1usize;
        let mut j = 0usize;
        let mut k = if N > key.len() { N } else { key.len() };
        while k > 0 {
            let prev = self.mt[i - 1];
            self.mt[i] = (self.mt[i] ^ (prev ^ (prev >> 30)).wrapping_mul(1664525))
                .wrapping_add(key[j])
                .wrapping_add(j as u32);
            i += 1; j += 1;
            if i >= N { self.mt[0] = self.mt[N - 1]; i = 1; }
            if j >= key.len() { j = 0; }
            k -= 1;
        }
        k = N - 1;
        while k > 0 {
            let prev = self.mt[i - 1];
            self.mt[i] = (self.mt[i] ^ (prev ^ (prev >> 30)).wrapping_mul(1566083941))
                .wrapping_sub(i as u32);
            i += 1;
            if i >= N { self.mt[0] = self.mt[N - 1]; i = 1; }
            k -= 1;
        }
        self.mt[0] = 0x80000000;
    }

    /// One 32-bit output — the core generator with the twist + tempering.
    pub fn genrand_uint32(&mut self) -> u32 {
        if self.mti >= N {
            for kk in 0..N - M {
                let y = (self.mt[kk] & UPPER_MASK) | (self.mt[kk + 1] & LOWER_MASK);
                self.mt[kk] = self.mt[kk + M] ^ (y >> 1) ^ if y & 1 != 0 { MATRIX_A } else { 0 };
            }
            for kk in N - M..N - 1 {
                let y = (self.mt[kk] & UPPER_MASK) | (self.mt[kk + 1] & LOWER_MASK);
                self.mt[kk] = self.mt[kk + M - N] ^ (y >> 1) ^ if y & 1 != 0 { MATRIX_A } else { 0 };
            }
            let y = (self.mt[N - 1] & UPPER_MASK) | (self.mt[0] & LOWER_MASK);
            self.mt[N - 1] = self.mt[M - 1] ^ (y >> 1) ^ if y & 1 != 0 { MATRIX_A } else { 0 };
            self.mti = 0;
        }
        let mut y = self.mt[self.mti];
        self.mti += 1;
        y ^= y >> 11;
        y ^= (y << 7) & 0x9d2c5680;
        y ^= (y << 15) & 0xefc60000;
        y ^= y >> 18;
        y
    }

    /// Python's `random.random()` — 53-bit float in [0,1). Consumes TWO uint32s.
    pub fn random(&mut self) -> f64 {
        let a = self.genrand_uint32() >> 5; // 27 bits
        let b = self.genrand_uint32() >> 6; // 26 bits
        (a as f64 * 67108864.0 + b as f64) * (1.0 / 9007199254740992.0)
    }

    /// Python's `getrandbits(k)` for k <= 32.
    pub fn getrandbits(&mut self, k: u32) -> u32 {
        self.genrand_uint32() >> (32 - k)
    }

    /// Python's `_randbelow(n)` — rejection sampling on getrandbits. Basis of randrange/randint.
    pub fn randbelow(&mut self, n: u32) -> u32 {
        if n == 0 { return 0; }
        let k = 32 - n.leading_zeros(); // Python uses n.bit_length(), NOT (n-1) — that was the bug
        loop {
            let r = self.getrandbits(k);
            if r < n { return r; }
        }
    }

    /// Python's `randrange(n)` / `randint(0, n-1)`.
    pub fn randrange(&mut self, n: u32) -> u32 {
        self.randbelow(n)
    }

    /// Python 3.11+ `random.shuffle` — Fisher-Yates using randbelow(i+1), in place.
    /// The tick loop shuffles agent execution order every tick; this must match exactly.
    pub fn shuffle<T>(&mut self, x: &mut [T]) {
        let n = x.len();
        if n < 2 { return; }
        for i in (1..n).rev() {
            let j = self.randbelow((i + 1) as u32) as usize;
            x.swap(i, j);
        }
    }
}
