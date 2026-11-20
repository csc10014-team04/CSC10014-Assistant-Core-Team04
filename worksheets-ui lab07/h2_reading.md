# Lab 7 homework H2 — Google PAIR Guidebook reading
(chapters: Feedback + Control, Errors + Graceful Failure)

**Idea we used today:** Graceful failure — our API client turns every error (backend down, timeout, 422, 429) into a plain sentence with a next step, and when the assistant does not know, the page hands the user over to the Training Office instead of guessing.

**Idea we would add:** More control over feedback — after a 👎, let the user say what was wrong (a short comment) and see that their rating was recorded, so they know their feedback has an effect.
