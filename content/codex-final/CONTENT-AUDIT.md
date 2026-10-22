# Pattern Decoder codex: content audit (read-only)

Date: 2026-10-22. Scope: `content/playbook-data.json` (`codex_completed`, 310 entries; `compendium`; the `NARROW_BY_FEELING` and `FEELINGS` constants in `content/prose/_raw/playbook.html`), checked against `WRITING-SPEC.md`. No entry file was edited. Metrics come from two throwaway scripts (Flesch-Kincaid with a heuristic syllable counter, which is accurate to about one grade; TF-IDF cosine for overlap). I read 40 entries in full: the 5 open nits, 10 safety-sensitive, 9 risk-flagged and 16 others spread across 18 categories.

The writing itself is strong. Read one at a time, the entries are careful, specific and kind, and the hard rules (no verdicts, real "not this" items, no announcing an exit in safety-sensitive scripts) mostly hold. The biggest problems are in **the structure around the writing**: how readers find entries, how entries link to each other, and how much a distressed person on a phone has to scroll through. The findings are ordered by impact.

---

## 1. Findability: the routes in are mechanical, and half the dangerous entries can't be reached (highest impact)

### 1a. "Narrow it down by feeling" misses 54 of the 105 safety-sensitive entries

The 35 feelings reach 179 of 310 entries. The 131 they never reach include 54 of the 105 `safety_sensitive` entries: **Intimidation, Financial Control, Reproductive Coercion, Smart-Home Coercion, Stalking-by-Notification, Doxxing, Deepfakes, AI Voice Cloning, Pig Butchering, Rage as Control, Forced Dependency, Golden Bars, Device Access Demands, Blackmail / Leverage Exploitation, Health Sabotage, all 9 Cult & Thought Reform entries**, and others. A frightened reader who doesn't know the word "intimidation" has no feeling-route to it.

The lists are built by a keyword-plus-category scorer, and they get padded with whatever sits at the top of a category. The results show it:

| Feeling (what the reader taps) | Entries returned that don't fit it |
|---|---|
| "I feel like I'm missing out if I don't buy, join, or watch this right now" | Sexual Coercion, Interrogation, Extinction Bursts, Response-Time Policing |
| "My family calls it 'just how we are'" | Medical Gaslighting, False Conclusion from Normal Labs, Pressure to Sign, Clinical Tone Policing, Confidentiality as Weapon |
| "My manager is only kind to me in front of other people" | Fabricated Evidence, Trash-Can Diagnosis, Pressure to Sign, Clinical Tone Policing |
| "A stranger online made me feel like they really, deeply know me" | Silent Treatment, "Sacred Duty" Manipulation, Negging |
| "I'm always the one who reaches out first" / "They're only sorry when I threaten to leave" | **Identical lists** (Jaccard 1.0). Five more pairs overlap by 0.8 or more |

Emotional Blackmail shows up under 11 feelings and Minimization under 9, while the high-danger entries listed above show up under none.

**Proposed fixes:**
- Hand-curate the 35 lists instead of scoring them: 6 to 10 entries each, in order of fit. Use the scorer only to suggest candidates.
- Add the feelings that are missing. They line up with the unreachable safety-sensitive entries: "I'm scared of how they'll react," "They control the money," "I think I'm being watched or tracked," "Someone has (or says they have) private photos of me," "I was pressured into sex," "I can't leave this group without losing everyone," "Someone online is asking me for money," "Things in my home act strangely."
- Add a build check that fails if any `safety_sensitive` entry can't be reached from at least one feeling.

### 1b. Category names are leftover internal labels, and several don't match what's inside them

Here are the 24 categories, with counts, plain names and a proposed reader-facing group:

