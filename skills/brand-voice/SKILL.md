---
name: brand-voice
description: Establishes a brand's voice and tone through a structured interview, producing a fixed-schema markdown voice guide.
disable-model-invocation: true
---

# Brand Voice

Establish a brand's voice through a short interview, a candidate pick, and a fixed-schema guide. The four dimensions, the schema, and the linter are a contract — don't skip them.

## Step 1: Discovery interview

Talk conversationally, in the user's own words — free text, not multiple-choice. Ask one question at a time and follow up; don't recite a checklist. Cover, broad to specific:

- What the product does and for whom; the emotional state the audience arrives in versus how you want them to feel.
- 2-3 admired brands and *what specifically* each does well, plus one "absolute no".
- 3-5 adjectives for the voice — for each, the "but not" it must not tip into. Reject any adjective a competitor would equally claim (professional, friendly, innovative) and push for a sharper one.
- Where the brand sits on the four dimensions — **Funny ↔ Serious, Formal ↔ Casual, Respectful ↔ Irreverent, Enthusiastic ↔ Matter-of-fact** — judged from concrete behaviour (real jokes? contractions? a norm they'd publicly challenge? exclamation marks?), not aspiration. Irreverence is toward the subject, never the reader.
- Real copy samples if any (they expose aspiration-versus-reality gaps), and any hard never-say words.

Then run a card sort with the 37 words in `assets/tone_words.md`; the rejects sharpen the never-say list.

**Stop when** you can, without guessing: score all four dimensions with a rationale grounded in what they said, and name 3-5 distinct traits (none a competitor would equally claim), each with a concrete do and don't. Then summarise back and confirm before drafting.

## Step 2: Draft candidate voices

Draft 5-6 distinct candidates. Each: a short label, a one-line personality, and the *same* realistic sample (e.g. a membership welcome message or an error message) rewritten in that voice, so they're directly comparable.

## Step 3: Pick

Show all candidates and ask which is closest. Let the user pick, blend, or reword, and iterate until they recognise it as theirs. If they're torn between two, offer a tighter pair rather than forcing a call.

## Step 4: Write the guide

Fill `assets/voice_doc_template.md`, following its inline rules for each section and keeping the headings, tables, and scale exactly as written. Fold hard never-say items into the voice chart's don'ts.

Ground every score and do/don't in what the user actually said, not invention. The guide states the voice, never the case for choosing it — no "why this voice", no derivation note, no commentary.

Save the guide to `docs/design/brand-voice-guide.md` under the project root, creating the directory if it doesn't exist. Then run `python3 scripts/lint_voice_guide.py <path>` and fix every error before telling the user it's ready.
