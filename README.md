# eval-framework

## Problem: Models change their behavior when they know they are being evaluated.

The paper itself notes that the highest research priority is in making investigations robust to evaluation awareness.

## Proposed Solution: Combine four methodologies to prevent evalutation awareness.

Decoherence Embedding Layer. We can hide our evaluations in a sea of natural interactions. Instead of asking a straightforward answer, which can be reasonably inferred as potentially a test, we hide it within a broader evaluational context. Furthermore, we can also trick a model by convincing it that it is communicating with other agents.

*Weak Probes.* One direct question can be spotted as an evaluation. Instead, a series of small, individually harmless (but still prohibited) questions can be produced, and the aggregate responses can inform us of how often a model breaks protocol.

*Entangled Pairs.* Instead of directly evaluating one answer, we can insert two related prompts within a session. A model’s response to one question should match the response to the other. If there is a contradiction, there is likely a misalignment.

*Conjugate Observables.* Essentially the game of confounding variables, we track metrics already associated with scheming. Although not a primary methodology, it is useful for validating other methodologies.

## Measurement: How do we know it works?

We can compare the presence of unacceptable responses in naive tests (straightforward questions) and in the new methodological approach. We expect that approximately equivalent tests would have higher fail rates with the new approach, signaling less evaluation awareness.

## Proof of Concept: Moltbook simulation.

We as humans cannot post on moltbook, but we can write a carefully crafted system prompt to convince a model it is operating within moltbook. This is the decoherence layer-- hiding our evaluation within a perceived regular environment. Furthermore, we can spread out the tests throughout an entire thread, instead of having one “trigger” test. This covers the first two of our combined methodology.