| Category (count) | Problem | Plain name | Reader group |
|---|---|---|---|
| Accountability Evasion (26) | | Dodging blame | 2 |
| Attack & Erosion (20) | | Put-downs and wearing you down | 5 |
| Attachment & Affection Control (18) | | Love and attention as a hook | 4 |
| Control & Domination (18) | holds Isolation itself | Control | 6 |
| Reality Distortion (17) | | Making you doubt what's real | 1 |
| Guilt & Obligation Leverage (17) | | Guilt and "you owe me" | 3 |
| Pressure & Coercion (17) | | Pressure and rushing | 3 |
| Social Warfare & Triangulation (16) | jargon | Turning people against you | 7 |
| Institutional & Process (16) | | Systems and paperwork | 8 |
| **Control structural** (16) | casing, "structural" means nothing to readers | Control (merge) | 6 |
| Digital & AI (13) | duplicates "Digital" | Online, AI and tech | 9 |
| Identity & Conditioning (12) | | Losing yourself | 5 |
| **Confusion / rhetoric** (12) | slash, lower case | Twisting the conversation | 1 |
| **Isolation / social** (12) | **contains no isolation entries** (Information Cascades, Maternal Gatekeeping, Stochastic Harassment...) | Groups and reputation | 7 |
| Deception (11) | | Lies and half-truths | 1 |
| Digital (9) | duplicates "Digital & AI" | Online, AI and tech | 9 |
| **Discard / institutional** (9) | holds Intimate Image Abuse, SIM Swap, Account Takeover, Stalking (Post-Separation), none of them institutional | After a breakup / tech abuse | 6 or 9 |
| Political & Propaganda (9) | | Propaganda | 10 |
| Espionage & Influence Operations (9) | | Spying and influence operations | 10 |
| Cult & Thought Reform (9) | | High-control groups | 10 |
| **Devaluation structural** (8) | "structural"; mixes PIP Weaponization with Dehumanization | Being made to feel less | 5 |
| **Hooking structural** (7) | "structural" | Hooks and traps | 4 |
| **Idealization structural** (5) | holds Social Engineering | Fake fronts | 4 |
| Organizational & Institutional (4) | duplicates "Institutional & Process" | Systems and paperwork | 8 |

Twenty-four categories is too many for a phone menu, and five of them have 8 or fewer entries. **Proposed: 10 reader-facing groups** (8 if groups 1 and 2 are merged), with the 24 kept as internal tags:

1. Making you doubt what's real (40)
2. Dodging blame (26)
3. Pressure, guilt and fear (34)
4. Love and attention as a hook (30)
5. Put-downs and losing yourself (40)
6. Control, watching and money (34, plus the tech-abuse items from "Discard")
7. Groups and reputation (28)
8. Work, school, doctors and official systems (20)
9. Online, AI and tech (22, plus the rest of "Discard")
10. Propaganda, spying and high-control groups (27)

Two entries also need moving: Isolation (from Control & Domination to group 7 or 6), and Intimate Image Abuse and Stalking & Surveillance (out of "Discard / institutional").

### 1c. Tactic names: about 80 of 310 won't mean anything to an 8th grader

Add a plain-words `subtitle` shown under the name and indexed by search. This doesn't touch the entry text. The most important ones:

| Name | Suggested subtitle |
|---|---|
| DARVO | Turning the blame back on you |
| FOG | Fear, guilt and "you owe me" all at once |
| Kafka Trapping | When denying it is taken as proof |
| Sealioning | Polite questions that never stop |
| Gish Gallop | Too many claims to answer |
| Negging | Compliments with a put-down inside |
| Hoovering | Pulling you back after you leave |
| Breadcrumbing | Just enough attention to keep you hoping |
| Triangulation | Using other people's opinions against you |
| Flying Monkeys | People sent to pressure you for someone else |
| Countering | Flatly contradicting your memory |
| Meta-Gaslighting | Told that naming the problem is the problem |
| Thought-Stopping Clichés | Stock phrases that end the conversation |
| Concern Trolling | Fake worry used to undercut you |
| Forced Teaming | A "we" you never agreed to |
| Trash-Can Diagnosis | Throwing a mental-health label at you |
| Relief Bait | Kindness right after the hurt |
| Intermittent Reinforcement | Never knowing if you'll get warmth or coldness |
| Extinction Bursts | It gets worse right after you set a limit |
| Ambient Abuse | A tense atmosphere with no single incident |
| Self-Gaslighting Induction | Doubting yourself automatically |
| Fawning | Pleasing someone because you feel unsafe |
| Parentification | A child made to care for the adult |
| HR Shielding | HR protecting the company, not you |
| Pseudo-Consultation | "Asked" after it was already decided |
| Individualization of Systemic Issues | Blamed for a problem the system caused |
| PIP Weaponization | A performance plan used to push you out |
| Limited Hangout | Admitting a little to hide a lot |
| Stochastic Harassment Direction | Stirring up a crowd against someone |
| Moving-in-Silence | Big decisions made behind your back |
| Negative Reinforcement Traps | The pressure stops only when you give in |
| Double Binds | Wrong whatever you do |
| Foot-in-the-Door / Door-in-the-Face | Small yes first / huge ask first |
| Overton Window Manipulation | Making extreme ideas sound normal |
| Astroturfing | Fake grassroots support |
| Reflexive Control | Shaping what you see so you "choose" their way |
| MICE Framework Exploitation | Money, belief, pressure or ego used to recruit |
| Milieu Control | A group controlling what you see and who you talk to |
| Bounded Choice | "Free" choices with only one real option |
| Sacred Science / Doctrine Over Person | Teachings that can't be questioned / told your experience is wrong |
| Dispensing of Existence | Outsiders treated as lesser or lost |
| Epistemic Coercion via AI | When an AI tool becomes the only voice you trust |
| Context Poisoning | False information planted where people and AI look things up |
| Pig Butchering | Friendship or romance scam that ends in a fake investment (INTERPOL has urged replacing this name, which shames victims, with "romance baiting"; consider adding that as an alias) |
| Paper Terrorism | Buried in legal filings and complaints ("terrorism" reads as alarmist; in the US the term usually means bogus liens and filings) |
| Golden Bars / Velvet Glove Control | A comfortable life with strings attached / control that feels gentle |

