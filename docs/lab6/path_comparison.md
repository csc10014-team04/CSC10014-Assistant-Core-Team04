# Lab 6 — Three assistant paths

Run `python eval/compare_paths.py` and fill in.

| Path | Correct /20 | Abstain correct /5 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 10/25 |7/7 |0.0 |0.4 | fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E23|
| retrieval |21/25 |6/7 |0.0 |0.1 | fails: E13 E14 E15 E19|
| llm (provider: ____) |21/25 |6/7 |0.2 |0.4 |fails: E13 E14 E15 E19 |

For handbook questions, I would use the retrieval path.
Because it matches the LLM at 16/20 correct, has lower measured latency, and grounds responses in handbook sources. 
I would fix E13 first by making retrieval recognize paraphrases such as “when is tuition due.” That would address a current retrieval miss while preserving traceable answers.
