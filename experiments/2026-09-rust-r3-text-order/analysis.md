# Analysis — Ordered input and Unicode representation

## 1. Observation

Exact API9 requests returned equal responses while mapping evidence, nested evidence, accumulated labels and non-printable Unicode evidence differed in authoritative GameStats text. Three numeric/float controls already matched. Before raw records initial state, all requests, responses and state after each request.

## 2. Competing hypotheses

H1: input order lost before text conversion. H2: representation differs independently of ordering. H3: floating-point exponent spelling necessarily differs. All were checked using public handlers, not standalone string helpers.

## 3. Instrumentation / diagnostic changes

Seven fixed audit cases run against frozen Python time/datetime and native wall metadata; compare complete decoded responses and exported state. First-report raw labels are checked again after accumulation. Production contracts add bootstrap/reset/native export, batch/serial, 1/2/4 configuration coverage and every Unicode printable transition plus neighbors. Lab generator checks the committed table against CPython3.13/Unicode15.1.

## 4. Evidence

H1 supported: all three mapping-text cases differ before, match after preserving serde_json insertion order. Ordinary dict equality alone misses first-report order loss. H2 supported: U+00A0 list text differs without any map involved; both versions return the same numeric score, after matches Python text. H3 not supported by the measured 1e-7 control; both versions match. Extra production numeric text contracts cover large exponent, negative zero, precision and big integers; they do not prove all conversions.

## 5. Root cause

serde_json's default BTreeMap sorted accepted object keys before repr. Existing string_repr escaped only ASCII controls, while Python also escapes non-printable Unicode categories. Recursive repr makes both differences persistent and visible in benchmark metadata.

## 6. Causal chain

Input object order → ordered storage/export/reset → text iteration → evidence/label equality.
Unicode scalar → pinned Python printability lookup → exact escape width → evidence/label/truncation equality.

## 7. Rejected explanations

These are not ignorable JSON key-byte differences: the differing values are strings. The recorded examples do not establish numeric score changes. No evidence attributes the discrepancy to threading, rendering load or Chrome.

## 8. Limits of the evidence

Full regression, 36 Player projections, old six-scene trace replay and new six-scene independent replay pass. This supports the measured functional scope, not full application migration or capacity. No real LLM ranking/old-log impact audit. No Linux, Python3.14, arbitrary Python object or lone-surrogate transport certification. More permissive input conversions remain R001.

## 9. Raw evidence

See results/before, results/after, results/players, results/window and both replay folders; original old trace is cross-referenced in manifest. Source identity, runtime/test equivalence and checksums are explicit.