Typography: 15 names use slashes to join two names, and 8 use parenthetical tags such as "(CMOs)" and "(Denial & Deception / D&D)". Show the first half as the title and move the rest into the subtitle or alias list.

---

## 2. Link graph: "related tactics" are mostly the neighbours in a list, not real neighbours

- 310 entries and 1,840 links, with no dangling links and no self-links. Every entry has at least 4 related tactics (245 have 6). So the problem isn't missing links. **It's that they were generated.**
- **For 219 of 310 entries (71%), `related_tactics` is exactly the first 5 to 8 other entries in the same category, in file order.** That's why every Accountability Evasion entry links to "DARVO, Blame-Shifting, Whataboutism, Non-Apology Apology, Denial, Minimization."
- 996 of the 1,840 links (54%) go one way only. **153 entries are linked from nowhere**, including Intermittent Reinforcement, Push-Pull, Word Salad, Silent Coalitions, Golden Child Elevation, Catfishing, False Reports and Idealize-Devalue-Discard Cycle. In-degree runs from 43 (Minimization) down to 0.
- Only 143 links cross a category line, so real cross-category neighbours (Gaslighting and Medical Gaslighting, Isolation and Milieu Control) are almost never linked.

**Sample of 20, judged by hand:** 7 close (Normative Messaging, Milieu Control, Kafka Trapping, Blame-Shifting, Deflection, Behavior Control, Name-Calling), 8 loose, and 5 poor:

| Entry | Bad links |
|---|---|
| False Dilemma | Sexual Coercion, Interrogation |
| Ultimatums | Sexual Coercion, Interrogation |
| Moral Framing | Spatial Invasion, Nonverbal Dominance, Resource Sabotage |
| Sabotaging Success | Contempt, Name-Calling, Intimidation |
| Diffusion of Responsibility | Trash-Can Diagnosis, Weaponized Therapy-Speak, Pressure to Sign |

The writers then had to compare entries against these poor neighbours in `how_to_distinguish_from_related`. Paper Terrorism is compared with "Tone policing" and "Signing pressure" when the obvious comparisons are Administrative Escalation and Legal Abuse. Tokenism is compared with "Legal threats" when the obvious comparisons are Performative Allyship and Weaponized Inclusion. Sexual Coercion is compared with Urgency and Interrogation when the obvious comparisons are Reproductive Coercion and Intimate Image Abuse.

Separately, 15 `how_to_distinguish` texts (in 13 entries) treat merged aliases as if they were separate tactics. "Conditional Love" (now Emotional Blackmail) appears 6 times, and "Pseudo-Insight as Shutdown", "Frame Assassination" and "Impossible Metrics" also appear. That breaks the spec's "aliases are not related tactics" rule, and a reader who searches for them lands somewhere unexpected.

