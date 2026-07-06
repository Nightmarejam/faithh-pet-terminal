# Tick-loop port spec — everything needed to finish alife-core
Complete after reading the full tick path (2026-07). This turns the port from "large and
scary" into a mechanical checklist. Nothing here is unknown; it's execution + hash-debug.

## Genome slot mapping (agent.py properties)
`genome[0..8]` = [S0, S1, P0, P1, M0, A0, A1, R0]:
- sense_ops = (genome[0], genome[1]) · process_ops = (genome[2], genome[3])
- memory_op = genome[4] (but MEM_NONE forced if MEMORY_ENABLED false — check config)
- act_ops = (genome[5], genome[6]) · regulate_op = genome[7]
- All op lookups mask `& 0x07`.

## Agent state to add (beyond the ported x,y,genome,energy,generation,alive)
`age:i32`, `memory:Vec<i32>`, `pattern_memory:Vec<(i32,i32)>`, `shield_active:bool`,
`signaling:bool`, `toxin_active:bool`, `op_usage:HashMap<u8,i32>` (insertion order matters
for reg_learn — use an ordered map or a Vec of pairs), `reproduction_cooldown:i32`,
`wave_arrival_times/wave1/wave2:Vec<i32>` (empty in exp0/no-wave), plus a few shield/wave
trackers. Helpers: `apply_energy_cost` (energy-=cost; if <=0 →0,alive=false),
`add_energy` (min(energy+amt, 255)), `tick_age`, `reset_tick_state` (clear
shield/signal/toxin), `record_op_usage`, `create_child` (child energy = REPRODUCTION_COST=80,
generation = parent+1, parent loses REPRODUCTION_COST).

## The 40 ops (all deterministic, no RNG) — port ops.py verbatim
- **SENSE (8):** energy(cell), threat(wave-front proximity; falls back to cell threat=0
  when no waves → exp0 returns 0), light(cell), neighbor(avg 8-adj energy, `// count`),
  density(min(255, occupied_adj*28)), self(min(255,energy)), gradient(dir*32 of best adj
  energy, 255 if flat), age(min(255,age)).
- **PROCESS (8) → bool:** threshold(>128), compare(>energy), memory_cmp(>memory[-1]),
  trend(memory[-1]>memory[-2]), predict(wave-interval float math → False in exp0),
  beat(dual-wave → falls back → False in exp0), average(mean(memory)>128), invert(<64).
- **MEMORY (8):** none(clear), last1/4/8 (rolling), best/worst, pattern(store (age,val)
  if val>128), dual(same as pattern for exp0).
- **ACT (8):** idle, move(to best adj energy if empty), consume(min(cell,25) → add_energy +
  reduce cell), shield(shield_active=true), reproduce(if cooldown==0 & energy>=120 →
  queue), signal(if SIGNAL_ACTIVE), toxin(if TOXIN_ACTIVE), flee(move opposite threat dir).
- **REGULATE (8) → dict:** none, conserve(cost_modifier=-1 if energy<50), burst, cycle,
  learn(op_discounts for count>=100), suppress, prioritize, adaptive(conserve+learn).
  Only `cost_modifier` is actually used downstream in exp0.
- Op costs: from config SENSE/PROCESS/MEMORY/ACT/REGULATE_COSTS arrays (index `&0x07`).

## _execute_genome orchestration (the exact order — get this right)
1. regulate_op → reg_mods; if non-empty, apply `max(0, regulate_cost + cost_modifier)`.
   (return early if dead after any cost.)
2. sense: for each of the 2 sense_ops → value; collect sense_values.
3. memory: mem_op(agent, sense_values[0]); apply memory cost IF (memory changed OR
   memory[-1]==sense_values[0]).  ← the subtle cost condition.
4. process: for i in 0,1: if proc_fn(sense_values[i]) → process_fired[i]=true, apply proc cost.
5. act: for i in 0,1: if process_fired[i] → run act_ops[i]; record_op_usage; then apply
   act cost ONLY if the action actually fired (per-op rule: move/flee=moved,
   consume=energy up, shield=newly active, reproduce=no op-cost, signal/toxin=flag set,
   idle=never). cost = `max(0, act_cost + cost_modifier)`, ×effectiveness if burst (exp0 no).

## tick() orchestration
advance_tick → total_ticks++ → regenerate_energy (done) → apply_predator_wave (no-op in
exp0) → `agents = shuffle(alive agents)` (shuffle done) → per agent: cooldown--,
reset_tick_state, apply BASELINE_DRAIN(1) [death check], passive_gain=min(cell,5) added &
removed from cell, _execute_genome [death check], tick_age → _process_reproductions →
_cleanup_dead.

## The two RNG spots in the tick (must match exactly)
- **_mutate_genome:** per-slot `random() < rate` (rates [.001,.001,.010,.010,.005,.001,
  .001,.005]) → `randint(0,7)`; then `random() < BYTE_SWAP_RATE` → `random.choice([(0,1),
  (2,3),(5,6)])`. random.choice(seq) = `seq[randbelow(len(seq))]`.
- **_process_reproductions → find_empty_adjacent → find_empty_nearby:** spiral radius 1..3,
  collect candidate empty cells (exact dx,dy order: for dx in -r..=r, for dy in -r..=r,
  only ring cells where |dx|==r or |dy|==r, in_bounds, empty) → `random.choice(candidates)`.
  Density threshold: `effective = 120 + max(0,(pop-150)//5)`; child only if parent energy
  >= effective; on success total_reproductions++, cooldown=20.

## Validation
Add a `run(seed, ticks)` that seeds → World → initialize_population → N× tick, then hash
full state (all agents' x,y,genome,energy,generation,age + world energy grid). Python
reference: `Simulation(experiment=0, seed=42)`, `initialize_population()`, N× `sim.tick()`,
same hash. **Start with ticks=1** (already exercises reproduction+mutation since init
energy 200 ≥ 120), then 10, then 100. On mismatch, binary-search: hash after each stage
(post-shuffle, post-execute, post-reproduce) to find the diverging step.

## Estimated size: ~600 lines Rust. No unknowns remain — it's execution + hash-debug.
