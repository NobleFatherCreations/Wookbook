# Writing spec — Pattern Decoder codex entries

You are writing finished entries for **The Pattern Decoder**, a free reference
that helps ordinary people recognize manipulation and control tactics. Read
this whole file, then read `exemplars.json` in this folder. Those two entries
(Gaslighting, Astroturfing) are the quality bar: match their care, specificity
and plain speech.

Every entry you write replaces an old one whose text was shared scaffolding:
the same few sentences, with the tactic's name swapped in, on every entry.
**The whole point of this job is that nothing you write could be pasted onto a
different tactic.** If a sentence would still be true and useful on another
entry, it is boilerplate. Rewrite it with detail that is only true of this one.

## Who reads this

Someone who is confused or hurt and is trying to name what happened, or a
student, advocate or curious person. They are not a clinician. Write for them.

- **Plain speech.** About an 8th-grade reading level. Short sentences. Explain a
  term the first time it appears. No jargon for its own sake.
- **Warm, direct, honest.** Talk to "you" where it is natural. Never preachy,
  never alarmist, never clinical-sounding.
- **Describe patterns, not people.** "This pattern can leave you doubting your
  memory" — not "abusers do this".

## The five hard rules

1. **No verdicts.** Never diagnose and never label a person's character
   (no narcissist, sociopath, psychopath, abuser, toxic). Describe what happens
   in an exchange. On everyday interpersonal tactics, never claim to know what
   someone intends; a sentence that mentions intent must be ruling it out
   ("this does not show what anyone meant").
2. **The "not this" fields must be real.** `what_it_is_not`,
   `this_may_not_be_it_when`, `innocent_or_ordinary_possibilities`,
   `common_false_positives` and `less_concerning_if` exist to stop readers
   over-reading. Each item must be an alternative a thoughtful clinician or
   mediator would actually accept, specific to *this* tactic. Never smuggle the
   accusation back in ("it might just be them manipulating you"). Where it is
   true, name the limits of what the reader can know from where they stand.
3. **Risk-flagged entries stay on recognition and protection.** If
   `risk_flagged` is true, the topic could be misused as instructions. Write
   only: what it looks like from the outside, what it costs the people on the
   receiving end, how to check whether it is happening, and how to protect
   yourself. **Never** say how to carry it out: no steps, tools, targeting
   advice, wording to use, or ways to avoid detection. Describing an observable
   sign is fine; describing how to produce it is not.
4. **Nothing shared.** No sentence, and no sentence skeleton with a few words
   swapped, may appear on another entry. Do not open every list the same way.
   Do not reuse stock phrases ("A single instance without repetition...",
   "It fits a repeating pattern..."). If you catch yourself writing a line that
   fits almost any tactic, stop and make it concrete: who, where, what exactly.
5. **True and unembellished.** No invented statistics, studies, quotes
   attributed to real people, laws or case names. Name real frameworks (MICE,
   DARVO, the Overton window...) only when you are sure of them and use them
   accurately. If you are not sure of a fact, leave it out.

## What kind of entry is it?

Decide from the `category`, `branch` and definition, then adapt the fields.

| Kind | Examples | How the fields change |
|---|---|---|
| **Interpersonal** | most of the Detected, Pattern, Watch and Reference entries | quoted lines people actually say; a boundary script you could say aloud |
| **Aftermath / self-directed** | Fawning, Self-Abandonment, Identity Erosion | there may be no second party; write about what the person carries, not what someone else does |
| **Digital** | Doxxing, Deepfakes, Sock Puppets | what it looks like on screens; `what_it_sounds_like` becomes observable signs rather than speech |
| **Institutional / organizational** | Paper Terrorism, Institutional Betrayal | systems, processes, paper trails; response options point to documentation, ombuds, counsel |
| **Societal / political / influence** | Astroturfing, Cognitive Warfare | population scale; the "boundary script" is a verification script you say to yourself before sharing or acting |
| **Cult and thought reform** | Milieu Control, Demand for Purity | judge by whether exit is possible and information is controlled, never by whether a belief is true |

## The fields

All lengths are checked by `design/validate-codex-final.py`. Item counts are
exact where shown.

