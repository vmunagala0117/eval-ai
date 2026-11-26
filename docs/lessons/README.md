# Finance evaluation lessons

Read each companion guide, predict the result, execute its notebook, and inspect the evidence. Markdown explains the business meaning and implementation; notebooks run the experiments; Python modules hold reusable logic.

## Current lessons and intended outcomes

| Lesson | Goal | Expected output | Next question it enables | Status |
|---|---|---|---|---|
| [00 — Success contract](00_success_contract.md) | Separate candidate answers, reference facts, and narrative reviews | Per-check and overall verdicts on authored examples | How are reference facts established? | Implemented offline |
| [01 — Trustworthy reference data](01_reference_data.md) | Derive expected facts from source records | Reconciled totals and a versioned reference with evidence IDs | Can the agent answer against this data? | Implemented offline |
| 02 — Agent and trace | Run an Azure OpenAI finance agent with observable execution | Answer, tool results, trace, run manifest | Which facts and steps are correct? | Planned |
| 03 — Deterministic graders | Check numerical and business requirements | Evidence-linked check verdicts | Did the agent follow a permitted path? | Planned |
| 04 — Trajectory and MCP | Implement real MCP integration and path checks | Required/forbidden action results | Does the conversation handle missing information? | Planned |
| 05 — Multi-turn journeys | Test clarification and follow-ups | Conversation and completion verdicts | Are stateful runs reliable? | Planned |
| 06 — State and isolation | Verify reports, reset, retries, and failures | Actual-state and resource-integrity results | How do we grade narrative meaning? | Planned |
| 07 — Judge calibration | Assess narrow semantic criteria against reviewed labels | Judge verdicts and disagreement analysis | Does a system change improve outcomes? | Planned |
| 08 — Comparisons | Compare versions with repeated trials | Improvements, regressions, uncertainty | Which overhead is worth its cost? | Planned |
| 09 — Efficiency | Measure skill/tool discovery/wait tradeoffs | Quality, token, cost, and time comparisons | How do checks govern releases? | Planned |
| 10 — Release pipeline | Apply full evaluation release rules | Evidence-linked pass/fail/blocked decisions | How does the suite stay relevant? | Planned; starter CI exists |
| 11 — Feedback and drift | Turn reviewed feedback into new cases | Case lineage and drift decisions | Ongoing evaluation maintenance | Planned |

Lessons 00 and 01 each have an executable notebook and companion guide. Add each remaining guide when its lesson is built.

## Standard companion-guide structure

1. Business question and why the requirement matters.
2. Learning objective and current implementation status.
3. Input files, schema fields, ownership, and provenance.
4. Enterprise interpretation versus current demo behavior.
5. Function walkthrough with a concrete example.
6. Expected results, a passing case, and a deliberately failing case.
7. Verification commands and interpretation of output.
8. Known limitations and checks not yet implemented.
9. Learner checkpoint and the next lesson's problem.

## Documentation maintenance

- Use matching names: `notebooks/NN_topic.ipynb` and `docs/lessons/NN_topic.md`.
- Update code, tests, notebook, and companion guide in the same pull request when behavior changes.
- Maintain relative links to actual files; do not copy the entire implementation into prose.
- Keep example results aligned with executable assertions; mark fabricated teaching data as authored.
- Distinguish planned, implemented, executed, and human-reviewed evidence. Never invent SME approval.
- Keep private Codex coaching and personal learning notes outside public lesson guides.
- Use the repository README as the entry point and this page as the lesson index.

[Project README](../../README.md) · [Environment setup](../setup.md) · [Lesson-building workflow](../workflows/build_a_lesson.md)