**Proposed:**
1. Rebuild `related_tactics` from the names each entry's own `how_to_distinguish_from_related` and `what_it_is_not` actually mention (most entries name 2 or 3 real neighbours), then make every link two-way.
2. Hand-fix the 5 poor cases above.
3. Fail the build on an in-degree of 0.
4. Render alias mentions as "Conditional Love (see Emotional Blackmail)".

---

## 3. Length on a phone: 7 minutes and 24 sections per entry

| Field | Median words | p90 | Max |
|---|---|---|---|
| **Whole entry** | **1,413** | 1,532 | 1,644 (Intimate Image Abuse) |
| response_options (5 parts) | 135 | 154 | 184 |
| what_it_is_not | 97 | 116 | 138 |
| what_it_is | 86 | 102 | 133 |
| expanded_definition | 82 | 92 | 104 |
| what_it_sounds_like | 80 | 108 | 143 |
| this_may_be_it_when | 71 | 82 | 96 |
| discernment_questions | 70 | 79 | 95 |
| this_may_not_be_it_when | 67 | 78 | 98 |
| safety_note / how_to_distinguish | 62 | 72 | 88 |
| plain_language_summary | 26 | 31 | 36 |
| short_definition | 23 | 26 | 30 |

At 200 words a minute, the median entry is a 7-minute read spread over 24 sections. Every entry has about 20 "not this" items and 17 "is it" items. Nobody in distress will scan that on a phone.

**The "read it in 30 seconds" layer** (about 90 words, all from existing fields):
1. **`plain_language_summary` as the lead.** It's the clearest field in the entry (median grade 10.2 against 11.6 for `short_definition`), it's written to "you," and at 26 words it takes about 8 seconds to read.
2. **Three lines from `what_it_sounds_like`**, which have a median grade of 3.3. This is how people recognise their own situation.
3. **Two lines from `this_may_not_be_it_when`** (grade 6.2), so the quick layer still carries the anti-over-reading safeguard.
4. **If `safety_sensitive`:** `safety_note` is always visible above the fold, never collapsed.

Put everything else behind "Read more."

**Duplicate text:**
- `short_definition` and `plain_language_summary` do the same job. Show only the summary. Keep `short_definition` for meta descriptions, search snippets and cards.
- `core_meaning` equals `short_definition` in all 310 entries, and `compendium.what`, `.why`, `.sounds` and `.nots` equal the codex fields in all 310 too. Never render both copies on one page, and consider dropping the duplicate copies from the payload.

---

## 4. Sections that say nearly the same thing

Overall, the wording overlap within an entry is low: the median cosine for any pair of fields is 0.21 or less, against a 0.01 baseline between entries. So the writers did avoid copy-paste. The redundancy is **in what the sections are for**, and at the level of single items:

- **Five "not this" fields:** `what_it_is_not`, `this_may_not_be_it_when`, `innocent_or_ordinary_possibilities`, `common_false_positives` and `less_concerning_if`. Their purposes overlap almost completely. **There are 123 near-duplicate items (cosine above 0.45) in 92 entries.** 61 of them are `this_may_not_be_it_when` against `less_concerning_if`. For example, Sock Puppets has "The accounts have long, varied histories and talk with many other people" in one and "...reply to many unrelated people" in the other. Exaggeration, Device Access Demands and Reverse Psychology show the same thing.
- **"Is it" fields:** `this_may_be_it_when` against `discernment_questions` is the most-overlapping pair in the dataset (0.205), because the questions often restate the signs as questions. `what_it_is` against `expanded_definition` comes next (0.18). There are also 66 near-duplicate "is it" items across 56 entries. For example, Guilt-Tripping's `what_it_is` "Reminders of past sacrifice... unrelated request" matches its `this_may_be_it_when` "The reminder is about something unrelated to the request."

**Proposed page structure (no data rewrite):**

| Reader section | Built from |
|---|---|
| What it is | `plain_language_summary`, then `expanded_definition` (folded). Drop `what_it_is` from the default view; it's the most repetitive of the definition fields |
| What it can sound like | `what_it_sounds_like` |
| Signs it might be this | `this_may_be_it_when` + `more_concerning_if` + `pattern_over_time_signs` (three sub-heads, one block) |
| **When it's probably something else** | `what_it_is_not` + `common_false_positives` ("Look-alikes"), `innocent_or_ordinary_possibilities` ("Ordinary reasons"), `this_may_not_be_it_when` + `less_concerning_if` ("Signs pointing away", removing items with cosine above 0.6) |
| Questions to ask yourself | `discernment_questions` |
| What you can do | `boundary_script` first, then `response_options` |
| Is it changing? | `repair_check` + `boundary_respect_check` |
| Staying safe | `safety_note` (pinned for safety-sensitive entries) |
| Go deeper | `psychological_mechanism`, `possible_impact_on_receiver`, `how_to_distinguish_from_related`, `misuse_warning` |

