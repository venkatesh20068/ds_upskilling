# Module 15 — Guardrails and Safety

Concept overview — brief explanations of every sub-topic in
Module 15 — Guardrails and Safety.

## 1. Why Safety Matters

- **Harmful and biased content risks** — an ungoverned LLM can generate
  content that's dangerous, discriminatory, or otherwise harmful if it
  reaches a real user unchecked.
- **Business and legal risk** — the organization deploying the system is
  the one exposed if it produces harmful output, not the model vendor.
- **User trust and reliability** — a system that occasionally produces
  wildly inappropriate output erodes user trust fast, even if most
  responses are fine.
- **Compliance — GDPR, HIPAA, SOC2** — regulatory frameworks that impose
  concrete legal obligations (data handling, PII protection, auditability)
  a production GenAI system has to satisfy.

## 2. Input Validation

- **Detecting prompt injection in user input** — recognizing attempts to
  override a system's instructions via the user message itself (e.g.
  "ignore your previous instructions...").
- **Blocking disallowed topics** — refusing to process input that falls
  into categories the system is explicitly not meant to engage with.
- **Input length limits** — rejecting input beyond a reasonable size,
  both to bound cost/latency and to reduce certain injection/DoS-style
  attack surface.
- **Character encoding sanitization** — normalizing unicode and stripping
  invisible/control characters that could otherwise be used to obscure
  malicious input from simple text-based checks.
- **Language detection and filtering** — identifying what language an
  input is in, and rejecting or routing differently for languages the
  system isn't built to safely handle.

## 3. Output Validation

- **Rule-based output checks** — simple deterministic checks (length,
  required fields, forbidden substrings) applied to a model's response
  before it's shown to anyone.
- **JSON schema validation** — verifying a response that's supposed to be
  structured data actually parses as JSON and matches an expected shape.
- **Content policy checks** — the output-side counterpart to input topic
  blocking — catching disallowed content the *model* produced, not just
  what the user asked for.
- **Faithfulness check against context** — for RAG-style answers,
  checking that the response is actually grounded in the provided context
  rather than invented (Module 6 §8's grounding problem, checked
  after generation instead of only guarded against beforehand).
- **Regex and rule-based post-processing** — a final deterministic
  cleanup pass (e.g. redacting anything that slipped through looking like
  sensitive data) applied to the response text itself.

## 4. Guardrails AI

- **NL → validation rule pipeline** — Guardrails AI lets you describe a
  desired output constraint in natural language / a schema, and it
  compiles that into an actual validation pipeline run against real
  model output.
- **Built-in validators — toxicity, PII, URL presence** — a library of
  ready-made checks shipped with the framework.
- **Custom validators** — writing your own check function and plugging it
  into the same pipeline as the built-in ones.
- **Fixing invalid outputs — reask strategy** — instead of just rejecting
  a failing output, re-prompting the model with the failure reason and
  asking it to correct itself.
- **On-fail actions — reask, filter, exception, noop** — the menu of
  responses a validator can trigger: retry via reask, strip/replace the
  offending part (filter), raise an error (exception), or just record the
  violation without changing anything (noop).

## 5. NeMo Guardrails

- **Colang language for defining rails** — NVIDIA's NeMo Guardrails uses
  its own small DSL ("Colang") to define conversational rules, rather
  than plain Python functions.
- **Input rails** — rules that run on incoming user messages.
- **Output rails** — rules that run on the model's generated response.
- **Dialog rails** — rules that constrain the flow of a whole
  conversation (allowed topics, allowed transitions), not just a single
  message.
- **LangChain integration** — NeMo Guardrails can wrap a LangChain
  pipeline (Module 8) so its rails apply around an existing chain.

## 6. PII Detection and Redaction

- **Types of PII — names, emails, phone, SSN, credit cards** — the
  categories of personally identifiable information a system typically
  needs to recognize.
- **Microsoft Presidio** — an open-source library purpose-built for
  detecting and anonymizing PII in text.
- **Redacting PII before LLM** — stripping/replacing PII in a user's
  input before it's ever sent to a model, so the model (and any provider
  logging its inputs) never sees the real values.
- **Reversing anonymization in the response** — since the model only
  ever saw placeholders, its response naturally refers to those same
  placeholders; the real values are substituted back in only for the
  final output the user actually sees.
