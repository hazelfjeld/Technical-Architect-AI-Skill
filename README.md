# Technical Architect AI Skill

An installable skill for designing, reviewing, and evolving software systems. It turns architectural reasoning into explicit constraints, alternatives, decisions, failure analysis, and implementation work.

**Start here: [technical-architect/SKILL.md](technical-architect/SKILL.md).**

## Book foundation and coverage

This project records the actual reading scope for each requested book:

| Book | Edition | Material actually available to this build |
|---|---|---|
| [Head First Software Architecture](https://www.oreilly.com/library/view/head-first-software/9781098134341/) | First, 2024 | Publisher contents/previews and an authorized Chapter 1 excerpt |
| [Head First Design Patterns](https://www.oreilly.com/library/view/head-first-design/9781492077992/) | Second, 2020 | Complete supplied 672-page PDF retrieved; all extracted text reviewed across every chapter and appendix, with 13 selected pages visually checked; official previews and six author-code files also inspected |

**Software Architecture still has partial coverage. Design Patterns now has complete extracted-text coverage, with selective visual inspection.** The supplied PDF titled *Head First Software Development* is a different book and was not substituted for *Head First Software Architecture*. The skill contains original engineering guidance and concise source notes. It does not include book files, copied examples, or a chapter-by-chapter reconstruction. No model training was performed, and the evaluations do not establish general expert-level performance.

See the [source guide](technical-architect/references/sources.md) and [machine-readable source record](technical-architect/references/source-manifest.json) for exact reading boundaries. The [authorized free architecture chapter](https://www.thoughtworks.com/content/dam/thoughtworks/documents/books/head-first-software-architecture_excerpt.pdf) remains on its official host. The [Design Patterns authors' code](https://github.com/bethrobson/Head-First-Design-Patterns) is linked for study and is not vendored.

## What it does

- Inspects a real repository before making claims about its architecture.
- Converts goals into constraints, invariants, and measurable quality scenarios.
- Compares the current/simple baseline with credible alternatives.
- Separates module boundaries, deployment boundaries, and trust boundaries.
- Selects design patterns using concrete change pressure and simpler alternatives.
- Checks whether wrappers, callbacks, shared state, and composed objects preserve their callers' behavioral contracts.
- Analyzes data ownership, partial failure, retries, duplicate effects, and recovery.
- Produces architecture briefs, decision records, review findings, and implementation slices.
- Applies an optional extension to model serving, retrieval, and agent applications.

The pattern decision aid covers 23 conventional patterns and includes concrete probes for notification snapshots, cache access checks, instance lifetime, invocation history, transitions, factory extension, and tree capabilities. The style guide includes layered systems, modular monoliths, plugins, services, events, and complementary structures. These are original operational decision aids.

## Use the skill

Import the complete `technical-architect/` directory using your agent's supported skill workflow. Preserve its `references/`, `assets/`, `agents/`, and `scripts/` directories. The surrounding repository documentation and evaluations are not required at runtime.

Example requests in an agent that supports named skill invocation:

```text
Use $technical-architect to review this repository. Inspect the code first,
prioritize consequential findings, and give me an implementation plan.
```

```text
Use $technical-architect to design a small SaaS for two developers.
Compare feasible options against our six-week deadline and operating budget.
```

```text
Use $technical-architect to refactor this pricing module. Explain which
variation points need a pattern and which can stay simple.
```

The skill works from the available project context. It asks targeted questions only when missing information could change the decision, and labels assumptions rather than inventing facts.

## Included resources

| Path | Purpose |
|---|---|
| `technical-architect/SKILL.md` | Main operating procedure and resource routing |
| `technical-architect/agents/openai.yaml` | Display name and default prompt |
| `technical-architect/references/` | Seven Markdown guides and one JSON source record |
| `technical-architect/assets/` | Four output templates and a hypothetical decision input |
| `technical-architect/scripts/evaluate_options.py` | Strict, dependency-free option comparison |
| `tests/` | Executed unit tests for the comparison utility |
| `evals/` | Behavioral prompts, a synthetic review fixture, and observed responses |
| `VALIDATION.md` | Validation evidence, results, and limitations |

## Compare architecture options

With Python 3.10 or newer, from this repository's root:

```bash
python3 technical-architect/scripts/evaluate_options.py \
  technical-architect/assets/option-matrix.example.json
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

The JSON input requires explicit criteria, weights, constraints, evidence, and assumptions. An option with a failed hard constraint is infeasible; an unknown constraint makes it provisional. Only options passing every declared constraint are ranked. A score cannot override either condition. The tool checks structure and arithmetic, not the truth of the evidence or completeness of the constraints. Read its module documentation for the schema.

## Extend the book grounding

When an authorized copy becomes available, inspect relevant sections, record the edition and exact reading scope, and update the source record. Keep licensed text, private annotations, credentials, and project-sensitive data outside public commits. Recheck the publisher's errata when making a precise claim about the book.

This project is independent of the books' authors and publisher and does not imply their endorsement.