That's 24 sections down to 9.

---

## 5. Readability: grade 9 to 11 in the fields people read first

Flesch-Kincaid grade for each field (target 8):

| Field | Median | p90 | At grade 10 or above |
|---|---|---|---|
| short_definition | 11.6 | 14.1 | 249 (80%) |
| how_to_distinguish_from_related | 10.8 | 13.3 | 207 (67%) |
| safety_note | 10.4 | 13.2 | 181 (58%) |
| plain_language_summary | 10.2 | 12.6 | 162 (52%) |
| misuse_warning | 9.8 | 12.5 | 136 (44%) |
| psychological_mechanism | 9.5 | 11.5 | 110 |
| why_this_matters | 9.4 | 12.2 | 114 |
| expanded_definition / what_it_is / possible_impact | about 9.1 | about 11.5 | 72 to 100 |
| repair_check | 8.9 | 11.3 | 105 |
| what_it_is_not | 8.9 | 10.2 | 53 |
| response_options | 7.5 | 10.1 | 33 |
| this_may_(not_)be_it_when, more/less_concerning, pattern, questions, boundary_respect | 5.5 to 7.5 | 7 to 9 | 0 to 11 |
| boundary_script | 4.4 | 7.0 | 1 |
| what_it_sounds_like | 3.3 | 7.8 | 5 |

The reason is **sentence length, not vocabulary**. `short_definition` is a single 23-word sentence by design, and `plain_language_summary` packs two ideas into one sentence. **There are 575 sentences of more than 30 words in 253 entries**: 134 in `safety_note`, 105 in `response_options`, 95 in `expanded_definition` and 24 in `plain_language_summary`. The longest runs to 47 words (Self-Gaslighting Induction, `safety_note`). `safety_note` matters most here, because it's the field read under the most stress.

**The 25 worst entry/field pairs (grade):**

| Grade | Entry | Field |
|---|---|---|
| 18.4 | PSYOP Message Framing | short_definition |
| 18.1 | Pressure to Sign | safety_note |
| 17.7 | Phobia Indoctrination | short_definition |
| 17.5 | Public Humiliation | safety_note |
| 17.4 | Agent of Influence Operations | short_definition |
| 17.0 | Group Consolidation | misuse_warning |
| 16.9 | Mystical Manipulation | why_this_matters |
| 16.8 | Revisionist History | why_this_matters |
| 16.8 | Medical Gaslighting | why_this_matters |
| 16.6 | Administrative Escalation | safety_note |
| 16.6 | Anchoring | why_this_matters |
| 16.4 | "Sacred Duty" Manipulation | why_this_matters |
| 16.4 | Honey Trapping | short_definition |
| 16.4 | Overton Window Manipulation | short_definition |
| 16.3 | Stochastic Harassment Direction | short_definition |
| 16.3 | Paper Terrorism | safety_note |
| 16.3 | False Reports | why_this_matters |
| 16.2 | Sabotaging Success | safety_note |
| 16.1 | Setting Up to Fail | safety_note |
| 16.0 | Weaponized Inclusion / Strategic Containment | psychological_mechanism |
| 16.0 | Legal/Administrative Threats | plain_language_summary |
| 15.9 | Social Engineering | short_definition |
| 15.9 | Confidentiality as Weapon | short_definition |
| 15.9 | Synthetic Persona Networks | short_definition |
| 15.8 | Performance Framework Manipulation | short_definition |

Entry-level grade across the top four fields (definition, summary, why, expanded): median 9.4. 106 entries score above 10 and 11 score above 12, the worst being False Reports and Mystical Manipulation at 13.1, then PSYOP, Computational Propaganda and Emotional Parasitism.

