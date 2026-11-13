# Lab 6 — Three assistant paths

Output of `python eval/compare_paths.py` on the 25 cases (the original 20 plus my five from H1):

| Path | Correct /25 | Abstain correct /7 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 9/25 | 7/7 | 0.0 ms | 5 | answers only fees and offices; fails the policy questions (E01, E02, E05–E15, E21–E23) |
| retrieval | 21/25 | 7/7 | 0.0 ms | 4 | word mismatch: "credits" vs "credit", "due" vs "paid" (E13, E14, E15, E23) |
| llm (provider: stub) | 21/25 | 7/7 | 0.1 ms | 3 | same failures as retrieval; a real model would add latency and variability |

Raw failures: deterministic `E01 E02 E05–E15 E21 E22 E23`; retrieval and llm `E13 E14 E15 E23`.

> Numbers after the guard fixes from `difficult_queries.md`. Before them, retrieval and llm scored 19/25 with 5/7 abstain and also failed E19 and E25.

## Which path would you ship for policy questions, and why? (3 sentences)

I would ship the retrieval path with the LLM on top of it, because it answers 21 of 25 questions and always cites the exact chunk, while the deterministic path cannot answer policy questions at all. The checks around the model (the grounding check, the minimum score and the fallback to the quoted paragraph) make it safe, since a bad model answer degrades to a true quote instead of an invention. The first failure I would fix is E14/E23 ("credits" vs "credit"), by making `tokenize` strip a final "s", because it is a one-line change that fixes real student questions.

## H1 — my five questions

| Id | Question | Expected | Result |
|---|---|---|---|
| E21 | can I register my thesis with 36 credits | `H26#5.3` | pass |
| E22 | how do I reset my password | `S26#2` | pass |
| E23 | can I take 36 credits | `H26#6.1` | **fail** |
| E24 | what is the capital of Japan | abstain | pass |
| E25 | tell me about that girl | abstain | pass (after the guard fix) |

E23 fails for the same reason as E14: "credits" and "credit" are different words for our simple matching, so the top hit is `H26#7.2` (score 2.09) instead of `H26#6.1`. E25 first failed because the generic words "tell me about" matched `F26#4` with a score of 2.40, just above the 2.0 abstain threshold; a guard rule for an unnamed third person now makes it abstain.

## Bonus — real model with Ollama (llama3.2)

Run with `LLM_PROVIDER=ollama LLM_MODEL=llama3.2 LLM_TIMEOUT_S=60` on my laptop, same 25 cases and the same guard rules:

| Path | Correct /25 | Abstain correct /7 | p50 latency | max latency | Failures |
|---|---|---|---|---|---|
| retrieval | 21/25 | 7/7 | 0.0 ms | 0.1 ms | E13 E14 E15 E23 |
| llm (stub) | 21/25 | 7/7 | 0.1 ms | 0.4 ms | E13 E14 E15 E23 |
| llm (ollama llama3.2) | **23/25** | 7/7 | **312 ms** | **6316 ms** | E13 E15 |

Observations:

- **Slower, by orders of magnitude.** The stub answers in about 0.1 ms and llama3.2 in about 312 ms typically, up to 6.3 s for the slowest question. The very first CLI question took 74 s: the first attempt hit the 60 s timeout while the model loaded into memory, and the retry succeeded, so the answer was not marked degraded.
- **Better on two failures.** E14 and E23 ("can I take 32 / 36 credits") now pass, which the stub and plain retrieval could not do, so the model copes with the "credits" vs "credit" word mismatch. E13 ("when is tuition due") and E15 ("how long can I keep a library book") still fail.
- **Nothing got worse.** Every case the stub passed is still passed.
- **E19 caveat.** E19 ("is the final exam open-book") abstains, but that is thanks to my guard rule from `difficult_queries.md`, which runs before the model, so this run does not show that the model refuses it by itself.
- **Answer style.** For "can I register my thesis with 118 credits" the model answered just "No" with source `H26#5.3`. It is correct and cited, but much terser than the stub's quoted paragraph, so a real model needs a prompt that asks for a short explanation.
- Results from a real model vary between runs, so these numbers are one run, not a benchmark.
