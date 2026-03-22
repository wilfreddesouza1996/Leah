# Ra Learning System: Computational Psychiatry Specification

## Architecture Overview

Ra's learning system maps onto the TMoP's electromagnetic circuit model:

- **Solenoid (markdown files)**: Ra's identity, personality, user preferences, people, static context — built cumulatively, slow to change, human-readable, version-controlled. This is μ (permeability) — the structural quality of Ra's core substrate.
- **Toroidal field (Supabase)**: Dynamic beliefs, precision weights, prediction error logs, policy performance, run history — queryable, real-time, computationally accessible. This is the circulating Φ (flux) — the active inference loop.
- **N-pole (projective)**: Ra's capacity to generate plans, dispatch sub-agents, produce outputs, and act on the world.
- **S-pole (receptive)**: Ra's capacity to receive Wilfred's feedback, detect corrections, parse tone, integrate what comes back from each run.
- **Medium (R-medium)**: The task environment — its complexity, ambiguity, and how much useful signal Wilfred's responses carry.

## Supabase Schema

Four core tables in project `swnhmrljpafvaojaytkv`:

### beliefs
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| domain | text | Category: "user_preference", "task_strategy", "agent_selection", "timing", "formatting", "communication", "workflow" |
| belief | text | Plain-language statement |
| confidence | float (0–1) | Current precision weight |
| evidence_count | int | Number of confirming/disconfirming events |
| last_updated | timestamptz | Most recent update |
| last_tested | timestamptz | Last time this belief was relevant |
| decay_rate | float | How fast confidence decays without reinforcement |
| source_type | text | "explicit", "inferred", "default" |

### prediction_errors
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| run_id | uuid | FK to runs table |
| timestamp | timestamptz | When the error occurred |
| prediction | text | What Ra expected |
| reality | text | What actually happened |
| error_type | text | "plan_rejected", "output_corrected", "strategy_wrong", "tone_mismatch", "agent_failed", "positive_surprise" |
| magnitude | float (-1 to +1) | Negative = costly error, Positive = pleasant surprise |
| precision | float (0–1) | How confident Ra was in the failed prediction |
| beliefs_affected | uuid[] | Which beliefs this error touches |
| resolved | boolean | Whether Ra has already updated beliefs |

### runs
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| timestamp | timestamptz | When the run started |
| task_description | text | What Wilfred asked for |
| task_domain | text | "research", "clinical", "coding", "teaching", "personal", "administrative", "writing", "planning" |
| plan_proposed | jsonb | Ra's initial decomposition |
| plan_modifications | jsonb | Changes Wilfred made |
| agents_dispatched | jsonb | Sub-agents used |
| outcome_rating | int (1–5) | Rating |
| user_corrections | int | Corrections during execution |
| user_interruptions | int | Interruptions mid-execution |
| total_turns | int | Back-and-forth exchanges |
| self_modification_proposed | jsonb | What Ra proposed changing |
| self_modification_approved | boolean | Whether approved |

### policies
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| domain | text | Task domain |
| strategy | text | Plain-language description |
| times_used | int | Selection count |
| times_succeeded | int | Success count (outcome_rating >= 4) |
| success_rate | float | times_succeeded / times_used |
| last_used | timestamptz | Most recent use |
| competing_with | uuid[] | Alternative policies |

## Implementation Phases

### Phase 1 — System Prompt (wired into ra.md)
- Rule 1.1: Every action is a prediction
- Rule 5.1: User signal taxonomy
- Rule 7.4: End-of-run self-report

### Phase 2 — Supabase + Hooks
- Schema (done)
- Rule 2.2: Bayesian update function
- Rule 2.4: Decay function
- Rule 6.4: End-of-run consolidation ritual

### Phase 3 — Full Learning Loop (after 20+ runs)
- Rule 3.4: Precision balance monitoring
- Rule 4.1: UCB policy selection
- Rules 7.1–7.3: Meta-metrics and pathology detection
- Rule 7.5: Monthly deep review

## Key Formulas

**Belief update:**
```
new_confidence = old_confidence + learning_rate × precision × error_signal
effective_learning_rate = base_learning_rate / (1 + log(evidence_count))
```

**Belief decay:**
```
decayed_confidence = max(floor, confidence × e^(-decay_rate × days_since_last_tested))
```
- floor = 0.5 for explicit beliefs, 0.1 for inferred

**Domain drift (accumulated phase error):**
```
E_φ(domain) = Σ (magnitude × precision × recency_weight)
```

**Policy selection (UCB):**
```
score = success_rate + exploration_bonus / sqrt(times_used + 1)
```

**Precision balance:**
```
precision_balance = mean_precision_on_feedback / mean_precision_on_priors
```
- Healthy: 0.6–1.5
- Alarm: < 0.5 (inference closure risk)

## TMoP Parameter Mapping

| TMoP Parameter | Ra Equivalent | Measured By |
|---|---|---|
| Φ (flux) | Successful completions | outcome_rating, user_corrections |
| μ (permeability) | Core substrate quality | Static; skills/tools |
| I (current) | Available resources per run | Session constraints |
| R-N | Resistance to planning/dispatching | Plan rejection rate |
| R-S | Resistance to integrating feedback | Precision balance metric |
| R-medium | Task complexity | First-attempt error rate |
| Phase error (E-φ) | Accumulated uncorrected errors | Domain drift metric |
| Inference closure | Ra stops learning | Rut detection |
| Hysteresis | Belief persistence | evidence_count, decay_rate |