**Jargon:** the terms named in the brief are almost never in the top layer. "Epistemic," "reflexive," "triangulation," "coercive control" and "cognitive" appear **0 times** in any `short_definition` or `plain_language_summary`. They live in `how_to_distinguish_from_related`: triangulat- appears 16 of 18 times there, infantiliz- 11 of 13, invalidat- 14 of 17, covert 8 of 11, paternalis- 8 of 9. "Coercive control" appears only in `safety_note` (9 entries) and is never explained. Terms used without explanation where readers will meet them:

| Term | Uses / entries | Where |
|---|---|---|
| ombuds | 40 / 34 | response_options |
| coercive control | 9 / 9 | safety_note |
| compliance | 49 / 34 | mechanism, expanded |
| escalate | 39 / 30 | safety_note |
| leverage | 28 / 20 | distinguish, not-this |

Smaller cases: "online vignette study" (DARVO); the "Harsey, Zurbriggen and Freyd (2017)" citation is accurate but academic in register.

**Proposed:**
- Rewrite `plain_language_summary` as two sentences of 15 words or fewer, for the 61 entries at grade 12 or above first.
- Split every `safety_note` sentence over 30 words (134 of them).
- Add a hover or tap glossary for ombuds, coercive control, legal aid, advocate, escalate and compliance. Then "explain on first use" is handled once, site-wide.

---

## 6. Fresh-eyes read (40 entries): real defects

**Bugs**
- **Sexual Coercion**, `possible_impact_on_receiver`: "going quiet during intimacy, going quiet during intimacy" (the phrase is duplicated).
- **Negging**, `more_concerning_if`: "Your confidence and your wish for their approval have both risen." Confidence should have *dropped*. The same entry's `pattern_over_time_signs` has "You tell a story of their approval as a prize you won last week," which doesn't parse.
- **Intimate Image Abuse**, `response_options.firm_boundary`: "do not send the script to them." This refers to the page's own UI. Change it to "do not send them the wording below."

**Not-this items that aren't real alternatives (rule 2)**
- **Intimate Image Abuse**, `what_it_is_not`: "A claim to hold images when none exist... it is still coercion." That's the same tactic, not an alternative.
- **Dog Whistling**, `what_it_is_not` #2: this is a caveat ("hold especially loosely"), not a look-alike.
- **Sock Puppets**, `what_it_is_not`: "Automated bot accounts... not one person pretending to be many." That's the same deception by other means.

**Inaccurate or misplaced examples**
- **Dog Whistling**: "Nice family you have. It would be a shame if anything happened to the dog" is an open threat (Intimidation already uses the same "Nice life you've got here" line). Replace it with a genuinely double-meaning phrase.
- Its `boundary_script`, "Can we bring a third person in next time we talk about it?", doesn't follow from the line before it.

**Safety: for clinical review**
- **Trauma Bonding**'s script asks for "a counselor or someone we both trust" in the room.
- **Sexual Coercion**'s script proposes picking the conversation up "with someone we both trust."
- Joint or couples counselling is usually advised against where there is abuse. These two scripts should offer a pause or individual support instead.
- **DARVO**'s script opens "What I said hurt you." That concedes fault before the reader's own point is made. Use "I can see you're upset, and I will listen to that."
- **Honey Trapping**, `response_options.workplace`: "Early disclosure is usually treated more gently than late" is an unsupported generalisation. Change it to "Reporting early usually leaves you more options."

**Editorial leakage** (process notes showing on reader pages)
- "This entry..." appears in 21 entries.
- "...so one entry covers both" (Financial Control, Identity Erosion, Public Humiliation, Setting Up to Fail).
- "Two words/names are joined here" (Stalking & Surveillance, SIM Swap).
- The merge formula "the two are the same tactic under different names" is repeated word for word in 6 entries. That's the shared-sentence frame rule 4 forbids. Recast as "Also known as ..." (or render from `absorbs`).

**Word choices**
- Fawning (a self-directed entry) calls the reader "the target."
- "The target" appears in 33 entries.
- "Victim" appears in 18. It fits for fraud and digital entries and is jarring elsewhere.

**Scripts mislabelled as things to say aloud**
- Only 1 of the 44 `societal` entries uses the spec's "Verification script (to yourself...)" prefix. Fawning uses a different one ("Self-support script:"). Reflexive Control, Context Poisoning and others are self-checks that the page currently presents as things to say to another person.
- Fix in the renderer: label `boundary_script` by `branch` ("Say to them," "Ask yourself before sharing," "Say to yourself").