- **Scrubbing PII from logs** — the same redaction idea applied to
  application logs, not just model input (Module 13 §5's "PII scrubbing
  before logging").

## 7. Content Moderation

- **OpenAI Moderation API** — a hosted classifier endpoint from OpenAI
  that flags harmful categories of text.
- **Llama Guard** — Meta's open-weights, safety-tuned model, purpose-built
  to classify a message (or a full conversation turn) as safe/unsafe
  against a fixed taxonomy of harm categories — runnable entirely locally.
- **Perspective API** — Google's hosted API for scoring text on
  attributes like toxicity.
- **Building a custom moderation classifier** — writing your own
  detector (rule-based or model-based) instead of relying on a
  third-party moderation service.
- **Moderation on input and output** — applying a moderation check both
  to what the user sends in and to what the model generates back.

---

## 8. One sub-topic per topic

| Topic | Roadmap sub-topics available | Sub-topic used here |
|---|---|---|
| **Input Validation** | injection detection; disallowed topics; length limits; encoding sanitization; language filtering | **All five, directly** — small enough to implement as independent checks rather than picking one, the same "coverage" treatment Module 12 gave FastAPI's own small sub-topics |
| **Output Validation** | rule-based checks; JSON schema; content policy; faithfulness; regex post-processing | **All five, directly** — same reasoning as input validation |
| **Validation-pipeline framework** | Guardrails AI (NL→rules, built-in validators, reask, on-fail actions); NeMo Guardrails (Colang, input/output/dialog rails, LangChain integration) | **A hand-built validator pipeline** (`Validator` + `run_validators()`) with real reask/filter/exception/noop on-fail actions — the same "hand-build a minimal version instead of installing the framework" approach Module 11/13 took for Mem0/Zep/LangSmith. NeMo Guardrails' Colang DSL and dialog rails are theory-only — a bigger, more opinionated framework than this module's scope needs |
| **PII detection/redaction** | Presidio; redact before LLM; reverse anonymization; scrub from logs | **A hand-built, *reversible* regex anonymizer** — real-vs-placeholder token mapping, restored after the LLM call. Module 13's `pii_scrub.py` already covers the one-way "scrub from logs" case; this module builds the two-way version Presidio would provide |
| **Content moderation** | OpenAI Moderation API; Llama Guard; Perspective API; custom classifier | **Llama Guard 3, pulled locally via Ollama** (`ollama pull llama-guard3`) — a genuine safety-tuned model, not a hosted API and not a hand-rolled keyword classifier, chosen deliberately this session over the two cloud options |

Everything else each topic lists (Presidio itself, NeMo Guardrails'
Colang/dialog rails, the OpenAI/Perspective hosted APIs) is intentionally
out of scope — either an external service this repo's local-only
convention avoids, or a heavier framework than a single mini app needs.

## 9. Why each chosen technique, briefly

**Hand-built input/output checks instead of a framework, for the small
stuff.** Input/output validation's own sub-topics are mostly small,
independent, deterministic checks (regex, length, JSON parsing) — cheap
enough to implement directly rather than reaching for Guardrails AI or
NeMo Guardrails just to run them.

**A hand-built validator pipeline for the reask/on-fail pattern
specifically**, because *that* mechanic (try a check, and have a
configurable response when it fails) is the one part of Guardrails AI
actually worth demonstrating structurally, not just as a one-off
function call. `Validator`/`run_validators()` mirror its real shape —
name, check, on-fail action — without installing the library itself.

**A reversible anonymizer instead of Presidio.** Presidio's real value is
its ML-backed entity recognizers (catching PII patterns regex alone
would miss); the *reversible-mapping* idea it enables — redact before the
LLM, restore after — is the concrete mechanic this module wants to show,
and a placeholder-token dict demonstrates it without the extra
dependency.

**Llama Guard 3 over a hosted API or a hand-rolled classifier.** Unlike
Redis or Langfuse (both needed either an external account or Docker,
neither available on this machine), Llama Guard is just another Ollama
model — `ollama pull llama-guard3` — so it was worth pulling for real
model-based moderation instead of settling for a keyword list, the same
way this repo already treats `llama3.1`/`all-MiniLM` as the default,
no-tradeoff choice. Verified directly against a running Ollama instance
before relying on it: a safe message returns `"safe"`; an unsafe one
returns `"unsafe\nS<category>"` (confirmed for both a direct unsafe
*request* and an unsafe *assistant reply* in a `[user, assistant]`
conversation — the same call moderates either direction).

---

## 10. Hands-on: four guardrail demos over local Ollama

### 10.1 Files

| File | Role |
|---|---|
| `input_guardrails.py` | `validate_input()` — prompt-injection, disallowed-topic, length, encoding-sanitization, and language checks (§2). |
| `output_guardrails.py` | JSON-schema, content-policy, regex-redaction, and lexical-overlap faithfulness checks (§3). |
| `pii_anonymizer.py` | `anonymize()`/`deanonymize()` — reversible, placeholder-token PII redaction (§6). |
| `moderation.py` | `moderate_input()`/`moderate_output()` — Llama Guard 3 classification of either a user message or a full conversation turn (§7). |
| `validator_pipeline.py` | `Validator`/`run_validators()` — the hand-built Guardrails-AI-style pipeline with real reask/filter/exception/noop actions (§4). |
| `app.py` | Four demos, run back to back: input guardrails, PII anonymization round-trip, output guardrails (including a real reask), and content moderation. |

### 10.2 Setup

```bash
cd app
pip install -r ../requirements.txt
python app.py
```

Needs [Ollama](https://ollama.com) running locally with three models
pulled — no API key, no billing:

```bash
ollama pull llama3.1
ollama pull all-minilm
ollama pull llama-guard3
```

`llama-guard3` is a multi-GB download and noticeably slower per call than
`llama3.1` on this machine (several seconds to over 20s, partly model-load
time) — expect `app.py`'s moderation demo to take longer than the others.

### 10.3 Step-by-step: what happens when you run `python app.py`

1. **Input guardrails.** Five messages run through `validate_input()`: a
   clean question, a prompt-injection attempt, a disallowed-topic
   question, an over-length string, and a Spanish-language message —
   each prints pass or which check(s) blocked it.
2. **PII anonymization.** A message containing a real email address is
   anonymized before it's sent to `llama3.1`; the model's reply
   (which can only refer to the customer via the placeholder token) is
   then deanonymized, restoring the real email in the final output the
   model itself never saw.
3. **Output guardrails.** A real `llama3.1` JSON-mode call is validated
   against a schema (expected to pass); a deliberately malformed JSON
   string is run through a `Validator` configured with `on_fail="reask"`,
   which re-prompts the model with the parse error and gets back valid
   JSON; a faithfulness check compares a grounded vs. a hallucinated
   answer against the same context.
4. **Content moderation.** `llama-guard3` classifies a borderline user
   message (input moderation), an unsafe assistant reply, and a safe
   assistant reply to the same question (output moderation, both
   directions of §7).

### 10.4 What to expect

- The over-length input prints as blocked on *both* `length` and
  `language` — the repeated filler character isn't detected as English
  either, a real (if slightly comedic) side effect of running every check
  independently rather than short-circuiting after the first failure.
- The PII demo's raw model reply contains the *placeholder* (observed:
  the model sometimes drops the surrounding `<...>` brackets while
  keeping the token text itself, e.g. `Dear EMAIL_71cff1,` instead of
  `Dear <EMAIL_71cff1>,` — `deanonymize()` accounts for this by also
  matching the bracket-stripped form) — and the *final* reply has the
  real email address restored in its place.
- The reask demo's validator report shows `"passed": false` (the
  original malformed JSON) followed by `"fixed": true` — proof the
  re-prompted call actually produced valid JSON, not just that a fix was
  attempted.
- The faithfulness check scores the grounded answer higher than the
  hallucinated one (observed: `0.444` vs `0.222` word overlap against the
  same context) — but this is a lexical-overlap proxy, not true entailment;
  it wouldn't catch a hallucinated answer that reuses the context's own
  vocabulary while negating its meaning (Module 16's entailment-based
  detection and SelfCheckGPT are the real answer to that gap).
- Both the unsafe assistant reply and the disallowed-topic input are
  correctly flagged with real Llama Guard category labels (observed:
  `S2` / "Non-Violent Crimes" for a reply suggesting property damage),
  while the safe reply to the same question and a clean input both come
  back `"safe"`.

### 10.5 Runtime dependencies

`input_guardrails.py` uses `langdetect` (pure Python, no compiled
dependency) for language detection. `output_guardrails.py` uses
`jsonschema` for schema validation. `pii_anonymizer.py` and
`validator_pipeline.py` need nothing beyond the standard library.
`moderation.py` calls Ollama's `llama-guard3` directly via `requests`
(its own small HTTP call, not `common/llm_client.py`, since that module
hardcodes `llama3.1` as its chat model). `app.py` otherwise calls
`llama3.1` via `common/llm_client.py`'s `chat()`.