| Field | Shape | What goes in it |
|---|---|---|
| `short_definition` | 1 sentence, 10–30 words | A complete sentence saying what it is. If the source definition is cut off mid-sentence (`source_definition_is_cut_off`), write the correct one from the expanded text and your own knowledge. |
| `core_meaning` | same text as `short_definition` | Copy it exactly. |
| `expanded_definition` | 40–110 words | What it is, how it shows up, why one instance may mean little, what makes it a pattern. Own words. |
| `plain_language_summary` | 12–45 words | One or two sentences a teenager would follow. No "In plain terms:" prefix. |
| `why_this_matters` | 20–60 words | The cost to the person on the receiving end. If `approved_draft.why_this_matters` exists, start from it; it was clinically reviewed. |
| `what_it_is` | 4–6 items | Concrete facts about the tactic: forms it takes, where it shows up, what sets it apart. Never "falls under category X". |
| `what_it_sounds_like` | 5–8 items | Realistic examples. Quotes for spoken tactics; short observable descriptions for digital, institutional and societal ones. Keep good existing lines; fix any cut-off word. |
| `what_it_is_not` | 5–6 items | Genuine look-alikes and innocent explanations (rule 2). If `approved_draft.what_it_is_not` exists, include it as one item, tightened. |
| `this_may_be_it_when` | exactly 5 | Specific signs that point toward it. |
| `this_may_not_be_it_when` | exactly 5 | Specific signs that point away from it. |
| `innocent_or_ordinary_possibilities` | 3–4 | Ordinary reasons the same thing might happen. |
| `common_false_positives` | 3–4 | Situations people commonly mistake for it. |
| `discernment_questions` | 4–6, each a question | Questions the reader can honestly ask about their own situation. |
| `less_concerning_if` | exactly 3 | |
| `more_concerning_if` | exactly 3 | |
| `pattern_over_time_signs` | exactly 4 | What shows up across weeks or months, not in one moment. |
| `repair_check` | 20–60 words | What real repair would look like for *this* tactic once it is raised, and what only looks like repair. **Do not use a "Real repair... Fake repair..." frame**; describe it in the tactic's own terms, and open each entry differently. |
| `boundary_respect_check` | 20–60 words | How to read the response when you state a boundary about this tactic. **Vary the shape**: sometimes a question to ask yourself, sometimes what to watch for, sometimes a contrast. Do not make every entry "Say '...'. If they..., ... If...". |
| `psychological_mechanism` | 30–85 words | A hedged account of how it can work on a person ("can", "tends to"). The hedging is in the verbs. **Do not add a closing disclaimer** ("this is a possible mechanism, not a claim about intent"); the safeguards page says that once. |
| `possible_impact_on_receiver` | 30–90 words | What people describe, in this tactic's own terms. Hedged; never a prediction or a diagnosis. **Do not close with "effects vary..."** or any other stock line. |
| `response_options` | object with exactly five keys | `soft_clarification`, `firm_boundary`, `disengagement`, `support_seeking`, `workplace_or_professional`; 12–55 words each, tailored to this tactic. For societal or digital entries, adapt: verify, report, step back, take it to a reporter or advocate. |
| `boundary_script` | 15–80 words | Real wording the reader could use (in quotation marks) with **no** fill-in-the-blank brackets, no "X" and "Y". For societal entries, a verification script prefixed "Verification script (to yourself, before sharing):". |
| `safety_sensitive` | true or false | **true** if the tactic can accompany physical danger, stalking, threats, coercive control, financial or legal entrapment, intimate-image abuse, self-harm pressure, danger to children, or loss of housing, income or immigration status. When in doubt for an interpersonal tactic that isolates, monitors, threatens or controls money, choose true. |
| `safety_note` | 25–95 words | Specific to this tactic. If `safety_sensitive` is true: the danger signals to watch for and what kind of help to reach (advocate, legal aid, a trusted person, emergency services if there is immediate danger). If false: say what would change that for this tactic. Never a generic hotline paragraph. |
| `misuse_warning` | 1–2 items | How *this label* tends to get misused (applied too fast, used as a weapon, used to dismiss). Specific. |
| `how_to_distinguish_from_related` | 30–105 words | Name two or three of the entry's related tactics (see `related_tactics`) and give the concrete difference in each case. End on the difference, not on a rule of thumb: **no "If the live question is..." closers.** |

Do **not** write `name`, `tier`, `category`, `related_tactics`, or anything
about what the Decoder tool can detect. Do not write the old universal
sentences ("One example is a signal to examine, not proof of motive...",
"No elevated safety concern is implied..."). One universal safeguards page will
carry those once. Your entries carry only what is true of this tactic.

## Frames to avoid (the checker enforces these)

A sentence can be different word for word and still be the same sentence. Across
55 batches these frames creep in. The validator now rejects any three-word
phrase (with at least two content words) that four or more entries share in the
same field, in the fields that are prone to it. Known frames, do not use:

- "Real repair ... Fake repair ..."
- "This describes a possible mechanism, not a claim about ..."
- "Effects vary with ..."
- "If the live question/point is ..., you are closer to ..."
- "Say '...'. If they ..., ... If ..." as the shape of every boundary check
- "In that case, speak to a trusted person / advocate" as the end of every safety note
  (name the real next step for this tactic instead)

Write each field as if you were the only entry. Facts about quoting real
people: you may name a researcher or framework only when you are certain, and
say no more about their work than you are sure of.

## Using the packet

Each packet entry has `existing_specific_text` (the old text with shared
sentences already removed — a starting point, **not** gospel; it can still carry
stray scaffolding), `approved_draft`, the definitions of related tactics, and
flags. Keep what is good and specific. Replace what is thin. Fix anything wrong.

## Output

Write one JSON file `content/codex-final/<batch-id>.json`, an object keyed by
the exact tactic name, each value holding exactly the fields above. Use plain
ASCII quotes and apostrophes inside the JSON strings (escape quotes properly);
avoid em dashes where a comma or full stop works. Then run:

    python3 design/validate-codex-final.py content/codex-final/<batch-id>.json

Fix every ERROR and run it again until it says all entries pass. `warn` lines
need a look but are not blockers. A passing validator only proves the shape and
the absence of shared sentences. It does not prove the writing is good. Reread
your own entries as the reader would before you report.

Report: the batch id, how many entries passed, anything you were unsure of
(a fact, a clinical judgement, an entry that did not fit its kind), and any
entry you think should be reconsidered.
