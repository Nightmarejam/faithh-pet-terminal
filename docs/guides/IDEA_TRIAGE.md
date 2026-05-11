# Idea Triage for FAITHH

This guide defines a simple ranking system for deciding when an idea should be acted on immediately versus documented for later.

## Goal

Keep momentum while protecting focus:

- High-value ideas become immediate actions.
- Medium-value ideas are queued.
- Low-value ideas are captured but not allowed to derail current work.

## Scoring model

Use a 0-5 score for each factor:

- `strategic_alignment`
- `urgency`
- `effort_inverse`
- `evidence_strength`
- `energy_match`

Weights are currently:

- alignment: `1.4`
- urgency: `1.1`
- effort inverse: `1.0`
- evidence strength: `1.1`
- energy match: `0.9`

## Buckets

- `NOW` if score >= 18
- `NEXT` if score >= 12 and < 18
- `ARCHIVE` if score < 12

## Create an idea card

1) Create a JSON file that matches `docs/data/idea_priority_schema.json`.
2) Example:

```json
{
  "id": "2026-03-31-runbook-ranking",
  "title": "Add idea ranking into FAITHH workflow",
  "notes": "Decide what is immediate vs document-only",
  "factors": {
    "strategic_alignment": 5,
    "urgency": 4,
    "effort_inverse": 3,
    "evidence_strength": 4,
    "energy_match": 5
  }
}
```

## Score an idea

```bash
cd ~/ai-stack
python3 scripts/score_idea_priority.py --input /path/to/idea.json --format text
```

For machine output:

```bash
python3 scripts/score_idea_priority.py --input /path/to/idea.json --format json
```

## Score the current layout (batch mode)

Use the seeded layout file:

```bash
cd ~/ai-stack
python3 scripts/score_idea_priority.py --input docs/data/current_priority_layout.json --format text
```

Top 3 only:

```bash
python3 scripts/score_idea_priority.py --input docs/data/current_priority_layout.json --format text --top 3
```

## Suggested operating rhythm

- At idea capture time, score once.
- If `NOW`, convert to an explicit task.
- If `NEXT`, add to queue and review daily/weekly.
- If `ARCHIVE`, keep it searchable and revisit during planning.

