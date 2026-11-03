# AI text watermarks: what is verified and what isn't

Checked on 2026-11-03. Primary sources are marked **[primary]**. Everything else is a secondary claim, and the weakest ones say so.

## Claude (Anthropic)

- **[primary]** Claude's text watermark is a variant of Google DeepMind's SynthID-Text. At each choice among near-equal next words, a secret key plus the preceding words replaces the usual random draw. Source: [How Claude's text watermarking works](https://www.anthropic.com/news/claude-text-watermark) (published 2026-08-14, updated 2026-09-01).
- **[primary]** It adds no hidden characters: "Nothing is added to the text and there are no hidden characters." Zero-width and U+202F scanners will not find it.
- **[primary]** Only someone holding the key can test for it, and the result is a probability, not a verdict. Anthropic describes a detection API in private preview for eligible organizations.
- **[primary]** It is sparse in code and in factual passages with few acceptable wordings, weak on short text, and unlikely to survive a full rewrite. Light editing probably leaves it in place. Claude's own translations are marked.
- **[primary]** Files (.png, .jpg, .svg) get a C2PA content credential in metadata instead.
- **[primary]** It indicates "Claude was likely involved". It cannot show human authorship and cannot detect other models.
- Secondary: [Daring Fireball](https://daringfireball.net/2026/08/anthropics_watermark_text_adulteration_in_claude_is_a_perversion_of_writing) and [Revolgy](https://www.revolgy.com/insights/blog/anthropic-claude-watermark-ai-text-detection) repeat Anthropic's description. Their extra claims (survives copy-paste, applies above roughly 200 tokens) are not checked here.

**What this means for `slop_scan.py`:** it cannot detect or remove this watermark. Nothing in this repo claims to.

## ChatGPT (OpenAI)

- Third-party blogs report invisible characters in some ChatGPT output, mainly U+202F (narrow no-break space), U+200B and unusual whitespace. These pages are mostly vendors of "watermark remover" tools and cite no primary source or date.
- The same pages say OpenAI denies adding a deliberate watermark and puts the characters down to training side effects. This also comes from a vendor blog and is unverified here.
- One scanner project that documents these characters says plainly that copy-paste and rendering add narrow no-break spaces and non-breaking spaces too, so they are not a reliable AI signal. See [ksanyok/watermark-detector](https://github.com/ksanyok/watermark-detector).

**Working rule:** treat a U+202F or U+200B as a formatting hint, never as proof of who wrote the text.

## SynthID-Text (Google DeepMind)

- Statistical word-choice watermark. The reference implementation is [google-deepmind/synthid-text](https://github.com/google-deepmind/synthid-text). It is for research reproduction, not production, and detection depends on the watermark configuration and its keys.

## Unicode tag characters ("ASCII smuggling")

- The tag block is U+E0000 to U+E007F. Most interfaces render nothing, but software can read it. Attackers have used it to hide prompt injections and to evade exact-match filters ([The New Stack](https://thenewstack.io/unicode-ascii-smuggling-ai-pipelines/)).
- Unicode normalization (NFC/NFD) does not remove these characters.
- Stripping the whole block breaks subdivision flag emoji (England, Scotland, Wales), which use tag sequences. `slop_scan.py` keeps those.

## What `slop_scan.py --hidden` covers

| Category | Code points |
|---|---|
| zero-width | U+200B, U+200C, U+200D, U+2060, U+FEFF |
| odd-space | U+00A0, U+1680, U+2000 to U+200A, U+202F, U+205F, U+3000 |
| soft-hyphen | U+00AD |
| bidi-control | U+061C, U+200E, U+200F, U+202A to U+202E, U+2066 to U+2069 |
| invisible-math | U+2061 to U+2064 |
| filler | U+115F, U+1160, U+3164, U+FFA0 |
| line-separator | U+2028, U+2029 |
| tag-char | U+E0000 to U+E007F (hidden ASCII is decoded in the report) |
| variation-selector | U+FE00 to U+FE0F, U+E0100 to U+E01EF |
| control | C0 and C1 controls except tab, newline, carriage return |
| lookalikes | Latin words that contain Cyrillic or Greek letters |

Kept as normal: emoji ZWJ sequences, a variation selector after an emoji, subdivision flag tag sequences, and U+3000 next to CJK text.