**What held up**
- No verdict labels ("abuser" appears 0 times; "narcissist" appears once, inside a quoted line in Trash-Can Diagnosis).
- The safety-sensitive scripts never announce leaving.
- The risk-flagged entries I read (Doxxing, Deepfakes, Voice Cloning, Pig Butchering, Milieu Control, Reflexive Control, Bounded Choice, Honey Trapping, Epistemic Coercion) stay on recognition and protection.
- Facts checked: 988, StopNCII, Take It Down, Lifton, Freyd's DARVO and the Soviet origin of reflexive control are all correct.
- The "not this" fields are real and specific in about 37 of the 40 entries.

---

## 7. Leftovers and open nits

**British spellings** (about 30 instances): idealised and idealise (Idealize-Devalue-Discard, 4), itemised, disorganisation and disorganised, favourable, reorganises, realisation, personalise, internalised and penalised (The "Good Woman Program"), traumatised, organiser and organisers, neighbourhood and neighbourhoods, colours, characterises, towards (2).

**British vocabulary:**

| British | US |
|---|---|
| flatmate (2) | roommate |
| a lift, meaning a ride (Punishment of Boundaries, Demand for Gratitude, Dog Whistling) | a ride |
| row (Location Tracking, Interrogation, Device Access Demands, Boundary Testing) | fight |
| rota (2) | schedule |
| rang (2) | called |
| diary (3) | calendar |
| flat battery | dead battery |
| pay check | paycheck |
| company flat | company apartment |
| GP, maths, letting agent, pupil, holiday | doctor, math, rental agent, student, vacation |

**Quotes and dashes:**
- The bodies use straight ASCII quotes throughout (per the spec). No curly quotes or em dashes appear.
- The 7 names with quotes ("I Know Best" Paternalism, "We're Family" Erasure, "You're Too Emotional", "Polite Hostile" Environments, "Sacred Duty" Manipulation, The "Good Woman Program", "Managed Out" Through Exhaustion) use straight double quotes. Convert to curly quotes at render time ("I Know Best") and keep the ASCII forms as keys. Search should ignore quote marks.

**Open nits:**

| Entry | Issue | Proposed fix |
|---|---|---|
| Word Salad | `boundary_script` asks for "one sentence: yes or no?" Those are two different requests, and many questions aren't yes or no | "I want to understand, and I've lost the thread. What's the short answer, in one sentence? If you need time to think, that's fine, and we can pick it up tomorrow." |
| Bounded Choice | Sounds-like #6, "...as long as it's the one already shown to you," says the hidden part out loud, which nobody does. `expanded_definition` has "Every environment narrows choices; jobs and mortgages do." | "It's your decision. We just know you'll make the right one." and "Every setting narrows choices; a job or a mortgage does too." |
| Meta-Gaslighting | "That's the real abuse here." and "raising concerns is itself abusive" bring the abuse frame into a non-safety-sensitive entry. The 31-word summary is grade 14 | "That's the real attack here." and "...is itself cruel." Split the summary into two sentences |
| Silent Coalitions | `short_definition` says the group is "quietly agreeing, without any open discussion," which asserts coordination. That contradicts the entry's own `expanded_definition` ("often no explicit agreement"), and rule 1 | "A group leaving one person out through many small, deniable slights, so there is never one clear incident to point to." Also change `what_it_is` "Exclusion that looks coordinated" to "...that can feel coordinated even when nobody planned it" |
| Honey Trapping | The script pairs a refusal with a test ("or can I meet some of your friends this weekend?"), which can tip off an operator. The checking belongs to security, not the reader | "I keep my work separate from my relationships, with everyone, and that won't change. I'm happy to talk about anything else." Leave the meet-friends check in `soft_clarification` |

---

## Fix order

1. Make all 105 safety-sensitive entries reachable by feeling (curate the lists, add the missing feelings, add a build check).
2. Rebuild `related_tactics` from each entry's own text, make the links two-way, and fail the build on orphans.
3. Collapse the page to 9 sections with the 30-second layer.
4. Collapse the 24 categories into 10 groups, rename and fix the misfiled categories, and add name subtitles.
5. Fix the 3 bugs and the 5 open nits, and send the 2 joint-counselling scripts for clinical review.
6. Shorten summaries and safety notes, add a glossary, and do a spelling and vocabulary pass.
