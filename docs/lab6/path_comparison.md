# Lab 6 — Three assistant paths

Run `python eval/compare_paths.py` and fill in.

| Path | Correct /20 | Abstain correct /5 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | | | | | |
| retrieval | | | | | |
| llm (provider: ____) | | | | | |

Which path would you ship for policy questions, and why? (3 sentences)
I would ship the retrieval path because policy answers require strict fidelity to authoritative source text and reliable abstention when a rule is not covered.
Retrieval grounds responses in verified policy documents, minimizing hallucination risk while preserving high controllability (4/5).
It generalizes across natural-language phrasing far better than brittle deterministic rules while keeping p50 latency low enough for production use.