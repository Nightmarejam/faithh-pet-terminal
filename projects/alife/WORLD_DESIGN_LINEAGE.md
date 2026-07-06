# World design — the breadcrumb trail, and does it still hold up?
Traced 2026-07 before porting the World to Rust. Question: what thinking went into the
current build, and does it hold? Same method as the concept/doctrine lineages, aimed at
the sandbox's physics.

## The gap worth naming first
You remember starting from **"my sense of how the universe worked"** — wanting something
like the *known universe*. But the design doc (docs/alife_science/TRACK_A_OVERVIEW) says
the actual goal became the **opposite**: *"TempleOS-influenced computational minimalism —
minimal genomes, minimal world rules, maximum emergence."* Somewhere, "encode the
universe" got corrected to "strip the rules to almost nothing and see what life does."

That correction was **right**, and worth understanding: a rich universe-model would
*confound* emergence — you couldn't tell whether complex behavior came from evolution or
from the physics you baked in. Minimal rules **isolate** emergence. So the AI-correction
moved you from a worse sandbox (universe-model) to a better one (minimal ecology). But it
also means the current build **is not, and was never trying to be, a model of the known
universe.** If that aspiration is still alive, it's a *different project* — name it as
such, don't assume the current World is pursuing it.

## What the World actually models (the current build)
A **minimal ecology**, not physics: a 160×120 grid where each cell carries
- **energy** (a resource that regenerates from ~20 sources — food),
- **threat** (predator *waves* that propagate across the grid at finite speed, 30%
  stealth/lethal — selection pressure),
- **light** (a gradient — a spatial signal),
- an occupant.
Plus thermal drain (a slow universal tax). That's it. Resources + threats + a gradient +
entropy-drain. Deliberately spare.

## The stated success criterion (this is the philosophy)
A World experiment "succeeds when it **discovers something surprising** — behavior the
experimenter did not predict from the rules." That's a real complexity-science stance,
and it's coherent with your worldview more than it looks: *complexity from simple rules*
IS a theory of how the universe works — just a different one than "replicate known
physics." Minimalism-generating-emergence is the same TempleOS thread running through your
attestation-fidelity and entropy ideas. It holds together.

## Does it hold up? (tiered honestly)
- **Design philosophy (minimal rules → emergence):** ✅ **holds.** Sound complexity
  science; the correction toward minimalism was correct.
- **As an emergence sandbox:** ✅ **holds.** The listed results *are* surprising
  emergence — carrying capacity ~324, Red Queen shield dominance, self-organized resource
  stripes, anticipation (agents shielding BEFORE detection), harmonic-zone specialization.
  These are the right *kind* of result.
- **As "a model of the known universe":** ❌ **does not hold — by design.** It isn't one
  and shouldn't be judged as one.
- **The specific claimed results ("89.2% predictive shielding", "genuine anticipation
  confirmed"):** ⚠️ **asserted, not confirmed.** Per SANDBOX_REVIEW, results files are
  often empty and there's no reproducibility receipt. These need the seeded-reproducibility
  gate (now built) to graduate from asserted → confirmed.

## What this means for the port (the decision it forces)
Two paths:
1. **Port the current minimal-ecology World as-is** (recommended). It holds up on its own
   terms, and porting it lets you re-run seeded to *confirm* the asserted results. You can
   always evolve the world rules later. Don't rebuild before you've confirmed what the
   current one even does.
2. **Redesign toward the universe-model aspiration** — a different, bigger project, and a
   *worse* emergence sandbox. Tier it **speculative / future**; don't let it block the port.

Recommendation: **port as-is, confirm the results, then decide** whether the
universe-aspiration is worth a separate track. The minimalism is a feature, not a
compromise — resist the urge to make the World "more like the universe" until a seeded
run tells you the current one's results are even real.
